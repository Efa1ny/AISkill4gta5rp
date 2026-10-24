#!/usr/bin/env python3
"""Утилита для юридического и структурного анализа IC/OOC документов и судебных тем на форуме GTA 5 RP.

Выполняет автоматический аудит темы форума:
1. Классифицирует тип документа (Исковое заявление, Юридическая реабилитация, Закон/Кодекс, Обращение в прокуратуру, Ордер/Указ, РП-биография, Форма подачи).
2. Извлекает реквизиты: номер заявления/иска, номер дела (SJ/FJ/DJ), номера ордеров (IA, AS, ASC, RI, SA).
3. Извлекает всех участников, упомянутые Static ID / номера паспортов / жетонов и статьи кодексов (УК, АК, ПК, СК, ТК, ЭК).
4. Проверяет Пост #1 по чек-листу допустимости (наличие ссылок на паспорт, госпошлину, доказательства, проверка на редактирование после ответа судьи и поиск MG / OOC-слов).
5. Строит хронологию движения дела по всем постам темы и проверяет соблюдение сроков (SLA 24ч на принятие, 72ч на расследование, 96ч на рассмотрение).

Примеры запуска:
  python analyze_forum_document.py "https://forum.gta5rp.com/threads/iskovoye-zayavleniye-no248.3418114/"
  python analyze_forum_document.py "https://forum.gta5rp.com/threads/..." --json
  python analyze_forum_document.py --file "./thread_fixture.html"
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import datetime
import importlib.util
import json
from pathlib import Path
import re
import sys

# Подключаем парсер темы из Модуля 1 (gta5rp-forum-navigation)
_NAV_SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "gta5rp-forum-navigation"
    / "scripts"
    / "extract_thread_content.py"
)
_spec = importlib.util.spec_from_file_location("extract_thread_content", _NAV_SCRIPT)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"Не найден базовый скрипт навигации: {_NAV_SCRIPT}")
_nav_mod = importlib.util.module_from_spec(_spec)
sys.modules["extract_thread_content"] = _nav_mod
_spec.loader.exec_module(_nav_mod)

FORUM_ORIGIN = _nav_mod.FORUM_ORIGIN
fetch_url = _nav_mod.fetch_url
parse_thread_html = _nav_mod.parse_thread_html

NUMBER_RE = re.compile(r"(?:№|N|#)\s*(\d+)", re.IGNORECASE)
CASE_CODE_RE = re.compile(
    r"Дело\s*(?:№|N)?\s*([0-9A-Za-zА-Яа-я/_-]+-(?:SJ|FJ|DJ|SC|FC|DC)[0-9A-Za-zА-Яа-я/_-]*)",
    re.IGNORECASE,
)
WARRANT_RE = re.compile(
    r"\b(?:ОРДЕР|ORDER|ордер[ауом]?)\s*(?:№|N)?\s*((?:IA|AS|ASC|RI|SA|FW|ML)[-–—]?\s*[0-9A-Za-zА-Яа-я-]+)"
    r"|\b((?:IA|AS|ASC|RI|SA)-\d+[A-Za-zА-Яа-я0-9-]*)\b",
    re.IGNORECASE,
)
STATIC_OR_PASSPORT_RE = re.compile(
    r"(?:паспорт[ауеом]*|id[- ]?карт[аыеу]|id[- ]?идентификатор[ау]?|жетон[ауом]*|бейдж[ауиком]*|нашивк[аиеу]|static\s*id|статик)\s*"
    r"(?:№|N|#|:|-)?\s*(\d{2,8})\b"
    r"|\[[A-Za-zА-Яа-я0-9 |_-]*#\s*(\d{2,8})\]"
    r"|(?<!Пост\s)#(\d{3,8})\b",
    re.IGNORECASE,
)
ARTICLE_RE = re.compile(
    r"(?:ст(?:ать[яеиюй]+|\.)\s*\d+(?:\.\d+)*(?:\s*(?:,|\sи\s)\s*\d+(?:\.\d+)*)*\s*"
    r"(?:УК|АК|ПК|СК|ТК|ЭК|ДК|ГК|Конституции)(?:\s*СА)?)"
    r"|(?:\b\d{1,2}\.\d{1,2}(?:\.\d{1,2})?\s*(?:УК|АК|ПК|СК|ТК|ЭК|ДК)(?:\s*СА)?)",
    re.IGNORECASE,
)
MG_OOC_WORDS_RE = re.compile(
    r"\b(форум[аеуом]?|админ(?:истратор|а|у|ом|ы)?|откат[ауеы]?|фрапс[ау]?|деморган[аеу]?|"
    r"варн[ауом]?|нон\s*рп|non\s*rp|нрп|статик[ауом]?|static\s*id|дискорд[аеу]?|"
    r"зеленая\s+зона|зелёная\s+зона|байт\s+гос)\b",
    re.IGNORECASE,
)


@dataclass
class ChecklistAudit:
    has_passport_link: bool
    has_fee_link: bool
    has_evidence_or_subpoena: bool
    edited_after_first_reply: bool
    mg_ooc_warnings: list[str]
    notes: list[str]


@dataclass
class TimelineEvent:
    post_number: int
    post_id: int
    author: str
    author_role: str | None
    published_at: str | None
    act_type: str
    summary: str


@dataclass
class SlaMetrics:
    started_at: str | None
    first_official_response_at: str | None
    hours_to_first_response: float | None
    first_response_overdue_24h: bool
    total_hours_elapsed: float | None
    resolution_overdue_96h: bool


@dataclass
class DocumentAnalysisResult:
    source: str
    title: str
    prefix: str | None
    document_type: str
    court_jurisdiction: str | None
    document_number: str | None
    case_codes: list[str]
    warrants: list[str]
    mentioned_ids: list[str]
    mentioned_articles: list[str]
    checklist: ChecklistAudit
    sla: SlaMetrics
    timeline: list[TimelineEvent]


def detect_document_type(title: str, first_post_text: str, breadcrumbs: list[dict[str, str]]) -> tuple[str, str | None]:
    t_low = title.casefold()
    b_low = " ".join(b["title"].casefold() for b in breadcrumbs)
    body_low = first_post_text.casefold()

    jurisdiction = None
    if "верховн" in b_low or "верховн" in body_low or "-sj" in body_low:
        jurisdiction = "Верховный суд (SJ)"
    elif "федеральн" in b_low or "федеральн" in body_low or "-fj" in body_low:
        jurisdiction = "Федеральный суд (FJ)"
    elif "окружн" in b_low or "окружн" in body_low or "-dj" in body_low:
        jurisdiction = "Окружной суд (DJ)"

    if re.search(r"\bформ[аы]\s+подачи\b|\bправила\s+подачи\b", t_low):
        return "template_or_rules (Форма / Правила подачи)", jurisdiction
    if "реабилитац" in t_low or "реабилитац" in b_low or "снятии судимости" in body_low:
        return "rehabilitation (Юридическая реабилитация)", jurisdiction
    if "исковое заявление" in t_low or "иск №" in t_low or "исковое заявление" in body_low:
        return "lawsuit (Исковое заявление)", jurisdiction
    if "прокуратур" in b_low or "в прокуратуру" in body_low or "обращение №" in t_low:
        return "prosecution_complaint (Обращение в Прокуратуру)", jurisdiction
    if any(w in t_low for w in ("кодекс", "конституци", "закон ", "устав ")):
        return "legislation (Нормативно-правовой акт / Закон / Устав)", jurisdiction
    if any(w in t_low for w in ("ордер", "указ", "постановление", "приказ")):
        return "warrant_or_decree (Ордер / Указ / Постановление)", jurisdiction
    if "биографи" in t_low or "биографи" in b_low:
        return "rp_biography (РП-биография)", jurisdiction
    return "general_document (Общий документ / Тема)", jurisdiction


def classify_post_act(post_number: int, text: str, author_role: str | None) -> str:
    low = text.casefold()
    if post_number == 1:
        return "Первичное заявление / Основной документ (Пост #1)"
    if "о принятии искового заявления" in low or "принять к производству" in low:
        if "назначить судебное заседание" in low:
            return "Определение о принятии иска и назначении судебного заседания"
        return "Определение о принятии заявления к производству"
    if "об оставлении" in low and "без движения" in low:
        return "Определение об оставлении заявления без движения"
    if "об отказе в принятии" in low or "отказать в принятии" in low:
        return "Определение об отказе в принятии заявления"
    if "ордер №ia" in low or "ордер ia" in low or "провести расследование в отношении" in low:
        return "Ордер IA (Доступ к расследованию неприкосновенного лица)"
    if "ордер №as" in low or "ордер №asc" in low or "ордер as" in low:
        return "Ордер AS/ASC (На задержание и арест)"
    if "назначить открытое судебное заседание" in low or "назначить закрытое судебное заседание" in low or "о назначении судебного заседания" in low:
        return "Определение о назначении судебного заседания"
    if "заочное решение" in low:
        return "Заочное решение суда (Итоговый вердикт)"
    if "резолютивное решение" in low or "именем штата сан-андреас" in low or ("р е ш и л" in low and "суд" in low):
        return "Решение суда (Итоговый вердикт)"
    if "ходатайств" in low:
        return "Ходатайство стороны"
    if "прокуратур" in low and ("делопроизводств" in low or "уголовное дело" in low or "проверк" in low):
        return "Акт Прокуратуры / Передача делопроизводства"
    if author_role and any(k in author_role.casefold() for k in ("judge", "судья", "председатель")):
        return "Судебное определение / Акт судьи"
    return "Ответ / Сообщение участника"


def summarize_post_text(text: str, max_len: int = 200) -> str:
    cleaned = re.sub(r"> \[ЦИТАТА.*?\n\[/ЦИТАТА\]", "", text, flags=re.DOTALL)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if len(cleaned) <= max_len:
        return cleaned
    return cleaned[: max_len - 3].rstrip() + "..."


def parse_iso_dt(val: str | None) -> datetime | None:
    if not val:
        return None
    try:
        return datetime.fromisoformat(val)
    except ValueError:
        return None


def analyze_thread(thread) -> DocumentAnalysisResult:
    first_post = thread.posts[0] if thread.posts else None
    first_text = first_post.text if first_post else ""

    doc_type, jurisdiction = detect_document_type(thread.title, first_text, thread.breadcrumbs)

    num_match = NUMBER_RE.search(thread.title) or NUMBER_RE.search(first_text[:300])
    doc_number = num_match.group(1) if num_match else None

    all_text = "\n".join(p.text for p in thread.posts)

    case_codes: list[str] = []
    for m in CASE_CODE_RE.finditer(all_text):
        code = m.group(1).strip()
        if code not in case_codes:
            case_codes.append(code)

    warrants: list[str] = []
    for m in WARRANT_RE.finditer(all_text):
        w = (m.group(1) or m.group(2) or "").strip()
        if w and w not in warrants:
            warrants.append(w)

    mentioned_ids: list[str] = []
    for m in STATIC_OR_PASSPORT_RE.finditer(all_text):
        sid = m.group(1) or m.group(2) or m.group(3)
        if sid and sid not in mentioned_ids:
            mentioned_ids.append(sid)

    mentioned_articles: list[str] = []
    for m in ARTICLE_RE.finditer(all_text):
        art = re.sub(r"\s+", " ", m.group(0)).strip()
        if art not in mentioned_articles:
            mentioned_articles.append(art)

    # Аудит Поста #1
    has_passport = False
    has_fee = False
    has_evidence = False
    edited_after_reply = False
    mg_warnings: list[str] = []
    notes: list[str] = []

    if first_post:
        p1_low = first_post.text.casefold()
        has_links = len(first_post.links) > 0 or len(first_post.media) > 0

        if any(k in p1_low for k in ("паспорт", "id-карт", "удостоверен", "ксер")) and has_links:
            has_passport = True
        if any(k in p1_low for k in ("пошлин", "оплат", "квитанц", "чек", "перевод")) and has_links:
            has_fee = True
        if any(
            k in p1_low
            for k in (
                "доказательст",
                "боди-камер",
                "экшн-камер",
                "видеофиксац",
                "запись",
                "истребовать",
                "уголовное дело",
            )
        ):
            has_evidence = True

        # Проверка на MG (OOC-слова) в IC-документах
        if not doc_type.startswith(("rp_biography", "template_or_rules")):
            found_mg = {m.group(1).lower() for m in MG_OOC_WORDS_RE.finditer(first_post.text)}
            mg_warnings = sorted(found_mg)
            if mg_warnings:
                notes.append(
                    f"В Посте #1 обнаружены потенциальные OOC/MG-слова: {', '.join(mg_warnings)}"
                )

        # Проверка редактирования Поста #1 после ответа в теме
        if first_post.last_edited_at and len(thread.posts) > 1:
            edit_dt = parse_iso_dt(first_post.last_edited_at)
            second_dt = parse_iso_dt(thread.posts[1].published_at)
            if edit_dt and second_dt and edit_dt > second_dt:
                edited_after_reply = True
                notes.append(
                    f"ВНИМАНИЕ: Пост #1 редактировался ({first_post.last_edited_at}) ПОСЛЕ публикации Поста #2 ({thread.posts[1].published_at})!"
                )

        if doc_type.startswith("lawsuit"):
            if not has_passport:
                notes.append("Не обнаружена явная ссылка на ксерокопию паспорта истца.")
            if not has_fee:
                notes.append("Не обнаружена явная ссылка на оплату судебной пошлины.")
            if not has_evidence:
                notes.append("Не обнаружены ссылки на доказательства или требование об их истребовании.")

    checklist = ChecklistAudit(
        has_passport_link=has_passport,
        has_fee_link=has_fee,
        has_evidence_or_subpoena=has_evidence,
        edited_after_first_reply=edited_after_reply,
        mg_ooc_warnings=mg_warnings,
        notes=notes,
    )

    # Таймлайн и SLA
    timeline: list[TimelineEvent] = []
    first_official_dt: datetime | None = None
    first_official_str: str | None = None

    for post in thread.posts:
        role_parts = [p for p in [post.user_title, *post.user_banners] if p]
        role_str = ", ".join(role_parts) if role_parts else None
        act_type = classify_post_act(post.post_number, post.text, role_str)
        timeline.append(
            TimelineEvent(
                post_number=post.post_number,
                post_id=post.post_id,
                author=post.author,
                author_role=role_str,
                published_at=post.published_at,
                act_type=act_type,
                summary=summarize_post_text(post.text),
            )
        )
        if post.post_number > 1 and first_official_dt is None and act_type.startswith(("Определение", "Ордер", "Решение", "Заочное")):
            first_official_dt = parse_iso_dt(post.published_at)
            first_official_str = post.published_at

    start_dt = parse_iso_dt(first_post.published_at) if first_post else None
    last_dt = parse_iso_dt(thread.posts[-1].published_at) if thread.posts else None

    hours_to_first: float | None = None
    overdue_24h = False
    if start_dt and first_official_dt:
        hours_to_first = round((first_official_dt - start_dt).total_seconds() / 3600.0, 2)
        overdue_24h = hours_to_first >= 24.0

    total_hours: float | None = None
    overdue_96h = False
    if start_dt and last_dt:
        total_hours = round((last_dt - start_dt).total_seconds() / 3600.0, 2)
        overdue_96h = total_hours >= 96.0

    sla = SlaMetrics(
        started_at=first_post.published_at if first_post else None,
        first_official_response_at=first_official_str,
        hours_to_first_response=hours_to_first,
        first_response_overdue_24h=overdue_24h,
        total_hours_elapsed=total_hours,
        resolution_overdue_96h=overdue_96h,
    )

    return DocumentAnalysisResult(
        source=thread.source,
        title=thread.title,
        prefix=thread.prefix,
        document_type=doc_type,
        court_jurisdiction=jurisdiction,
        document_number=doc_number,
        case_codes=case_codes,
        warrants=warrants,
        mentioned_ids=mentioned_ids,
        mentioned_articles=mentioned_articles,
        checklist=checklist,
        sla=sla,
        timeline=timeline,
    )


def format_markdown(res: DocumentAnalysisResult) -> str:
    lines: list[str] = []
    prefix_str = f"[{res.prefix}] " if res.prefix else ""
    lines.append(f"# Юридический и структурный разбор: {prefix_str}{res.title}")
    lines.append(f"- **Источник**: {res.source}")
    lines.append(f"- **Тип документа**: `{res.document_type}`")
    if res.court_jurisdiction:
        lines.append(f"- **Инстанция / Подсудность**: `{res.court_jurisdiction}`")
    if res.document_number:
        lines.append(f"- **Номер документа / заявления**: `№{res.document_number}`")
    if res.case_codes:
        lines.append(f"- **Номера судебных дел**: {', '.join(f'`{c}`' for c in res.case_codes)}")
    if res.warrants:
        lines.append(f"- **Упомянутые ордера**: {', '.join(f'`{w}`' for w in res.warrants)}")
    if res.mentioned_ids:
        lines.append(
            f"- **Извлеченные Static ID / Паспорта / Жетоны**: {', '.join(f'`#{i}`' for i in res.mentioned_ids)}"
        )
    if res.mentioned_articles:
        lines.append(
            f"- **Упомянутые статьи законов и кодексов**: {', '.join(f'`{a}`' for a in res.mentioned_articles)}"
        )

    lines.append("\n## Чек-лист проверки Поста #1 (Формальные требования)")
    lines.append(
        f"- **Ксерокопия паспорта / ID**: {'✅ Да' if res.checklist.has_passport_link else '❌ Не найдено'}"
    )
    lines.append(
        f"- **Оплата госпошлины**: {'✅ Да' if res.checklist.has_fee_link else '❌ Не найдено'}"
    )
    lines.append(
        f"- **Доказательства / Истребование**: {'✅ Да' if res.checklist.has_evidence_or_subpoena else '❌ Не найдено'}"
    )
    lines.append(
        f"- **Редактирование Поста #1 после ответа**: {'⚠️ ДА (Нарушение!)' if res.checklist.edited_after_first_reply else '✅ Нет'}"
    )
    lines.append(
        f"- **Признаки MG / OOC-лексики**: {', '.join(f'`{w}`' for w in res.checklist.mg_ooc_warnings) if res.checklist.mg_ooc_warnings else '✅ Не обнаружено'}"
    )
    if res.checklist.notes:
        lines.append("\n### Замечания аудитора:")
        for note in res.checklist.notes:
            lines.append(f"- ⚠️ {note}")

    lines.append("\n## Контроль процессуальных сроков (SLA)")
    lines.append(f"- **Дата подачи (#1)**: `{res.sla.started_at or '—'}`")
    lines.append(
        f"- **Первый судебный акт**: `{res.sla.first_official_response_at or '—'}` "
        + (
            f"(`{res.sla.hours_to_first_response} ч.` — {'🔴 Просрочка >24ч' if res.sla.first_response_overdue_24h else '🟢 В пределах 24ч'})"
            if res.sla.hours_to_first_response is not None
            else ""
        )
    )
    if res.sla.total_hours_elapsed is not None:
        lines.append(
            f"- **Длительность между первым и последним постом**: `{res.sla.total_hours_elapsed} ч.` "
            f"({'🟡 Свыше 96ч' if res.sla.resolution_overdue_96h else '🟢 В пределах 96ч'})"
        )

    lines.append(f"\n## Хронология движения дела ({len(res.timeline)} постов)")
    for ev in res.timeline:
        role_note = f" ({ev.author_role})" if ev.author_role else ""
        lines.append(
            f"1. **Пост #{ev.post_number}** [`{ev.published_at or '—'}`] — **{ev.author}**{role_note}: "
            f"**{ev.act_type}**\n   > _{ev.summary}_"
        )

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Юридический и структурный анализатор документов форума GTA 5 RP"
    )
    parser.add_argument("url", nargs="?", help="URL темы форума")
    parser.add_argument("--file", "-f", help="Путь к локальному HTML-файлу темы")
    parser.add_argument("--json", action="store_true", help="Вывести результат в формате JSON")
    args = parser.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    if not args.url and not args.file:
        parser.error("Укажите URL темы или флаг --file <путь_к_html>")

    if args.file:
        path = Path(args.file)
        html = path.read_text(encoding="utf-8")
        source = str(path.resolve())
        base_url = FORUM_ORIGIN
    else:
        html = fetch_url(args.url)
        source = args.url
        base_url = args.url

    thread = parse_thread_html(html, source=source, base_url=base_url)
    analysis = analyze_thread(thread)

    if args.json:
        print(json.dumps(asdict(analysis), ensure_ascii=False, indent=2))
    else:
        print(format_markdown(analysis))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
