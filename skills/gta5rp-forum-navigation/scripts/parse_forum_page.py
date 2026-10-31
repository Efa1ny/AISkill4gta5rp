#!/usr/bin/env python3
"""Утилита для парсинга страницы раздела (форума) GTA 5 RP (XenForo 2.x).

Извлекает:
- Заголовок раздела и хлебные крошки (breadcrumbs)
- Вложенные подфорумы (subforums)
- Закрепленные темы (sticky threads)
- Обычные темы (regular threads)
- Пагинацию (текущая страница, всего страниц, ссылка на следующую страницу)

Примеры запуска:
  python parse_forum_page.py "https://forum.gta5rp.com/forums/verkhovnyi-sud.2188/"
  python parse_forum_page.py "https://forum.gta5rp.com/forums/verkhovnyi-sud.2188/" --json
  python parse_forum_page.py --file "./forum_list.html"
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from html import unescape
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urljoin
from urllib.request import Request, urlopen

FORUM_ORIGIN = "https://forum.gta5rp.com"
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)

TAG_RE = re.compile(r"<[^>]+>")
BREADCRUMB_BLOCK_RE = re.compile(
    r'<ul class="p-breadcrumbs[^"]*"[^>]*>(.*?)</ul>',
    re.DOTALL,
)
BREADCRUMB_LINK_RE = re.compile(
    r'<a href="([^"]+)"[^>]*>(.*?)</a>',
    re.DOTALL,
)
H1_TITLE_RE = re.compile(
    r'<h1 class="p-title-value"[^>]*>(.*?)</h1>',
    re.DOTALL,
)
SUBFORUM_BLOCK_RE = re.compile(
    r'<div class="node node--id\d+ node--depth\d+ node--forum[^"]*"[^>]*>(.*?)(?=<div class="node node--id|<div class="block-outer|<div class="structItemContainer|$)',
    re.DOTALL,
)
SUBFORUM_TITLE_RE = re.compile(
    r'<h3 class="node-title"[^>]*>\s*<a href="([^"]+)"[^>]*>(.*?)</a>',
    re.DOTALL,
)
STICKY_GROUP_RE = re.compile(
    r'<div class="structItemContainer-group structItemContainer-group--sticky[^"]*"[^>]*>(.*?)</div>\s*(?=<div class="structItemContainer-group js-threadList"|<div class="block-footer"|$)',
    re.DOTALL,
)
THREAD_START_RE = re.compile(r'<div class="structItem structItem--thread\b')
THREAD_ID_RE = re.compile(r"js-threadListItem-(\d+)")
AUTHOR_ATTR_RE = re.compile(r'data-author="([^"]+)"')
LOCKED_RE = re.compile(r"\bis-locked\b|structItem-status--locked")
LABEL_RE = re.compile(
    r'<span class="label[^"]*"[^>]*>\s*(.*?)\s*</span>',
    re.DOTALL,
)
TITLE_RE = re.compile(
    r'<a href="(/threads/[^"]+)"[^>]*data-tp-primary="on"[^>]*>\s*(.*?)\s*</a>',
    re.DOTALL,
)
FALLBACK_TITLE_RE = re.compile(
    r'<div class="structItem-title"[^>]*>.*?<a href="(/threads/[^"?]+)"[^>]*>\s*(.*?)\s*</a>',
    re.DOTALL,
)
START_TIME_RE = re.compile(
    r'structItem-startDate.*?<time[^>]*datetime="([^"]+)"',
    re.DOTALL,
)
LATEST_CELL_RE = re.compile(
    r"structItem-cell--latest(.*)$",
    re.DOTALL,
)
LATEST_TIME_RE = re.compile(r'structItem-latestDate[^>]*datetime="([^"]+)"')
USERNAME_RE = re.compile(r'class="username[^"]*"[^>]*>(.*?)</a>', re.DOTALL)
PAGE_NUM_RE = re.compile(r"/page-(\d+)")
CURRENT_PAGE_RE = re.compile(
    r'<li class="pageNav-page pageNav-page--current[^"]*"[^>]*>\s*<a[^>]*>(\d+)</a>',
    re.DOTALL,
)
NEXT_PAGE_RE = re.compile(
    r'<a href="([^"]+)"[^>]*class="pageNav-jump pageNav-jump--next"',
    re.DOTALL,
)


@dataclass
class BreadcrumbItem:
    title: str
    url: str


@dataclass
class SubforumItem:
    title: str
    url: str


@dataclass
class ThreadItem:
    thread_id: int
    title: str
    prefix: str | None
    url: str
    author: str
    started_at: str | None
    last_poster: str | None
    last_post_at: str | None
    is_sticky: bool
    is_locked: bool


@dataclass
class ForumPageResult:
    source: str
    title: str
    current_page: int
    total_pages: int
    next_page_url: str | None
    breadcrumbs: list[BreadcrumbItem]
    subforums: list[SubforumItem]
    sticky_threads: list[ThreadItem]
    regular_threads: list[ThreadItem]


def clean_html_text(raw: str) -> str:
    text = TAG_RE.sub(" ", raw)
    return unescape(re.sub(r"\s+", " ", text).strip())


def fetch_url(url: str, timeout: int = 20, cookie: str | None = None) -> str:
    cookie_val = (cookie or os.environ.get("GTA5RP_XF_USER", "")).strip()
    if cookie_val.startswith("xf_user="):
        cookie_val = cookie_val.split("=", 1)[1].strip()

    headers = {
        "User-Agent": DEFAULT_USER_AGENT,
        "Accept-Language": "ru,en;q=0.9",
    }
    if cookie_val:
        headers["Cookie"] = f"xf_user={cookie_val}"

    try:
        req = Request(url, headers=headers)
        with urlopen(req, timeout=timeout) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(charset, errors="replace")
    except Exception:
        cmd = ["curl.exe", "-sSL", "-A", DEFAULT_USER_AGENT]
        if cookie_val:
            cmd.extend(["-b", f"xf_user={cookie_val}"])
        cmd.append(url)
        res = subprocess.run(cmd, capture_output=True, timeout=timeout)
        if res.returncode == 0 and res.stdout:
            return res.stdout.decode("utf-8", errors="replace")
        raise


def parse_breadcrumbs(html: str, base_url: str) -> list[BreadcrumbItem]:
    block_match = BREADCRUMB_BLOCK_RE.search(html)
    if not block_match:
        return []
    seen: set[tuple[str, str]] = set()
    items: list[BreadcrumbItem] = []
    for href, raw_title in BREADCRUMB_LINK_RE.findall(block_match.group(1)):
        title = clean_html_text(raw_title)
        full_url = urljoin(base_url, unescape(href))
        key = (title, full_url)
        if title and key not in seen:
            seen.add(key)
            items.append(BreadcrumbItem(title=title, url=full_url))
    return items


def parse_subforums(html: str, base_url: str) -> list[SubforumItem]:
    items: list[SubforumItem] = []
    seen: set[str] = set()
    for match in SUBFORUM_TITLE_RE.finditer(html):
        url = urljoin(base_url, unescape(match.group(1)))
        title = clean_html_text(match.group(2))
        if title and url not in seen:
            seen.add(url)
            items.append(SubforumItem(title=title, url=url))
    return items


def _parse_single_thread(block: str, base_url: str, is_sticky: bool) -> ThreadItem | None:
    id_match = THREAD_ID_RE.search(block)
    title_match = TITLE_RE.search(block) or FALLBACK_TITLE_RE.search(block)
    if not id_match or not title_match:
        return None

    thread_id = int(id_match.group(1))
    url = urljoin(base_url, unescape(title_match.group(1)))
    title = clean_html_text(title_match.group(2))

    author_match = AUTHOR_ATTR_RE.search(block)
    if author_match:
        author = clean_html_text(author_match.group(1))
    else:
        user_match = USERNAME_RE.search(block)
        author = clean_html_text(user_match.group(1)) if user_match else "unknown"

    label_match = LABEL_RE.search(block)
    prefix = clean_html_text(label_match.group(1)) if label_match else None

    start_match = START_TIME_RE.search(block)
    started_at = start_match.group(1) if start_match else None

    latest_cell = LATEST_CELL_RE.search(block)
    latest_html = latest_cell.group(1) if latest_cell else block
    latest_time_match = LATEST_TIME_RE.search(latest_html)
    last_post_at = latest_time_match.group(1) if latest_time_match else None

    last_user_match = USERNAME_RE.search(latest_html)
    last_poster = clean_html_text(last_user_match.group(1)) if last_user_match else None

    is_locked = bool(LOCKED_RE.search(block))

    return ThreadItem(
        thread_id=thread_id,
        title=title,
        prefix=prefix,
        url=url,
        author=author,
        started_at=started_at,
        last_poster=last_poster,
        last_post_at=last_post_at,
        is_sticky=is_sticky,
        is_locked=is_locked,
    )


def _extract_threads_from_chunk(chunk: str, base_url: str, is_sticky: bool) -> list[ThreadItem]:
    starts = [m.start() for m in THREAD_START_RE.finditer(chunk)]
    results: list[ThreadItem] = []
    seen_ids: set[int] = set()
    for idx, start in enumerate(starts):
        end = starts[idx + 1] if idx + 1 < len(starts) else len(chunk)
        item = _parse_single_thread(chunk[start:end], base_url, is_sticky=is_sticky)
        if item and item.thread_id not in seen_ids:
            seen_ids.add(item.thread_id)
            results.append(item)
    return results


def parse_forum_html(html: str, source: str, base_url: str = FORUM_ORIGIN) -> ForumPageResult:
    h1_match = H1_TITLE_RE.search(html)
    title = clean_html_text(h1_match.group(1)) if h1_match else "Раздел форума"

    breadcrumbs = parse_breadcrumbs(html, base_url)
    subforums = parse_subforums(html, base_url)

    sticky_threads: list[ThreadItem] = []
    regular_threads: list[ThreadItem] = []

    list_split = "structItemContainer-group js-threadList"
    if list_split in html:
        before_regular, regular_part = html.split(list_split, 1)
        if "structItemContainer-group--sticky" in before_regular:
            sticky_chunk = before_regular.split("structItemContainer-group--sticky", 1)[-1]
            sticky_threads = _extract_threads_from_chunk(sticky_chunk, base_url, is_sticky=True)
        regular_threads = _extract_threads_from_chunk(regular_part, base_url, is_sticky=False)
    else:
        sticky_match = STICKY_GROUP_RE.search(html)
        if sticky_match:
            sticky_threads = _extract_threads_from_chunk(
                sticky_match.group(1), base_url, is_sticky=True
            )
        regular_threads = _extract_threads_from_chunk(html, base_url, is_sticky=False)

    page_numbers = [int(n) for n in PAGE_NUM_RE.findall(html)]
    total_pages = max(page_numbers, default=1)

    current_match = CURRENT_PAGE_RE.search(html)
    current_page = int(current_match.group(1)) if current_match else 1

    next_match = NEXT_PAGE_RE.search(html)
    next_page_url = urljoin(base_url, unescape(next_match.group(1))) if next_match else None

    return ForumPageResult(
        source=source,
        title=title,
        current_page=current_page,
        total_pages=total_pages,
        next_page_url=next_page_url,
        breadcrumbs=breadcrumbs,
        subforums=subforums,
        sticky_threads=sticky_threads,
        regular_threads=regular_threads,
    )


def format_markdown(result: ForumPageResult) -> str:
    lines: list[str] = []
    lines.append(f"# {result.title}")
    lines.append(f"- **Источник**: {result.source}")
    lines.append(f"- **Страница**: {result.current_page} из {result.total_pages}")
    if result.next_page_url:
        lines.append(f"- **Следующая страница**: {result.next_page_url}")

    if result.breadcrumbs:
        crumbs = " → ".join(f"[{b.title}]({b.url})" for b in result.breadcrumbs)
        lines.append(f"- **Навигация**: {crumbs}")

    if result.subforums:
        lines.append("\n## Вложенные подфорумы")
        for sub in result.subforums:
            lines.append(f"- [{sub.title}]({sub.url})")

    if result.sticky_threads:
        lines.append(f"\n## Закрепленные темы ({len(result.sticky_threads)})")
        for t in result.sticky_threads:
            prefix_str = f"[{t.prefix}] " if t.prefix else ""
            lock_str = " 🔒" if t.is_locked else ""
            lines.append(
                f"- **{prefix_str}[{t.title}]({t.url})**{lock_str} "
                f"(ID: `{t.thread_id}`, Автор: `{t.author}`, Создано: `{t.started_at or '—'}`)"
            )

    lines.append(f"\n## Обычные темы ({len(result.regular_threads)})")
    if not result.regular_threads:
        lines.append("_Обычные темы не найдены на странице._")
    else:
        for t in result.regular_threads:
            prefix_str = f"[{t.prefix}] " if t.prefix else ""
            lock_str = " 🔒" if t.is_locked else ""
            lines.append(
                f"- **{prefix_str}[{t.title}]({t.url})**{lock_str} "
                f"(ID: `{t.thread_id}`, Автор: `{t.author}`, Создано: `{t.started_at or '—'}`, "
                f"Последний ответ: `{t.last_poster or '—'}` в `{t.last_post_at or '—'}`)"
            )

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Парсер разделов форума GTA 5 RP (XenForo 2.x)"
    )
    parser.add_argument("url", nargs="?", help="URL страницы раздела форума")
    parser.add_argument("--file", "-f", help="Путь к локальному HTML-файлу вместо URL")
    parser.add_argument("--cookie", "-c", help="Значение cookie xf_user (или через GTA5RP_XF_USER)")
    parser.add_argument("--json", action="store_true", help="Вывести результат в формате JSON")
    args = parser.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    if not args.url and not args.file:
        parser.error("Укажите URL раздела или флаг --file <путь_к_html>")

    if args.file:
        path = Path(args.file)
        html = path.read_text(encoding="utf-8")
        source = str(path.resolve())
        base_url = FORUM_ORIGIN
    else:
        html = fetch_url(args.url, cookie=args.cookie)
        source = args.url
        base_url = args.url

    result = parse_forum_html(html, source=source, base_url=base_url)
    if args.json:
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    else:
        print(format_markdown(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
