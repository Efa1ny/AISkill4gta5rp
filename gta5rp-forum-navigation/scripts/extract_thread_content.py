#!/usr/bin/env python3
"""Утилита для полного извлечения содержимого темы (постов, спойлеров, цитат, ссылок и медиа) на форуме GTA 5 RP.

Автоматически:
- Извлекает все посты на странице темы (номер поста, ID, автор, должность, плашки, время публикации и редактирования)
- Раскрывает текст внутри спойлеров (.bbCodeSpoiler) и свернутых цитат (blockquote.bbCodeBlock--quote)
- Извлекает все скрытые за словами «тык» / «клик» гиперссылки и классифицирует их (Imgur, Yapx, YouTube, Rutube, Google Docs/Sheets/Drive, Discord, внутренние ссылки форума)
- Извлекает встроенные изображения (включая lazy-load data-src) и видео-плееры (iframe)

Примеры запуска:
  python extract_thread_content.py "https://forum.gta5rp.com/threads/iskovoye-zayavleniye-no248.3418114/"
  python extract_thread_content.py "https://forum.gta5rp.com/threads/..." --json
  python extract_thread_content.py --file "./thread.html"
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from html import unescape
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

FORUM_ORIGIN = "https://forum.gta5rp.com"
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)

TAG_RE = re.compile(r"<[^>]+>")
H1_TITLE_RE = re.compile(r'<h1 class="p-title-value"[^>]*>(.*?)</h1>', re.DOTALL)
LABEL_RE = re.compile(r'<span class="label[^"]*"[^>]*>(.*?)</span>', re.DOTALL)
BREADCRUMB_BLOCK_RE = re.compile(r'<ul class="p-breadcrumbs[^"]*"[^>]*>(.*?)</ul>', re.DOTALL)
BREADCRUMB_LINK_RE = re.compile(r'<a href="([^"]+)"[^>]*>(.*?)</a>', re.DOTALL)
PAGE_NUM_RE = re.compile(r"/page-(\d+)")
CURRENT_PAGE_RE = re.compile(
    r'<li class="pageNav-page pageNav-page--current[^"]*"[^>]*>\s*<a[^>]*>(\d+)</a>',
    re.DOTALL,
)
NEXT_PAGE_RE = re.compile(
    r'<a href="([^"]+)"[^>]*class="pageNav-jump pageNav-jump--next"',
    re.DOTALL,
)

ARTICLE_START_RE = re.compile(r'<article class="message message--post\b[^>]*>', re.DOTALL)
POST_ID_RE = re.compile(r'data-content="post-(\d+)"|id="js-post-(\d+)"')
AUTHOR_ATTR_RE = re.compile(r'data-author="([^"]+)"')
USER_TITLE_RE = re.compile(r'<h5 class="userTitle[^"]*"[^>]*>(.*?)</h5>', re.DOTALL)
USER_BANNER_RE = re.compile(r'<div class="userBanner[^"]*"[^>]*>(.*?)</div>', re.DOTALL)
HEADER_TIME_RE = re.compile(
    r'<header class="message-attribution[^"]*"[^>]*>.*?<time[^>]*datetime="([^"]+)"',
    re.DOTALL,
)
FALLBACK_TIME_RE = re.compile(r'<time[^>]*datetime="([^"]+)"')
POST_NUM_RE = re.compile(
    r'<a href="([^"]+)"[^>]*>\s*#(\d+)\s*</a>',
    re.DOTALL,
)
LAST_EDIT_RE = re.compile(
    r'<div class="message-lastEdit"[^>]*>.*?<time[^>]*datetime="([^"]+)"',
    re.DOTALL,
)


@dataclass
class ExtractedLink:
    anchor: str
    url: str
    category: str
    normalized_media_url: str | None = None


@dataclass
class ExtractedMedia:
    media_type: str
    url: str
    alt: str | None = None


@dataclass
class ForumPost:
    post_id: int
    post_number: int
    permalink: str
    author: str
    user_title: str | None
    user_banners: list[str]
    published_at: str | None
    last_edited_at: str | None
    text: str
    links: list[ExtractedLink]
    media: list[ExtractedMedia]


@dataclass
class ThreadPageResult:
    source: str
    title: str
    prefix: str | None
    current_page: int
    total_pages: int
    next_page_url: str | None
    breadcrumbs: list[dict[str, str]]
    posts: list[ForumPost]


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


def classify_url(url: str) -> tuple[str, str | None]:
    """Классифицирует URL и при возможности возвращает прямую ссылку для скачивания/экспорта."""
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    path = parsed.path

    if not host or "forum.gta5rp.com" in host:
        return "internal_forum", None
    if "gta5rp.com" in host:
        return "gta5rp_main", None

    if "imgur.com" in host:
        if host == "i.imgur.com":
            return "imgur_direct", url
        if path.startswith(("/a/", "/gallery/")):
            return "imgur_album", None
        img_id = path.strip("/").split("/")[0]
        if img_id and "." not in img_id:
            return "imgur_single", f"https://i.imgur.com/{img_id}.png"
        return "imgur", None

    if "yapx.ru" in host:
        if host == "i.yapx.ru":
            return "yapx_direct", url
        return "yapx_album", None

    if "youtube.com" in host or "youtu.be" in host:
        return "youtube", None

    if "rutube.ru" in host:
        return "rutube", None

    if "twitch.tv" in host:
        return "twitch", None

    if "docs.google.com" in host:
        doc_match = re.search(r"/document/d/([a-zA-Z0-9_-]+)", path)
        if doc_match:
            doc_id = doc_match.group(1)
            return "google_docs", f"https://docs.google.com/document/d/{doc_id}/export?format=txt"
        sheet_match = re.search(r"/spreadsheets/d/([a-zA-Z0-9_-]+)", path)
        if sheet_match:
            sheet_id = sheet_match.group(1)
            gid_match = re.search(r"gid=(\d+)", parsed.query + "#" + parsed.fragment)
            gid = gid_match.group(1) if gid_match else "0"
            return (
                "google_sheets",
                f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}",
            )

    if "drive.google.com" in host:
        file_match = re.search(r"/file/d/([a-zA-Z0-9_-]+)", path)
        if file_match:
            file_id = file_match.group(1)
            return "google_drive", f"https://drive.google.com/uc?export=download&id={file_id}"
        return "google_drive", None

    if "discordapp.com" in host or "discordapp.net" in host or "discord.com" in host:
        return "discord", None

    if any(h in host for h in ("postimg.cc", "ibb.co", "prnt.sc", "lightshot")):
        return "image_hosting", None

    return "external", None


class BBWrapperParser(HTMLParser):
    """Парсит div.bbWrapper с сохранением структуры спойлеров, цитат, таблиц, ссылок и медиа."""

    def __init__(self, base_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.chunks: list[str] = []
        self.links: list[ExtractedLink] = []
        self.media: list[ExtractedMedia] = []
        self._seen_links: set[tuple[str, str]] = set()
        self._seen_media: set[str] = set()

        self._in_link_href: str | None = None
        self._in_link_text: list[str] = []
        self._ignore_depth = 0
        self._spoiler_depth = 0
        self._quote_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_dict = {k: (v or "") for k, v in attrs}
        classes = set(attr_dict.get("class", "").split())

        if "bbCodeBlock-expandLink" in classes or "js-expandLink" in classes:
            self._ignore_depth += 1
            return

        if self._ignore_depth > 0:
            self._ignore_depth += 1
            return

        if tag in ("br", "hr"):
            self.chunks.append("\n")
        elif tag in ("p", "div", "li", "tr", "blockquote", "pre"):
            if "bbCodeSpoiler" in classes:
                self._spoiler_depth += 1
                self.chunks.append("\n\n[СПОЙЛЕР ")
            elif "bbCodeSpoiler-content" in classes:
                self.chunks.append("]:\n")
            elif tag == "blockquote" and "bbCodeBlock--quote" in classes:
                self._quote_depth += 1
                quoted_user = attr_dict.get("data-quote", "Пользователь")
                self.chunks.append(f"\n\n> [ЦИТАТА от {quoted_user}]:\n> ")
            elif tag == "li":
                self.chunks.append("\n• ")
            elif tag == "tr":
                self.chunks.append("\n")
            else:
                self.chunks.append("\n")
        elif tag in ("td", "th"):
            self.chunks.append(" | ")

        if tag == "a":
            href = attr_dict.get("href", "").strip()
            if href and not href.startswith("javascript:"):
                self._in_link_href = urljoin(self.base_url, href)
                self._in_link_text = []
                if "js-lbImage" in classes:
                    self._add_media("lightbox_image", self._in_link_href, None)

        if tag == "img":
            src = (
                attr_dict.get("data-url")
                or attr_dict.get("data-src")
                or attr_dict.get("src")
                or ""
            ).strip()
            if src and not src.startswith("data:image/"):
                full_src = urljoin(self.base_url, src)
                alt = attr_dict.get("alt") or None
                self._add_media("image", full_src, alt)

        if tag == "iframe":
            src = (attr_dict.get("data-s9e-mediaembed-iframe") or attr_dict.get("src") or "").strip()
            if src:
                full_src = urljoin(self.base_url, src)
                self._add_media("iframe_embed", full_src, None)

    def handle_endtag(self, tag: str) -> None:
        if self._ignore_depth > 0:
            self._ignore_depth -= 1
            return

        if tag == "a" and self._in_link_href is not None:
            anchor = re.sub(r"\s+", " ", "".join(self._in_link_text)).strip() or "[без текста]"
            href = self._in_link_href
            if "/goto/post" not in href:
                key = (anchor, href)
                if key not in self._seen_links:
                    self._seen_links.add(key)
                    category, norm_url = classify_url(href)
                    self.links.append(
                        ExtractedLink(
                            anchor=anchor,
                            url=href,
                            category=category,
                            normalized_media_url=norm_url,
                        )
                    )
                self.chunks.append(f" ({href}) ")
            self._in_link_href = None
            self._in_link_text = []

        if tag == "blockquote" and self._quote_depth > 0:
            self._quote_depth -= 1
            self.chunks.append("\n[/ЦИТАТА]\n")

    def handle_data(self, data: str) -> None:
        if self._ignore_depth > 0:
            return
        self.chunks.append(data)
        if self._in_link_href is not None:
            self._in_link_text.append(data)

    def _add_media(self, media_type: str, url: str, alt: str | None) -> None:
        if url not in self._seen_media:
            self._seen_media.add(url)
            self.media.append(ExtractedMedia(media_type=media_type, url=url, alt=alt))

    def get_clean_text(self) -> str:
        raw = "".join(self.chunks)
        raw = re.sub(r'\{\s*"lightbox_close".*?\}', "", raw, flags=re.DOTALL)
        raw = raw.replace("\u200b", "").replace("\ufeff", "")
        lines = [re.sub(r"[ \t]+", " ", line).strip() for line in raw.splitlines()]
        cleaned = "\n".join(lines)
        return re.sub(r"\n{3,}", "\n\n", cleaned).strip()


def extract_balanced_div(html: str, start_marker: str) -> str | None:
    """Находит первый div с заданным маркером и возвращает его внутренний HTML с учетом вложенности."""
    pos = html.find(start_marker)
    if pos == -1:
        return None
    open_tag_end = html.find(">", pos)
    if open_tag_end == -1:
        return None

    depth = 1
    tag_iter = re.finditer(r"</?div\b[^>]*>", html[open_tag_end + 1 :], re.IGNORECASE)
    for match in tag_iter:
        token = match.group(0).lower()
        if token.startswith("</div"):
            depth -= 1
            if depth == 0:
                end_pos = open_tag_end + 1 + match.start()
                return html[open_tag_end + 1 : end_pos]
        else:
            depth += 1
    return html[open_tag_end + 1 :]


def parse_single_post(article_html: str, base_url: str, fallback_index: int) -> ForumPost:
    id_match = POST_ID_RE.search(article_html)
    post_id = int(id_match.group(1) or id_match.group(2)) if id_match else fallback_index

    author_match = AUTHOR_ATTR_RE.search(article_html)
    author = clean_html_text(author_match.group(1)) if author_match else "unknown"

    title_match = USER_TITLE_RE.search(article_html)
    user_title = clean_html_text(title_match.group(1)) if title_match else None

    banners = [
        clean_html_text(b)
        for b in USER_BANNER_RE.findall(article_html)
        if clean_html_text(b)
    ]

    time_match = HEADER_TIME_RE.search(article_html) or FALLBACK_TIME_RE.search(article_html)
    published_at = time_match.group(1) if time_match else None

    num_match = POST_NUM_RE.search(article_html)
    if num_match:
        permalink = urljoin(base_url, unescape(num_match.group(1)))
        post_number = int(num_match.group(2))
    else:
        permalink = f"{base_url}#post-{post_id}"
        post_number = fallback_index

    edit_match = LAST_EDIT_RE.search(article_html)
    last_edited_at = edit_match.group(1) if edit_match else None

    bb_html = extract_balanced_div(article_html, '<div class="bbWrapper">')
    if bb_html is None:
        bb_html = article_html

    bb_parser = BBWrapperParser(base_url=base_url)
    bb_parser.feed(bb_html)

    return ForumPost(
        post_id=post_id,
        post_number=post_number,
        permalink=permalink,
        author=author,
        user_title=user_title,
        user_banners=banners,
        published_at=published_at,
        last_edited_at=last_edited_at,
        text=bb_parser.get_clean_text(),
        links=bb_parser.links,
        media=bb_parser.media,
    )


def parse_thread_html(html: str, source: str, base_url: str = FORUM_ORIGIN) -> ThreadPageResult:
    h1_match = H1_TITLE_RE.search(html)
    prefix = None
    title = "Тема форума"
    if h1_match:
        raw_h1 = h1_match.group(1)
        label_match = LABEL_RE.search(raw_h1)
        if label_match:
            prefix = clean_html_text(label_match.group(1))
            raw_h1 = raw_h1.replace(label_match.group(0), "")
        title = clean_html_text(raw_h1)

    breadcrumbs: list[dict[str, str]] = []
    bc_match = BREADCRUMB_BLOCK_RE.search(html)
    if bc_match:
        seen_bc: set[str] = set()
        for href, raw_t in BREADCRUMB_LINK_RE.findall(bc_match.group(1)):
            t = clean_html_text(raw_t)
            u = urljoin(base_url, unescape(href))
            if t and u not in seen_bc:
                seen_bc.add(u)
                breadcrumbs.append({"title": t, "url": u})

    page_numbers = [int(n) for n in PAGE_NUM_RE.findall(html)]
    total_pages = max(page_numbers, default=1)
    current_match = CURRENT_PAGE_RE.search(html)
    current_page = int(current_match.group(1)) if current_match else 1
    next_match = NEXT_PAGE_RE.search(html)
    next_page_url = urljoin(base_url, unescape(next_match.group(1))) if next_match else None

    starts = [m.start() for m in ARTICLE_START_RE.finditer(html)]
    posts: list[ForumPost] = []
    for idx, start in enumerate(starts):
        end = starts[idx + 1] if idx + 1 < len(starts) else len(html)
        article_chunk = html[start:end]
        end_article = article_chunk.find("</article>")
        if end_article != -1:
            article_chunk = article_chunk[: end_article + len("</article>")]
        posts.append(parse_single_post(article_chunk, base_url=base_url, fallback_index=idx + 1))

    return ThreadPageResult(
        source=source,
        title=title,
        prefix=prefix,
        current_page=current_page,
        total_pages=total_pages,
        next_page_url=next_page_url,
        breadcrumbs=breadcrumbs,
        posts=posts,
    )


def format_markdown(result: ThreadPageResult) -> str:
    lines: list[str] = []
    prefix_str = f"[{result.prefix}] " if result.prefix else ""
    lines.append(f"# {prefix_str}{result.title}")
    lines.append(f"- **Источник**: {result.source}")
    lines.append(f"- **Страница**: {result.current_page} из {result.total_pages}")
    if result.next_page_url:
        lines.append(f"- **Следующая страница**: {result.next_page_url}")
    if result.breadcrumbs:
        crumbs = " → ".join(f"[{b['title']}]({b['url']})" for b in result.breadcrumbs)
        lines.append(f"- **Навигация**: {crumbs}")

    lines.append(f"\n---\n## Сообщения на странице ({len(result.posts)})")
    for post in result.posts:
        role_parts = [p for p in [post.user_title, *post.user_banners] if p]
        role_str = f" ({', '.join(role_parts)})" if role_parts else ""
        lines.append(
            f"\n### Пост #{post.post_number} — {post.author}{role_str}"
        )
        lines.append(
            f"- **ID поста**: `{post.post_id}` | **Опубликовано**: `{post.published_at or '—'}`"
            + (f" | **Отредактировано**: `{post.last_edited_at}`" if post.last_edited_at else "")
        )
        lines.append(f"- **Ссылка**: {post.permalink}")
        lines.append("\n#### Текст сообщения:")
        lines.append(post.text or "_Пустое сообщение_")

        if post.links:
            lines.append(f"\n#### Гиперссылки в посте ({len(post.links)}):")
            for link in post.links:
                norm_note = (
                    f" → прямой/экспорт URL: `{link.normalized_media_url}`"
                    if link.normalized_media_url
                    else ""
                )
                lines.append(
                    f"- **[{link.category}]** `{link.anchor}`: {link.url}{norm_note}"
                )

        if post.media:
            lines.append(f"\n#### Встроенные медиа и изображения ({len(post.media)}):")
            for m in post.media:
                alt_note = f" (alt: `{m.alt}`)" if m.alt else ""
                lines.append(f"- **[{m.media_type}]** {m.url}{alt_note}")

        lines.append("\n---")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Извлечение постов, спойлеров, ссылок и медиа из темы форума GTA 5 RP"
    )
    parser.add_argument("url", nargs="?", help="URL темы форума")
    parser.add_argument("--file", "-f", help="Путь к локальному HTML-файлу темы")
    parser.add_argument("--cookie", "-c", help="Значение cookie xf_user (или через GTA5RP_XF_USER)")
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
        html = fetch_url(args.url, cookie=args.cookie)
        source = args.url
        base_url = args.url

    result = parse_thread_html(html, source=source, base_url=base_url)
    if args.json:
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    else:
        print(format_markdown(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
