#!/usr/bin/env python3
"""Пересборка поискового индекса laws_index.json по файлам references/laws/*.md.

Метаданные закона (ID темы, алиасы) берутся из текущего индекса, название и редакция —
из заголовка md-файла «# Название (Редакция от ДД.ММ.ГГГГ)». Статьи распознаются по строкам
«Статья N[.N]» и «N.N[.N]» в начале абзаца; заголовками глав считаются строки «Раздел …» и «Глава …».
Повторяющиеся номера (например, «Статья 1» в каждом разделе Конституции) получают ключ
«N (Раздел …)», чтобы не затирать друг друга.

Запуск:
  python build_laws_index.py
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


def main() -> int:
    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    for slug, meta in index["laws"].items():
        path = LAWS_DIR / meta["filename"]
        if not path.exists():
            sys.stderr.write(f"Нет файла {path}\n")
            continue
        raw = path.read_text(encoding="utf-8")
        head, sep, body = raw.partition("\n---\n")
        if not sep:
            body = raw
        title_m = HEADER_RE.search(head)
        if title_m:
            meta["title"] = title_m.group(1)
            ed = EDITION_RE.search(title_m.group(1))
            if ed:
                meta["edition_date"] = ed.group(1)
        meta["articles"] = parse_articles(body)
        meta["articles_count"] = len(meta["articles"])
        new_raw = COUNT_RE.sub(rf"\g<1>{meta['articles_count']}", raw, count=1)
        if new_raw != raw:
            path.write_text(new_raw, encoding="utf-8", newline="\n")
        print(f"{slug:<36} {meta['articles_count']:>4}  {meta.get('edition_date') or '-'}")
    index["updated_at"] = date.today().isoformat()
    INDEX_PATH.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
