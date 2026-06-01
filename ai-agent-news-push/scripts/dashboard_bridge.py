#!/usr/bin/env python3
"""把 ai-agent-news-push Skill 的真实采集结果转换成 Dashboard 数据。

这个脚本复用仓库内原有的 sources / processor / pushers / store：
采集 -> 关键词过滤 -> 去重 -> LLM 处理 -> 写 dashboard-news.json -> 可选真实推送。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime, time, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("缺少 PyYAML，请先安装依赖：python -m pip install -r ai-agent-news-push/scripts/requirements.txt", file=sys.stderr)
    raise SystemExit(1)

import requests

import pushers
import sources
import store
from news_push import keyword_filter
from processor import process_items


def resolve_redirect_urls(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """把 Google News 等聚合源的跳转链替换为原站直链。

    只在最终入选的少量条目上跑（< 20），失败保留原 URL。
    """
    REDIRECT_HOSTS = ("news.google.com",)
    headers = {"User-Agent": sources.USER_AGENT}
    for item in items:
        url = item.get("url") or ""
        if not any(host in url for host in REDIRECT_HOSTS):
            continue
        try:
            resp = requests.get(url, headers=headers, allow_redirects=True, timeout=8)
            final = resp.url
            if final and final != url and not any(host in final for host in REDIRECT_HOSTS):
                item["url"] = final
        except Exception:
            # 解析失败保留原 URL，不让网络抖动拖垮推送
            pass
    return items


def load_config(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def source_id(index: int) -> str:
    return f"live-{index + 1}"


def item_datetime(item: dict[str, Any]) -> datetime | None:
    value = item.get("published")
    if not value:
        return None
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, date):
        dt = datetime.combine(value, time.min)
    else:
        text = str(value).strip()
        try:
            dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except Exception:
            try:
                dt = parsedate_to_datetime(text)
            except Exception:
                return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone()


def filter_recent(items: list[dict[str, Any]], hours: int) -> list[dict[str, Any]]:
    if hours <= 0:
        return items
    cutoff = datetime.now().astimezone() - timedelta(hours=hours)
    recent = []
    for item in items:
        dt = item_datetime(item)
        if dt is None or dt >= cutoff:
            recent.append(item)
    return recent


def build_dashboard_payload(
    processed: list[dict[str, Any]],
    raw_count: int,
    filtered_count: int,
    recent_count: int,
    fresh_count: int,
    cfg: dict[str, Any],
    push_results: list[str] | None,
) -> dict[str, Any]:
    now = datetime.now().astimezone()
    delivery = cfg.get("delivery", {})
    dashboard_cfg = cfg.get("dashboard", {})
    title = delivery.get("digest_title", "AI / Agent 每日情报")

    source_rows = []
    brief_items = []
    trends: dict[str, list[dict[str, Any]]] = {}

    for idx, item in enumerate(processed):
        sid = source_id(idx)
        source_rows.append(
            {
                "id": sid,
                "org": item.get("source") or "未知来源",
                "product": item.get("category") or "AI / Agent",
                "date": item.get("published") or now.strftime("%Y-%m-%d"),
                "freshness": "本次采集",
                "title": item.get("zh_title") or item.get("title") or "未命名资讯",
                "type": item.get("category") or "资讯",
                "url": item.get("url") or "",
                "summary": item.get("one_liner") or item.get("summary") or "",
            }
        )
        brief_items.append(
            {
                "title": item.get("zh_title") or item.get("title") or "未命名资讯",
                "summary": item.get("one_liner") or item.get("summary") or "",
                "whyNow": "这是本次采集窗口中新出现或仍在发酵的信息，已通过关键词、去重和后台排序进入简报。",
                "action": build_action(item),
                "sourceIds": [sid],
                "importanceScore": int(item.get("value_score") or delivery.get("min_value_score", 6)),
            }
        )
        category = item.get("category") or "Thinking"
        trends.setdefault(category, []).append(item)

    trend_rows = [
        {
            "name": trend_name(category),
            "description": f"本次采集中有 {len(items)} 条相关信息进入候选，代表该方向仍值得持续观察。",
            "sourceIds": [source_id(processed.index(items[0]))] if items else [],
        }
        for category, items in trends.items()
    ][:4]

    poc_rows = [
        {
            "title": item["title"][:36],
            "reason": item["summary"][:120] or "该信息与企业 AI / Agent 落地相关。",
            "next": item["action"],
        }
        for item in brief_items[:3]
    ]

    agent_rows = [
        {
            "name": item["title"][:34],
            "type": source_rows[i]["type"],
            "description": item["summary"][:130],
            "sourceIds": item["sourceIds"],
        }
        for i, item in enumerate(brief_items[:3])
    ]

    push_steps = [
        {
            "name": "真实资讯采集 Skill",
            "status": "已完成",
            "description": f"采集 {raw_count} 条，关键词过滤后 {filtered_count} 条。"
        },
        {
            "name": "实时窗口过滤 Skill",
            "status": "已完成",
            "description": f"按最近时间窗口保留 {recent_count} 条候选。"
        },
        {
            "name": "去重与排序 Skill",
            "status": "已完成",
            "description": f"去重后 {fresh_count} 条，进入简报 {len(processed)} 条。"
        },
        {
            "name": "渠道适配 Skill",
            "status": "已完成",
            "description": "已生成 Dashboard 数据、邮件正文、企业微信/飞书文案。"
        },
        {
            "name": "企业微信 / 飞书 / 邮件推送 Skill",
            "status": "已完成" if push_results else "待推送",
            "description": "；".join(push_results or ["当前为预览模式，未向真实渠道发送。"])
        },
    ]

    workflow_rows = [
        {
            "name": "定时采集",
            "count": f"{raw_count} 条",
            "rate": "已完成",
            "description": "从 RSS 和 Hacker News 等来源采集真实资讯。"
        },
        {
            "name": "关键词过滤",
            "count": f"{filtered_count} 条",
            "rate": "已完成",
            "description": "先过滤出 AI / Agent / 企业应用相关候选，降低无关信息。"
        },
        {
            "name": "实时窗口过滤",
            "count": f"{recent_count} 条",
            "rate": "已完成",
            "description": "只保留最近时间窗口内的新变化，避免日报长期显示旧资讯。"
        },
        {
            "name": "去重存档",
            "count": f"{fresh_count} 条",
            "rate": "已完成",
            "description": "基于 URL 哈希过滤已推送内容。"
        },
        {
            "name": "LLM 处理",
            "count": f"{len(processed)} 条",
            "rate": "已完成",
            "description": "完成合并、分类、后台评分和中文摘要。"
        },
        {
            "name": "Dashboard 输出",
            "count": "1 份 JSON",
            "rate": "已完成",
            "description": "前端页面会优先读取 data/dashboard-news.json。"
        },
    ]

    return {
        "meta": {
            "dateLabel": now.strftime("%Y-%m-%d"),
            "generatedAt": now.strftime("%H:%M"),
            "windowLabel": dashboard_cfg.get("window_label", "最近一次真实采集"),
            "nextRun": dashboard_cfg.get("next_run", "明日 09:00"),
            "digestTitle": title,
            "rawCount": raw_count,
            "filteredCount": filtered_count,
            "recentCount": recent_count,
            "freshCount": fresh_count,
            "pushed": bool(push_results),
        },
        "sources": source_rows,
        "briefItems": brief_items,
        "trends": trend_rows,
        "pocItems": poc_rows,
        "agentItems": agent_rows,
        "pushSkillSteps": push_steps,
        "workflowSteps": workflow_rows,
        "digestText": pushers.render_markdown(processed, title),
    }


def build_action(item: dict[str, Any]) -> str:
    category = item.get("category", "")
    if category == "Research":
        return "建议研究或技术团队阅读原文，判断是否可转化为内部评测或 PoC 指标。"
    if category == "Tool Mastery":
        return "建议技术团队核验接口、工具调用和权限边界，必要时加入技术选型清单。"
    if category == "Workflow Mastery":
        return "建议产品和业务团队评估是否适合进入内部流程自动化 PoC。"
    if category == "Funding":
        return "建议关注其商业化方向、客户行业和可对标的企业应用场景。"
    return "建议纳入本周 AI / Agent 观察清单，结合企业场景进一步判断价值。"


def trend_name(category: str) -> str:
    names = {
        "Tool Mastery": "工具与接口更新",
        "Workflow Mastery": "企业工作流落地",
        "Thinking": "行业判断与趋势",
        "Funding": "融资与商业化",
        "Research": "研究与评测",
    }
    return names.get(category, category)


def write_json(path: str, payload: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    js_target = target.with_suffix(".js")
    with js_target.open("w", encoding="utf-8") as f:
        f.write("window.AI_NEWS_PUSH_DATA = ")
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write(";\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="生成 AI 情报雷达 Dashboard 数据，并可选真实推送。")
    parser.add_argument("--config", required=True, help="配置文件路径")
    parser.add_argument("--dry-run", action="store_true", help="只生成 Dashboard 数据，不推送、不更新去重存档")
    parser.add_argument("--push", action="store_true", help="真实推送到已启用渠道，并更新去重存档")
    args = parser.parse_args()

    cfg = load_config(args.config)
    delivery = cfg.get("delivery", {})
    title = delivery.get("digest_title", "AI / Agent 情报")
    output = cfg.get("dashboard", {}).get("output", "./data/dashboard-news.json")
    dedup_path = delivery.get("dedup_store", "./data/pushed.json")

    raw = sources.gather_items(cfg.get("sources", {}))
    filtered = keyword_filter(raw, cfg)
    recent_hours = int(delivery.get("recent_hours", 0))
    recent = filter_recent(filtered, recent_hours)
    seen = store.load_seen(dedup_path)
    fresh = store.filter_new(recent, seen)

    if fresh:
        processed = process_items(fresh, cfg.get("llm", {}), delivery)
        processed = processed[: int(delivery.get("max_items", 8))]
        processed = resolve_redirect_urls(processed)
    else:
        processed = []

    push_results = None
    if args.push and processed:
        push_results = pushers.push_all(processed, cfg.get("push", {}), title)
        if any("OK" in result for result in push_results):
            store.mark_pushed(processed, seen, dedup_path)

    payload = build_dashboard_payload(
        processed=processed,
        raw_count=len(raw),
        filtered_count=len(filtered),
        recent_count=len(recent),
        fresh_count=len(fresh),
        cfg=cfg,
        push_results=push_results,
    )
    write_json(output, payload)

    print(f"已生成 Dashboard 数据：{output}")
    print(f"采集 {len(raw)} 条，过滤 {len(filtered)} 条，实时窗口 {len(recent)} 条，新内容 {len(fresh)} 条，入选 {len(processed)} 条。")
    if args.dry_run:
        print("当前为 dry-run，未推送、未更新去重存档。")
    elif args.push:
        print("推送结果：")
        for result in push_results or ["没有可推送内容"]:
            print("  " + result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
