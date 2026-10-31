#!/usr/bin/env python3
"""CLI-утилита для быстрого офлайн-поиска по Законодательной базе, прецедентам ВС и OOC-правилам сервера GTA 5 RP Mirror.

Использует локальный поисковый индекс laws_index.json и файлы в references/laws/.
Не требует внешних библиотек (работает на чистом Python 3.10+).

Примеры запуска:
  python search_mirror_law.py --list
  python search_mirror_law.py --law УК --article 17.6
  python search_mirror_law.py --law ПК --article 15.1
  python search_mirror_law.py --law "взаимодействие" --article 8.1
  python search_mirror_law.py --query "неповиновение"
  python search_mirror_law.py --query "штурм титульного района" --ooc
  python search_mirror_law.py --precedents --query "LEP-1"
  python search_mirror_law.py --law УК --article 15.1 --json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
LAWS_DIR = BASE_DIR / "references" / "laws"
INDEX_PATH = LAWS_DIR / "laws_index.json"


def load_index() -> dict:
    if not INDEX_PATH.exists():
        sys.stderr.write(f"Ошибка: Индекс законов не найден: {INDEX_PATH}\n")
        sys.exit(1)
    return json.loads(INDEX_PATH.read_text(encoding="utf-8"))


def find_law_slug(index: dict, name_or_alias: str) -> str | None:
    query = name_or_alias.strip().casefold()
    laws = index.get("laws", {})

    # Точное совпадение со слагом
    if query in laws:
        return query

    # Совпадение по алиасам
    for slug, meta in laws.items():
        if query in [a.casefold() for a in meta.get("aliases", [])]:
            return slug

    # Частичное совпадение в алиасах или названии
    for slug, meta in laws.items():
        title = meta.get("title", "").casefold()
        if query in title or any(query in a.casefold() for a in meta.get("aliases", [])):
            return slug

    return None


def list_laws(index: dict):
    laws = index.get("laws", {})
    print(f"=== Законодательная база сервера Mirror (Всего НПА: {len(laws)}) ===")
    print(f"{'Слаг / Код':<32} | {'Статей':<6} | {'Редакция':<12} | {'Название'}")
    print("-" * 90)
    for slug, meta in laws.items():
        aliases = ", ".join(meta.get("aliases", [])[:3])
        ed = meta.get("edition_date") or "-"
        cnt = meta.get("articles_count", 0)
        title = meta.get("title", "")
        print(f"{slug:<32} | {cnt:<6} | {ed:<12} | {title} (Алиасы: {aliases})")


def search_article(index: dict, slug: str, article_num: str) -> list[dict]:
    laws = index.get("laws", {})
    law_meta = laws.get(slug)
    if not law_meta:
        return []

    articles = law_meta.get("articles", {})
    target = article_num.strip().rstrip(".*")

    results = []
    # 1. Точное совпадение номера
    if target in articles:
        results.append(articles[target])

    # 2. Префиксное или похожее совпадение (например 17.6 и 17.6.1)
    if not results:
        for num, art in articles.items():
            if num.startswith(target) or target in num:
                results.append(art)

    return results


def search_text(index: dict, query: str, law_slug: str | None = None, include_ooc: bool = False, include_precedents: bool = False) -> list[dict]:
    q_low = query.strip().casefold()
    results = []

    laws = index.get("laws", {})
    target_slugs = [law_slug] if law_slug else list(laws.keys())

    for slug in target_slugs:
        meta = laws.get(slug)
        if not meta:
            continue
        for num, art in meta.get("articles", {}).items():
            t_low = (art.get("title") or "").casefold()
            b_low = (art.get("text") or "").casefold()
            c_low = (art.get("chapter") or "").casefold()

            if q_low in t_low or q_low in b_low or q_low in num.casefold():
                score = 0
                if q_low in num.casefold():
                    score += 10
                if q_low in t_low:
                    score += 5
                score += b_low.count(q_low)
                results.append({
                    "source": "law",
                    "law_slug": slug,
                    "law_title": meta.get("title"),
                    "chapter": art.get("chapter"),
                    "article": num,
                    "title": art.get("title"),
                    "text": art.get("text"),
                    "score": score,
                })

    # Поиск по судебным прецедентам
    if include_precedents or not law_slug:
        prec_file = LAWS_DIR / "precedents_3424533.md"
        if prec_file.exists():
            prec_text = prec_file.read_text(encoding="utf-8")
            if q_low in prec_text.casefold():
                blocks = prec_text.split("### ")
                for bl in blocks[1:]:
                    if q_low in bl.casefold():
                        first_line = bl.splitlines()[0]
                        results.append({
                            "source": "precedent",
                            "law_slug": "precedents",
                            "law_title": "Реестр прецедентов ВС Mirror (3424533)",
                            "chapter": "Прецедентная практика ВС",
                            "article": first_line,
                            "title": first_line,
                            "text": bl.strip(),
                            "score": bl.casefold().count(q_low) * 2,
                        })

    # Поиск по OOC-правилам
    if include_ooc or not law_slug:
        ooc_file = LAWS_DIR / "ooc_rules_mirror.md"
        if ooc_file.exists():
            ooc_text = ooc_file.read_text(encoding="utf-8")
            if q_low in ooc_text.casefold():
                sections = ooc_text.split("## ")
                for sec in sections[1:]:
                    if q_low in sec.casefold():
                        first_line = sec.splitlines()[0]
                        results.append({
                            "source": "ooc_rule",
                            "law_slug": "ooc_rules",
                            "law_title": "OOC правила проекта и сервера Mirror",
                            "chapter": "OOC Регламент",
                            "article": first_line,
                            "title": first_line,
                            "text": sec.strip()[:1500] + ("..." if len(sec) > 1500 else ""),
                            "score": sec.casefold().count(q_low),
                        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Поиск по законодательству сервера Mirror GTA 5 RP")
    parser.add_argument("--list", action="store_true", help="Вывести список всех НПА и алиасов")
    parser.add_argument("--law", "-l", help="Название, слаг или аббревиатура закона (например, УК, ПК, СК, ЗОТ)")
    parser.add_argument("--article", "-a", help="Номер статьи (например, 17.6, 15.1, 8.1)")
    parser.add_argument("--query", "-q", help="Поисковая фраза или ключевые слова")
    parser.add_argument("--precedents", action="store_true", help="Включить поиск по судебным прецедентам ВС")
    parser.add_argument("--ooc", action="store_true", help="Включить поиск по OOC-правилам и переопределениям Mirror")
    parser.add_argument("--json", action="store_true", help="Вывод результатов в формате JSON")
    args = parser.parse_args()

    index = load_index()

    if args.list:
        list_laws(index)
        return 0

    slug = None
    if args.law:
        slug = find_law_slug(index, args.law)
        if not slug:
            sys.stderr.write(f"Закон с названием/алиасом '{args.law}' не найден. Используйте --list для списка.\n")
            return 1

    # 1. Поиск конкретной статьи
    if args.article:
        if not slug:
            sys.stderr.write("Укажите закон через --law (например, --law УК --article 17.6)\n")
            return 1
        matches = search_article(index, slug, args.article)
        if not matches:
            sys.stderr.write(f"Статья '{args.article}' не найдена в {slug}.\n")
            return 1
        if args.json:
            print(json.dumps(matches, ensure_ascii=False, indent=2))
        else:
            law_title = index["laws"][slug]["title"]
            print(f"=== {law_title} (Статья {args.article}) ===")
            for m in matches:
                if m.get("chapter"):
                    print(f"[{m['chapter']}]")
                print(m.get("text"))
                print("-" * 50)
        return 0

    # 2. Текстовый поиск
    if args.query:
        matches = search_text(index, args.query, law_slug=slug, include_ooc=args.ooc, include_precedents=args.precedents)
        if not matches:
            print(f"Ничего не найдено по запросу: '{args.query}'")
            return 0
        if args.json:
            print(json.dumps(matches[:15], ensure_ascii=False, indent=2))
        else:
            print(f"Найдено совпадений: {len(matches)} (показано до 10 лучших)\n")
            for i, m in enumerate(matches[:10], 1):
                src = m["source"].upper()
                print(f"{i}. [{src}] {m['law_title']} — {m.get('chapter', '')} / {m['article']}")
                txt = m.get("text", "").strip()
                preview = txt[:400] + ("..." if len(txt) > 400 else "")
                print(f"{preview}\n" + "-" * 70)
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
