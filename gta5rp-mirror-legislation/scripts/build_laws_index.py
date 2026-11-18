#!/usr/bin/env python3
"""Пересборка индекса laws_index.json по файлам references/laws/*.md.

Индекс хранит только метаданные законов (файл, ID темы, алиасы, название, редакция, число статей).
Тексты статей не дублируются: search_mirror_law.py разбирает md на лету через parse_articles()
(вся база — ~10 мс), поэтому индекс не может разойтись с текстом законов.

Метаданные (ID темы, алиасы) берутся из текущего индекса, название и редакция —
из заголовка md-файла «# Название (Редакция от ДД.ММ.ГГГГ)». Статьи распознаются по строкам
«Статья N[.N]» и «N.N[.N]» в начале абзаца; заголовками глав считаются строки «Раздел …» и «Глава …».
Повторяющиеся номера (например, «Статья 1» в каждом разделе Конституции) получают ключ
«N (Раздел …)», чтобы не затирать друг друга.

Запуск:
  python build_laws_index.py           # пересобрать индекс
  python build_laws_index.py --check   # только проверить: exit 1, если индекс устарел (для CI)
"""

from __future__ import annotations

from datetime import date
import json
from pathlib import Path
import re
import sys

LAWS_DIR = Path(__file__).resolve().parent.parent / "references" / "laws"
INDEX_PATH = LAWS_DIR / "laws_index.json"

HEADER_RE = re.compile(r"^#\s+(.*?)\s*$", re.M)
EDITION_RE = re.compile(r"Редакция от (\d\d\.\d\d\.\d{4})")
CHAPTER_RE = re.compile(r"^(?:Раздел|РАЗДЕЛ|Глава|ГЛАВА)\b")
ARTICLE_RE = re.compile(r"^(?:Статья\s+(\d+(?:\.\d+)*)\.?|(\d+\.\d+(?:\.\d+)*)\.?)\**\s*(.*)$")
COUNT_RE = re.compile(r"(\*\*Индексированных статей/разделов\*\*: )\d+")


def parse_articles(body: str) -> dict[str, dict]:
    articles: dict[str, dict] = {}
    chapter = ""
    current: dict | None = None

    def flush() -> None:
        if not current:
            return
        current["text"] = "\n".join(current.pop("_lines")).strip()
        key = current["number"]
        if key in articles:
            key = f"{key} ({current['chapter']})" if current["chapter"] else key
            n = 2
            while key in articles:
                key = f"{current['number']} ({current['chapter']}) #{n}"
                n += 1
        articles[key] = current

    for line in body.split("\n"):
        stripped = line.strip()
        if CHAPTER_RE.match(stripped):
            flush()
            current = None
            chapter = stripped
            continue
        m = ARTICLE_RE.match(stripped)
        if m:
            flush()
            current = {
                "number": m.group(1) or m.group(2),
                "title": m.group(3).strip(),
                "chapter": chapter,
                "_lines": [stripped],
            }
            continue
        if current is not None:
            current["_lines"].append(line)
    flush()
    return articles


def split_law_file(raw: str) -> tuple[str, str]:
    """md-файл закона → (шапка, тело со статьями)."""
    head, sep, body = raw.partition("\n---\n")
    return (head, body) if sep else (head, raw)


def load_articles(meta: dict) -> dict[str, dict]:
    """Статьи закона из его md-файла (тексты в индексе не хранятся)."""
    path = LAWS_DIR / meta["filename"]
    if not path.exists():
        return {}
    return parse_articles(split_law_file(path.read_text(encoding="utf-8"))[1])


def main(argv: list[str] | None = None) -> int:
    check = "--check" in (argv or [])
    old_text = INDEX_PATH.read_text(encoding="utf-8")
    old_index = json.loads(old_text)
    index = json.loads(old_text)
    stale = []
    for slug, meta in index["laws"].items():
        path = LAWS_DIR / meta["filename"]
        if not path.exists():
            sys.stderr.write(f"Нет файла {path}\n")
            stale.append(slug)
            continue
        raw = path.read_text(encoding="utf-8")
        head, body = split_law_file(raw)
        title_m = HEADER_RE.search(head)
        if title_m:
            meta["title"] = title_m.group(1)
            ed = EDITION_RE.search(title_m.group(1))
            if ed:
                meta["edition_date"] = ed.group(1)
        meta.pop("articles", None)  # старый формат индекса хранил тексты статей
        meta["articles_count"] = len(parse_articles(body))
        new_raw = COUNT_RE.sub(rf"\g<1>{meta['articles_count']}", raw, count=1)
        if meta != old_index["laws"][slug] or new_raw != raw:
            stale.append(slug)
        if new_raw != raw and not check:
            path.write_text(new_raw, encoding="utf-8", newline="\n")
        if not check:
            print(f"{slug:<36} {meta['articles_count']:>4}  {meta.get('edition_date') or '-'}")

    if check:
        if stale:
            print("Индекс устарел (запусти python build_laws_index.py):\n  " + "\n  ".join(stale))
            return 1
        print(f"Индекс актуален: {len(index['laws'])} НПА.")
        return 0
    if stale:  # дата меняется только вместе с содержимым — без лишних диффов
        index["updated_at"] = date.today().isoformat()
        INDEX_PATH.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
