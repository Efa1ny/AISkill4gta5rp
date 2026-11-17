#!/usr/bin/env python3
"""Обновление законодательной базы сервера Mirror с форума GTA 5 RP (инструмент мейнтейнера).

Конвейер:
  1. скачать темы раздела 2181 (ID тем берутся из references/laws/laws_index.json);
  2. записать references/laws/<slug>.md (шапка + текст первого поста; у ленты изменений — все посты);
  3. пересобрать laws_index.json (build_laws_index.py);
  4. поднять patch-версию в plugin.json и .claude-plugin/plugin.json (без этого маркетплейс
     Claude Code не увидит обновление);
  5. обновить копии модулей (scripts/sync_copies.py в корне репозитория).
Дальше вручную: просмотреть `git diff`, закоммитить и запушить в main. Пользователи Claude Code
с включённым автообновлением маркетплейса получат базу сами, остальные — переустановкой с GitHub.

Раздел закрыт авторизацией: нужен cookie xf_user (--cookie или переменная окружения GTA5RP_XF_USER).
Если форум отдаёт 403 скрипту, сохрани страницы тем из браузера как thread_<ID>.html и передай --html-dir.
Тема, которая не скачалась или не распарсилась, не трогается (старый файл остаётся).

Примеры:
  python sync_mirror_laws.py --cookie "<id>,<токен>"
  python sync_mirror_laws.py --html-dir ./saved_pages
  python sync_mirror_laws.py --only criminal_code procedure_code
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys

SCRIPTS_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPTS_DIR.parent
LAWS_DIR = BASE_DIR / "references" / "laws"
INDEX_PATH = LAWS_DIR / "laws_index.json"
sys.path.insert(0, str(BASE_DIR.parent / "gta5rp-forum-navigation" / "scripts"))
sys.path.insert(0, str(SCRIPTS_DIR))
import build_laws_index  # noqa: E402
import extract_thread_content as etc  # noqa: E402

CHANGELOG_SLUG = "law_changes_info"
CATEGORY = "Законодательная база штата Сан-Андреас (Сервер Mirror)"
EDITION_RE = re.compile(r"[Рр]едакци[яи] от (\d\d\.\d\d\.\d{4})")
MIN_TEXT_LEN = 300  # короче — почти наверняка страница входа или ошибка, а не закон


def fetch_posts(thread_id: int, cookie: str, html_dir: Path | None, all_pages: bool) -> tuple[str, list]:
    url = f"{etc.FORUM_ORIGIN}/threads/{thread_id}/"
    if html_dir:
        # shortcut: офлайн читается только первая страница; ленту изменений на нескольких страницах качай онлайн
        html = (html_dir / f"thread_{thread_id}.html").read_text(encoding="utf-8", errors="replace")
        res = etc.parse_thread_html(html, source=url)
        return res.title, res.posts
    title, posts = "", []
    while url:
        res = etc.parse_thread_html(etc.fetch_url(url, timeout=25, cookie=cookie), source=url)
        title = title or res.title
        posts += res.posts
        url = res.next_page_url if all_pages else None
    return title, posts


def edition_of(title: str, post) -> str | None:
    m = EDITION_RE.search(title) or EDITION_RE.search(post.text[:2000])
    if m:
        return m.group(1)
    iso = post.last_edited_at or post.published_at  # 2026-11-14T15:41:00+0300
    return f"{iso[8:10]}.{iso[5:7]}.{iso[:4]}" if iso else None


def render(slug: str, thread_id: int, old_title: str, edition: str | None, body: str) -> str:
    base = re.sub(r"\s*\(Редакция от [^)]*\)\s*$", "", old_title).strip()
    if slug == CHANGELOG_SLUG or not edition:
        title, edition_line = base, "Актуальная"
    else:
        title, edition_line = f"{base} (Редакция от {edition})", edition
    return "\n".join([
        f"# {title}",
        "",
        f"- **ID темы на форуме**: `{thread_id}`",
        f"- **URL темы**: {etc.FORUM_ORIGIN}/threads/{thread_id}/",
        f"- **Редакция**: {edition_line}",
        f"- **Категория**: {CATEGORY}",
        "- **Индексированных статей/разделов**: 0",  # число проставит build_laws_index
        "",
        "---",
        "",
        body.strip(),
        "",
    ])


def bump_patch_version() -> str | None:
    """1.2.0 → 1.2.1 в обоих манифестах: маркетплейс Claude Code обновляет плагин только при смене version."""
    root = BASE_DIR.parent.parent
    new_version = None
    for manifest in (root / "plugin.json", root / ".claude-plugin" / "plugin.json"):
        if not manifest.exists():
            continue
        raw = manifest.read_text(encoding="utf-8")
        m = re.search(r'"version":\s*"(\d+)\.(\d+)\.(\d+)"', raw)
        if not m:
            continue
        new_version = f"{m[1]}.{m[2]}.{int(m[3]) + 1}"
        manifest.write_text(raw[:m.start()] + f'"version": "{new_version}"' + raw[m.end():], encoding="utf-8", newline="\n")
    return new_version


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Обновление законодательной базы Mirror с форума")
    parser.add_argument("--cookie", help="Значение cookie xf_user (или переменная GTA5RP_XF_USER)")
    parser.add_argument("--html-dir", type=Path, help="Папка с сохранёнными страницами thread_<ID>.html")
    parser.add_argument("--only", nargs="+", metavar="SLUG", help="Обновить только эти законы (слаги из laws_index.json)")
    args = parser.parse_args(argv)

    cookie = (args.cookie or os.environ.get("GTA5RP_XF_USER", "")).strip().removeprefix("xf_user=")
    if not cookie and not args.html_dir:
        sys.stderr.write("Нужен cookie xf_user (--cookie или GTA5RP_XF_USER) либо --html-dir с сохранёнными страницами.\n")
        return 1

    laws = json.loads(INDEX_PATH.read_text(encoding="utf-8"))["laws"]
    unknown = set(args.only or []) - set(laws)
    if unknown:
        sys.stderr.write(f"Неизвестные слаги: {', '.join(sorted(unknown))}. Список: search_mirror_law.py --list\n")
        return 1

    changed, failed = [], []
    for slug, meta in laws.items():
        if args.only and slug not in args.only:
            continue
        tid = meta["thread_id"]
        try:
            title, posts = fetch_posts(tid, cookie, args.html_dir, all_pages=slug == CHANGELOG_SLUG)
        except Exception as exc:  # сеть, 403, нет файла — тему пропускаем, старый файл остаётся
            failed.append(f"{slug} (#{tid}): {exc}")
            continue
        body = "\n\n".join(p.text for p in posts) if slug == CHANGELOG_SLUG else (posts[0].text if posts else "")
        if len(body) < MIN_TEXT_LEN:
            failed.append(f"{slug} (#{tid}): пустой или слишком короткий текст — истёк cookie?")
            continue
        path = LAWS_DIR / meta["filename"]
        new = render(slug, tid, meta.get("title") or title, edition_of(title, posts[0]), body)
        old = path.read_text(encoding="utf-8") if path.exists() else ""
        # сравнение без строки счётчика: её всё равно перепишет build_laws_index
        strip_count = lambda s: build_laws_index.COUNT_RE.sub(r"\g<1>0", s.replace("\r\n", "\n"))
        if strip_count(old) != new:
            path.write_text(new, encoding="utf-8", newline="\n")
            changed.append(slug)
        print(f"  [{'UPD' if slug in changed else ' OK'}] {slug} (#{tid})")

    if changed:
        print("\nПересборка laws_index.json:")
        build_laws_index.main()
        version = bump_patch_version()  # до sync_copies не нужно: манифесты лежат в корне, а не в модулях
        if version:
            print(f"Версия плагина: {version}")
        sys.path.insert(0, str(BASE_DIR.parent.parent / "scripts"))
        import sync_copies
        sync_copies.main([])

    print(f"\nИзменено: {len(changed)}. Без изменений: {len(laws if not args.only else args.only) - len(changed) - len(failed)}. Ошибок: {len(failed)}.")
    for f in failed:
        print(f"  [FAIL] {f}")
    if changed:
        print("Дальше: git diff → commit → push в main (версия уже поднята).")
    return 1 if failed else 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    sys.exit(main())
