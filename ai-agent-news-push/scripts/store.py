"""去重存档：用一个 JSON 文件记录已推送过的链接哈希。

这样定时运行 (如每小时/每天) 时，只会推送「上次运行以来的新内容」，
天然实现了 实时/早报 模式。换去重策略 (如改用 SQLite、按标题去重) 时只改这里。
"""
from __future__ import annotations

import hashlib
import json
import os
from typing import Any


def _hash(url: str) -> str:
    return hashlib.sha256(url.strip().encode("utf-8")).hexdigest()[:16]


def load_seen(path: str) -> set[str]:
    if not path or not os.path.exists(path):
        return set()
    try:
        with open(path, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except Exception:
        return set()


def filter_new(items: list[dict[str, Any]], seen: set[str]) -> list[dict[str, Any]]:
    """只保留 url 未推送过的条目。"""
    out = []
    for it in items:
        if _hash(it["url"]) not in seen:
            out.append(it)
    return out


def mark_pushed(items: list[dict[str, Any]], seen: set[str], path: str) -> None:
    """把本次推送的所有链接 (含被合并的 merged_urls) 记入存档。"""
    for it in items:
        seen.add(_hash(it["url"]))
        for u in it.get("merged_urls", []) or []:
            seen.add(_hash(u))
    if not path:
        return
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(sorted(seen), f)
    except Exception as exc:
        print(f"[store] 写入去重文件失败: {exc}")
