#!/usr/bin/env python3
"""Fetch public RSS/newsletter items into a local JSON packet."""

from __future__ import annotations

import argparse
import email.utils
import html
import json
import re
import sys
import urllib.request
import warnings
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

try:
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL.*")
        import trafilatura
except Exception:  # pragma: no cover - optional dependency in older local envs.
    trafilatura = None


CONTENT_NS = "{http://purl.org/rss/1.0/modules/content/}"
ATOM_NS = "{http://www.w3.org/2005/Atom}"


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "svg", "iframe"}:
            self._skip_depth += 1
        if tag in {"p", "br", "li", "h1", "h2", "h3", "h4", "blockquote"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "svg", "iframe"} and self._skip_depth:
            self._skip_depth -= 1
        if tag in {"p", "li", "h1", "h2", "h3", "h4", "blockquote"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._skip_depth:
            self.parts.append(data)

    def text(self) -> str:
        return normalize_ws(" ".join(self.parts))


@dataclass
class FeedConfig:
    name: str
    url: str
    themes: list[str]


def normalize_ws(value: str) -> str:
    value = html.unescape(value or "")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def html_to_text(value: str) -> str:
    parser = TextExtractor()
    parser.feed(value or "")
    return parser.text()


def trim_text(text: str, max_chars: int) -> tuple[str, int, bool]:
    text = normalize_ws(text)
    original_chars = len(text)
    truncated = original_chars > max_chars
    if truncated:
        text = text[:max_chars].rsplit(" ", 1)[0].strip()
    return text, original_chars, truncated


def parse_datetime(value: str | None) -> str | None:
    if not value:
        return None
    try:
        dt = email.utils.parsedate_to_datetime(value)
    except (TypeError, ValueError, IndexError):
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat()


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_url(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "MorningStar-public/0.1",
            "Accept": "application/rss+xml, application/xml, text/xml;q=0.9, */*;q=0.8",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read()


def fetch_article_text(url: str, max_chars: int, timeout: int = 25) -> tuple[str | None, int, bool, str | None]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "MorningStar-public/0.1 (+article extraction)",
            "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.7",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read()
    except Exception:
        return None, 0, False, None
    html_text = raw.decode("utf-8", errors="ignore")
    if trafilatura is not None:
        extracted = trafilatura.extract(
            html_text,
            url=url,
            include_comments=False,
            include_tables=False,
            favor_precision=True,
        )
        if extracted:
            text, chars, truncated = trim_text(extracted, max_chars)
            if chars >= 400:
                return text, chars, truncated, "trafilatura"
    text, chars, truncated = trim_text(html_to_text(html_text), max_chars)
    return text, chars, truncated, "html_article"


def child_text(element: ET.Element, names: list[str]) -> str:
    for name in names:
        child = element.find(name)
        if child is not None and child.text:
            return child.text
    return ""


def parse_rss_items(feed: FeedConfig, raw_xml: bytes, max_chars: int) -> list[dict[str, Any]]:
    root = ET.fromstring(raw_xml)
    rss_items = root.findall(".//channel/item")
    atom_items = root.findall(f".//{ATOM_NS}entry")
    parsed: list[dict[str, Any]] = []

    for item in rss_items:
        title = normalize_ws(child_text(item, ["title"]))
        link = normalize_ws(child_text(item, ["link"]))
        guid = normalize_ws(child_text(item, ["guid"]))
        author = normalize_ws(child_text(item, ["{http://purl.org/dc/elements/1.1/}creator", "author"]))
        published_raw = child_text(item, ["pubDate"])
        content_html = child_text(item, [f"{CONTENT_NS}encoded", "description"])
        description = html_to_text(child_text(item, ["description"]))
        content_text = html_to_text(content_html)
        parsed.append(
            build_item(
                feed=feed,
                title=title,
                link=link or guid,
                author=author,
                published=parse_datetime(published_raw),
                description=description,
                content_text=content_text,
                max_chars=max_chars,
            )
        )

    for item in atom_items:
        title = normalize_ws(child_text(item, [f"{ATOM_NS}title"]))
        link = ""
        for link_el in item.findall(f"{ATOM_NS}link"):
            href = link_el.attrib.get("href")
            if href:
                link = href
                break
        author = normalize_ws(child_text(item, [f"{ATOM_NS}author/{ATOM_NS}name"]))
        published_raw = child_text(item, [f"{ATOM_NS}published", f"{ATOM_NS}updated"])
        content_html = child_text(item, [f"{ATOM_NS}content", f"{ATOM_NS}summary"])
        description = html_to_text(child_text(item, [f"{ATOM_NS}summary"]))
        content_text = html_to_text(content_html)
        parsed.append(
            build_item(
                feed=feed,
                title=title,
                link=link,
                author=author,
                published=parse_datetime(published_raw),
                description=description,
                content_text=content_text,
                max_chars=max_chars,
            )
        )

    return [item for item in parsed if item["link"]]


def build_item(
    feed: FeedConfig,
    title: str,
    link: str,
    author: str,
    published: str | None,
    description: str,
    content_text: str,
    max_chars: int,
) -> dict[str, Any]:
    text = content_text or description
    text, original_chars, truncated = trim_text(text, max_chars)
    return {
        "source": feed.name,
        "source_url": feed.url,
        "source_themes": feed.themes,
        "title": title,
        "link": link,
        "author": author,
        "published_at": published,
        "description": description,
        "content_text": text,
        "content_chars": original_chars,
        "content_truncated": truncated,
        "extraction_method": "feed_content",
    }


def fetch_packet(
    config_path: Path,
    state_path: Path,
    output_dir: Path,
    recent_per_feed: int | None = None,
    include_seen: bool = False,
    fetch_html: bool = True,
) -> Path:
    config = load_json(config_path, {})
    state = load_json(state_path, {"seen_links": []})
    seen_links = set(state.get("seen_links", []))
    tz = ZoneInfo(config.get("timezone", "UTC"))
    lookback_days = int(config.get("lookback_days", 2))
    max_items_per_feed = recent_per_feed or int(config.get("max_items_per_feed", 5))
    max_chars = int(config.get("max_chars_per_item", 18000))
    cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)

    items: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for feed_obj in config.get("feeds", []):
        feed = FeedConfig(
            name=feed_obj["name"],
            url=feed_obj["url"],
            themes=feed_obj.get("themes", []),
        )
        try:
            feed_items = parse_rss_items(feed, fetch_url(feed.url), max_chars=max_chars)
        except Exception as exc:  # noqa: BLE001 - packet should record feed failures.
            errors.append({"feed": feed.name, "url": feed.url, "error": str(exc)})
            continue

        selected: list[dict[str, Any]] = []
        for item in feed_items:
            if not include_seen and item["link"] in seen_links:
                continue
            published = item.get("published_at")
            if published and recent_per_feed is None:
                try:
                    published_dt = datetime.fromisoformat(published)
                except ValueError:
                    published_dt = None
                if published_dt and published_dt < cutoff:
                    continue
            if fetch_html and item["content_chars"] < 1200 and item["link"].startswith(("http://", "https://")):
                html_text, html_chars, html_truncated, method = fetch_article_text(item["link"], max_chars=max_chars)
                if html_text and html_chars > item["content_chars"]:
                    item["content_text"] = html_text
                    item["content_chars"] = html_chars
                    item["content_truncated"] = html_truncated
                    item["extraction_method"] = method or "html_article"
            selected.append(item)
            if len(selected) >= max_items_per_feed:
                break
        items.extend(selected)

    items.sort(key=lambda item: item.get("published_at") or "", reverse=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc)
    stamp = generated_at.astimezone(tz).strftime("%Y-%m-%d")
    output_path = output_dir / f"{stamp}_newsletter_items.json"
    packet = {
        "generated_at": generated_at.isoformat(),
        "display_date": stamp,
        "timezone": str(tz),
        "config_path": str(config_path),
        "state_path": str(state_path),
        "item_count": len(items),
        "items": items,
        "errors": errors,
    }
    output_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding="utf-8")
    print(output_path)
    return output_path


def mark_seen(packet_path: Path, state_path: Path) -> None:
    packet = load_json(packet_path, {})
    state = load_json(state_path, {"seen_links": []})
    seen_links = list(dict.fromkeys(state.get("seen_links", [])))
    existing = set(seen_links)
    for item in packet.get("items", []):
        link = item.get("link")
        if link and link not in existing:
            seen_links.append(link)
            existing.add(link)
    state["seen_links"] = seen_links[-1000:]
    state["last_successful_digest"] = datetime.now(timezone.utc).isoformat()
    state["updated_at"] = datetime.now(timezone.utc).isoformat()
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/feeds.json")
    parser.add_argument("--state", default="data/state.json")
    parser.add_argument("--output-dir", default="data/packets")
    parser.add_argument("--mark-seen", metavar="PACKET_JSON")
    parser.add_argument("--recent-per-feed", type=int, help="Fetch the latest N items per feed, ignoring lookback days.")
    parser.add_argument("--include-seen", action="store_true", help="Include items already present in the state file.")
    parser.add_argument("--no-html", action="store_true", help="Do not fetch article HTML for short feed entries.")
    args = parser.parse_args(argv)

    if args.mark_seen:
        mark_seen(Path(args.mark_seen), Path(args.state))
        return 0

    fetch_packet(
        Path(args.config),
        Path(args.state),
        Path(args.output_dir),
        recent_per_feed=args.recent_per_feed,
        include_seen=args.include_seen,
        fetch_html=not args.no_html,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
