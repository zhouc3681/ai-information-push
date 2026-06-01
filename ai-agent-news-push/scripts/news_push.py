#!/usr/bin/env python3
"""AI / Agent 资讯推送工具 —— CLI 入口与四阶段编排。

四阶段：采集(sources) → 关键词预过滤 → 去重(store) → AI 处理(processor) → 推送(pushers)

用法：
    python news_push.py --config config.yaml --dry-run   # 跑全流程但只在终端打印，不推送
    python news_push.py --config config.yaml             # 真正推送到已启用渠道
"""
from __future__ import annotations

import argparse
import sys
from typing import Any

try:
    import yaml
except ImportError:
    print("缺少 PyYAML，请先 pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)

import pushers
import sources
import store
from processor import process_items


def load_config(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def keyword_filter(items: list[dict[str, Any]], cfg: dict[str, Any]) -> list[dict[str, Any]]:
    inc = [k.lower() for k in (cfg.get("keywords_include") or [])]
    exc = [k.lower() for k in (cfg.get("keywords_exclude") or [])]
    out = []
    for it in items:
        blob = f"{it.get('title','')} {it.get('summary','')}".lower()
        if exc and any(k in blob for k in exc):
            continue
        if inc and not any(k in blob for k in inc):
            continue
        out.append(it)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="AI/Agent 资讯智能推送工具")
    ap.add_argument("--config", required=True, help="config.yaml 路径")
    ap.add_argument("--dry-run", action="store_true", help="只预览不推送，也不更新去重存档")
    args = ap.parse_args()

    cfg = load_config(args.config)
    delivery = cfg.get("delivery", {})
    title = delivery.get("digest_title", "AI / Agent 情报")
    max_items = int(delivery.get("max_items", 8))
    dedup_path = delivery.get("dedup_store", "./pushed.json")

    # 1. 采集
    raw = sources.gather_items(cfg.get("sources", {}))
    print(f"[main] 采集 {len(raw)} 条原始资讯", file=sys.stderr)

    # 2. 关键词预过滤
    filtered = keyword_filter(raw, cfg)
    print(f"[main] 关键词过滤后剩 {len(filtered)} 条", file=sys.stderr)

    # 3. 去重 (去掉已推送过的)
    seen = store.load_seen(dedup_path)
    fresh = store.filter_new(filtered, seen)
    print(f"[main] 去重后剩 {len(fresh)} 条新内容", file=sys.stderr)

    if not fresh:
        print("[main] 没有新内容，结束。", file=sys.stderr)
        return 0

    # 4. AI 处理 (去重合并/分类/评分/中文摘要)，取前 max_items 条
    processed = process_items(fresh, cfg.get("llm", {}), delivery)
    processed = processed[:max_items]
    if not processed:
        print("[main] 处理后无满足阈值的条目，结束。", file=sys.stderr)
        return 0

    # 5. 输出 / 推送
    if args.dry_run:
        print("\n" + pushers.render_plain(processed, title))
        print(f"\n[main] --dry-run：以上 {len(processed)} 条本应推送，但未发送，去重存档未更新。", file=sys.stderr)
        return 0

    results = pushers.push_all(processed, cfg.get("push", {}), title)
    print("\n推送结果：")
    for r in results:
        print("  " + r)

    # 仅在至少一个渠道成功时才记入去重，避免失败后内容被永久跳过
    if any("OK" in r for r in results):
        store.mark_pushed(processed, seen, dedup_path)
        print(f"[main] 已更新去重存档：{dedup_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
