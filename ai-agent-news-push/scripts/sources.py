"""数据采集层：把各种来源抓成统一的 Item 结构。

Item = {
    "title":     str,   # 原始标题
    "url":       str,   # 原文链接 (用于去重 + 跳转)
    "source":    str,   # 来源名 (如 "Anthropic News")
    "summary":   str,   # 原文摘要/正文片段 (可能为空)
    "published": str,   # 发布时间字符串 (可能为空)
}

新增数据源 = 写一个 fetch_<x>(cfg) -> list[Item]，然后在 gather_items 里注册。
核心原则：单个源失败必须被吞掉 (打日志 + 返回 [])，绝不能让一个挂掉的源拖垮整次运行。
"""
from __future__ import annotations

import sys
from typing import Any

try:
    import feedparser
except ImportError:  # pragma: no cover
    feedparser = None

import requests

# 真实 Chrome UA: 一些站点 (Aliyun WAF / Cloudflare / Substack)
# 会拦截短 UA 或 python-requests/feedparser 的默认 UA.
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


def _log(msg: str) -> None:
    print(f"[sources] {msg}", file=sys.stderr)


def fetch_rss(feeds: list[dict[str, str]]) -> list[dict[str, Any]]:
    """抓取一组 RSS 源。feeds = [{name, url}, ...]"""
    if feedparser is None:
        _log("feedparser 未安装，跳过 RSS。请先 pip install feedparser")
        return []
    items: list[dict[str, Any]] = []
    for feed in feeds:
        name = feed.get("name", feed.get("url", "RSS"))
        url = feed.get("url")
        if not url:
            continue
        try:
            parsed = feedparser.parse(url, agent=USER_AGENT)
            for entry in parsed.entries:
                items.append(
                    {
                        "title": (entry.get("title") or "").strip(),
                        "url": entry.get("link") or "",
                        "source": name,
                        "summary": _clean(entry.get("summary") or entry.get("description") or ""),
                        "published": entry.get("published") or entry.get("updated") or "",
                    }
                )
            _log(f"RSS [{name}] 抓到 {len(parsed.entries)} 条")
        except Exception as exc:  # 单源失败不影响整体
            _log(f"RSS [{name}] 抓取失败: {exc}")
    return items


def fetch_hackernews(cfg: dict[str, Any]) -> list[dict[str, Any]]:
    """抓取 Hacker News 头条中得分达标且命中关键词的帖子。"""
    if not cfg.get("enabled"):
        return []
    min_score = int(cfg.get("min_score", 100))
    keywords = [k.lower() for k in cfg.get("keywords", [])]
    items: list[dict[str, Any]] = []
    try:
        top = requests.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json", timeout=15
        ).json()
        # 只看前 ~120 条头条，避免过多请求
        for story_id in top[:120]:
            try:
                story = requests.get(
                    f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json",
                    timeout=10,
                ).json()
            except Exception:
                continue
            if not story or story.get("type") != "story":
                continue
            score = story.get("score", 0)
            title = story.get("title", "")
            if score < min_score:
                continue
            if keywords and not any(k in title.lower() for k in keywords):
                continue
            items.append(
                {
                    "title": title.strip(),
                    "url": story.get("url")
                    or f"https://news.ycombinator.com/item?id={story_id}",
                    "source": f"Hacker News ({score} pts)",
                    "summary": "",
                    "published": "",
                }
            )
        _log(f"Hacker News 命中 {len(items)} 条 (min_score={min_score})")
    except Exception as exc:
        _log(f"Hacker News 抓取失败: {exc}")
    return items


def fetch_pages(pages: list[dict[str, str]]) -> list[dict[str, Any]]:
    """抓取一组指定网页的标题和 meta description。

    用于没有 RSS 的高价值官方页面、发布说明或研究报告入口。
    """
    items: list[dict[str, Any]] = []
    for page in pages:
        name = page.get("name", page.get("url", "Page"))
        url = page.get("url")
        if not url:
            continue
        try:
            resp = requests.get(url, timeout=20, headers={"User-Agent": USER_AGENT})
            resp.raise_for_status()
            html = resp.text
            title = _extract_tag(html, "title") or page.get("title") or name
            summary = _extract_meta_description(html) or page.get("summary") or ""
            items.append(
                {
                    "title": _clean(title),
                    "url": url,
                    "source": name,
                    "summary": _clean(summary),
                    "published": page.get("published", ""),
                }
            )
            _log(f"Page [{name}] 抓取成功")
        except Exception as exc:
            _log(f"Page [{name}] 抓取失败: {exc}")
            if page.get("summary"):
                items.append(
                    {
                        "title": page.get("title") or name,
                        "url": url,
                        "source": name,
                        "summary": page.get("summary", ""),
                        "published": str(page.get("published", "")),
                    }
                )
                _log(f"Page [{name}] 使用配置摘要作为降级来源")
    return items


def gather_items(sources_cfg: dict[str, Any]) -> list[dict[str, Any]]:
    """汇总所有已配置数据源。新增源在此注册即可。"""
    items: list[dict[str, Any]] = []
    items += fetch_pages(sources_cfg.get("pages", []) or [])
    items += fetch_rss(sources_cfg.get("rss", []) or [])
    items += fetch_hackernews(sources_cfg.get("hackernews", {}) or {})
    # 去掉没有链接的脏数据
    items = [it for it in items if it.get("url")]
    return items


def _clean(html: str) -> str:
    """非常轻量的去标签，避免摘要里塞满 HTML。"""
    import re

    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:600]


def _extract_tag(html: str, tag: str) -> str:
    import re

    match = re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", html, flags=re.I | re.S)
    return match.group(1).strip() if match else ""


def _extract_meta_description(html: str) -> str:
    import re

    patterns = [
        r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']',
        r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\'](.*?)["\']',
        r'<meta[^>]+content=["\'](.*?)["\'][^>]+name=["\']description["\']',
        r'<meta[^>]+content=["\'](.*?)["\'][^>]+property=["\']og:description["\']',
    ]
    for pattern in patterns:
        match = re.search(pattern, html, flags=re.I | re.S)
        if match:
            return match.group(1).strip()
    return ""
