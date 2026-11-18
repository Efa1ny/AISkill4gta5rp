#!/usr/bin/env python3
"""Проверка внутренних отсылок законодательной базы Mirror.

Находит в текстах статей ссылки вида «статьи 20.5 настоящего Кодекса», «ст. 4.14, 4.15 настоящего закона»,
«статьей 5.2 Административного кодекса», «ст. 17.6 УК» и проверяет, что такая статья есть в базе.
Битая отсылка — ссылка на несуществующую статью: типичный след неаккуратной поправки
(статью перенумеровали или удалили, а ссылки на неё остались).

Примеры:
  python check_law_refs.py                  # все НПА
  python check_law_refs.py --law СК         # один закон
  python check_law_refs.py --law СК --json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_laws_index import load_articles  # noqa: E402
from search_mirror_law import find_law_slug, load_index, search_article  # noqa: E402

NUM = r"\d+(?:\.\d+)*"
# «статьи 37.6 и 37.8 настоящего Кодекса», «ст. 4.14, 4.15 настоящего закона», «статьей 5.2 Административного кодекса»
REF_RE = re.compile(
    rf"(?:\bстать[а-яё]*|\bст\.)\s*(?P<nums>{NUM}(?:\s*(?:,|и|–|-)\s*{NUM})*)\s+"
    r"(?P<target>настоящего\s+(?:кодекса|закона|положения)|[А-ЯЁ][а-яё]+\s+кодекса|(?:УК|ПК|СК|АК|ДК|ТК|ЭК)\b)",
    re.I,
)
CODE_NAMES = {"уголовного": "УК", "процессуального": "ПК", "судебного": "СК", "административного": "АК",
              "дорожного": "ДК", "трудового": "ТК", "этического": "ЭК", "избирательного": "избирательный кодекс"}


def target_slug(index: dict, own_slug: str, target: str) -> str | None:
    t = target.casefold()
    if t.startswith("настоящего"):
        return own_slug
    word = t.split()[0]
    return find_law_slug(index, CODE_NAMES.get(word, word))


def find_broken_refs(index: dict, slugs: list[str]) -> list[dict]:
    broken = []
    for slug in slugs:
        for art_num, art in load_articles(index["laws"][slug]).items():
            for m in REF_RE.finditer(art["text"]):
                ref_slug = target_slug(index, slug, m["target"])
                if not ref_slug:
                    continue
                for num in re.findall(NUM, m["nums"]):
                    if not search_article(index, ref_slug, num):
                        broken.append({
                            "law": slug,
                            "article": art_num,
                            "reference": m.group(0),
                            "target_law": ref_slug,
                            "missing_article": num,
                        })
    return broken


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Поиск битых отсылок между статьями законов Mirror")
    parser.add_argument("--law", "-l", help="Проверить один закон (УК, ПК, СК, слаг…); по умолчанию — все")
    parser.add_argument("--json", action="store_true", help="Вывод в JSON")
    args = parser.parse_args(argv)

    index = load_index()
    if args.law:
        slug = find_law_slug(index, args.law)
        if not slug:
            sys.stderr.write(f"Закон '{args.law}' не найден. Список: search_mirror_law.py --list\n")
            return 1
        slugs = [slug]
    else:
        slugs = list(index["laws"])

    broken = find_broken_refs(index, slugs)
    if args.json:
        print(json.dumps(broken, ensure_ascii=False, indent=2))
        return 0
    if not broken:
        print(f"Битых отсылок не найдено ({len(slugs)} НПА).")
        return 0
    print(f"Битых отсылок: {len(broken)}\n")
    for b in broken:
        print(f"- {b['law']} ст. {b['article']}: «{b['reference']}» → в {b['target_law']} нет статьи {b['missing_article']}")
    return 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    sys.exit(main())
