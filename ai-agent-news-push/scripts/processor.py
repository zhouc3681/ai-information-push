"""AI 处理层：一次批量调用大模型，完成 去重合并 / 分类 / 价值度评分 / 中文摘要。

设计要点：把所有候选条目放进一个请求里，让模型横向比较，从而能合并重复事件
(同一条 Claude 发布被 5 家媒体报道) 并相对排序；同时比逐条调用省大量 token。

输出在原 Item 上追加：
    category     : Tool Mastery / Workflow Mastery / Thinking / Funding / Research
    value_score  : 1-10
    zh_title     : 中文标题
    one_liner    : 一句话结论
    highlights   : [核心看点, ...] (保留专业术语英文)
    merged_urls  : [被合并的其它原文链接, ...]

若模型调用失败或返回无法解析，降级为返回原始条目 (用原标题/摘要)，
确保「降级简报」也好过「静默失败」。
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any

import requests

CATEGORIES = ["Tool Mastery", "Workflow Mastery", "Thinking", "Funding", "Research"]


def _log(msg: str) -> None:
    print(f"[processor] {msg}", file=sys.stderr)


def _resolve_llm(cfg: dict[str, Any]) -> tuple[str, str, str]:
    """返回 (base_url, api_key, model)。优先用写死值，否则读环境变量。"""
    model = cfg.get("model", "anthropic/claude-haiku-4.5")
    base_url = cfg.get("base_url")
    api_key = cfg.get("api_key")
    if not base_url:
        env_name = cfg.get("base_url_env", "AI_GATEWAY_BASE_URL")
        base_url = os.environ.get(env_name, "")
        base_url += cfg.get("base_url_suffix", "/api/v1")
    if not api_key:
        api_key = os.environ.get(cfg.get("api_key_env", "AI_GATEWAY_API_KEY"), "")
    return base_url.rstrip("/"), api_key, model


def _build_prompt(items: list[dict[str, Any]], style: str, min_score: int) -> str:
    lines = []
    for i, it in enumerate(items):
        lines.append(
            f"[{i}] 来源:{it['source']} | 标题:{it['title']} | 摘要:{it.get('summary','')[:300]} | 链接:{it['url']}"
        )
    catalog = " / ".join(CATEGORIES)
    return f"""你是企业级 AI/Agent 情报分析师。下面是若干条原始资讯，请处理后输出 JSON。

要求：
1. 合并重复事件：若多条讲同一件事，合并为一条，主链接取信息最全的，其余放入 merged_urls。
2. 分类 category 必须是以下之一：{catalog}
3. value_score 1-10：对「企业 AI/Agent 决策者与从业者」的价值，低于 {min_score} 分的可不输出。
4. 为每条写：zh_title(中文标题)、one_liner(一句话结论)、highlights(2-3 条核心看点，保留专业术语英文对照)。
5. 摘要风格：{style}

只输出一个 JSON 对象，格式：
{{"items":[{{"source_index":0,"category":"...","value_score":8,"zh_title":"...","one_liner":"...","highlights":["...","..."],"merged_urls":["..."]}}]}}

原始资讯：
{chr(10).join(lines)}
"""


def _prefilter(items: list[dict[str, Any]], cap: int) -> list[dict[str, Any]]:
    """LLM 调用前先粗筛到 cap 条，避免一次塞太多导致返回 JSON 截断/超时。

    启发式：按发布时间倒序（新→旧）取前 cap 条；无时间的排在后面。
    这样既限制 prompt 体积，又优先保留最新资讯。
    """
    if cap <= 0 or len(items) <= cap:
        return items
    indexed = list(enumerate(items))
    indexed.sort(key=lambda p: (_published_sort_value(p[1].get("published")), -p[0]), reverse=True)
    kept = [it for _, it in indexed[:cap]]
    _log(f"LLM 前粗筛：{len(items)} → {len(kept)} 条 (cap={cap})")
    return kept


def _chunk(seq: list[Any], size: int) -> list[list[Any]]:
    if size <= 0:
        return [seq]
    return [seq[i : i + size] for i in range(0, len(seq), size)]


def _published_sort_value(value: Any) -> float:
    if not value:
        return 0.0
    from datetime import date, datetime, time, timezone
    from email.utils import parsedate_to_datetime

    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, date):
        dt = datetime.combine(value, time.min)
    else:
        text = str(value)
        try:
            dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except Exception:
            try:
                dt = parsedate_to_datetime(text)
            except Exception:
                return 0.0
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.timestamp()


def _call_llm(
    prompt: str, base_url: str, api_key: str, model: str, max_tokens: int
) -> dict[str, Any]:
    resp = requests.post(
        f"{base_url}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            # 请求未压缩响应：本环境网关声明的 content-encoding 与实际 body 不符，
            # 用 identity 可绕过 requests 的解压报错。
            "Accept-Encoding": "identity",
        },
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            # 必须显式设置：网关默认输出额度很低，批量富集结果会被截断 (finish=length)，
            # 导致 JSON 被从中间切断而解析失败。给足额度让单批输出完整。
            "max_tokens": max_tokens,
        },
        timeout=120,
    )
    resp.raise_for_status()
    choice = resp.json()["choices"][0]
    content = choice["message"]["content"]
    if choice.get("finish_reason") == "length":
        # 仍被截断说明单批条目过多/摘要过长，提示调小 llm_batch_size 或调大 max_tokens。
        _log("警告：输出因 max_tokens 截断，建议调小 llm_batch_size 或调大 llm.max_tokens。")
    return _extract_json(content)


def process_items(
    items: list[dict[str, Any]], llm_cfg: dict[str, Any], delivery_cfg: dict[str, Any]
) -> list[dict[str, Any]]:
    """主入口。返回带结构化字段、已按 value_score 降序、已过滤低分的条目。

    分批调用 LLM：先粗筛到 llm_max_candidates 条，再按 llm_batch_size 切块逐批处理。
    单批失败仅该批降级，不影响其它批；全部失败才整体降级。
    """
    if not items:
        return []
    min_score = int(delivery_cfg.get("min_value_score", 6))
    style = delivery_cfg.get("summary_style", "去粗取精，保留专业术语英文对照。")
    cap = int(delivery_cfg.get("llm_max_candidates", 60))
    batch_size = int(delivery_cfg.get("llm_batch_size", 12))
    max_tokens = int(llm_cfg.get("max_tokens", 4096))
    base_url, api_key, model = _resolve_llm(llm_cfg)

    if not base_url or not api_key:
        _log("未找到 LLM base_url/api_key，按时间粗筛后降级为原始条目。")
        return _fallback(_prefilter(items, cap), min_score)

    candidates = _prefilter(items, cap)
    batches = _chunk(candidates, batch_size)
    enriched: list[dict[str, Any]] = []
    failed_batches = 0
    for bi, batch in enumerate(batches):
        prompt = _build_prompt(batch, style, min_score)
        try:
            parsed = _call_llm(prompt, base_url, api_key, model, max_tokens)
            enriched.extend(_merge_back(batch, parsed.get("items", []), min_score))
        except Exception as exc:
            failed_batches += 1
            _log(f"第 {bi + 1}/{len(batches)} 批 LLM 失败({exc})，该批降级。")
            enriched.extend(_fallback(batch, min_score))

    if failed_batches == len(batches):
        _log("全部批次失败，整体降级为原始条目。")
        return _fallback(candidates, min_score)
    if not enriched:
        _log("模型返回为空，降级为原始条目。")
        return _fallback(candidates, min_score)
    enriched.sort(key=lambda x: x.get("value_score", 0), reverse=True)
    _log(
        f"模型处理后保留 {len(enriched)} 条"
        f"（{len(batches)} 批，失败 {failed_batches} 批）"
    )
    return enriched


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        text = text[start : end + 1]
    return json.loads(text)


def _merge_back(
    items: list[dict[str, Any]], processed: list[dict[str, Any]], min_score: int
) -> list[dict[str, Any]]:
    out = []
    for p in processed:
        idx = p.get("source_index")
        if idx is None or not (0 <= idx < len(items)):
            continue
        score = int(p.get("value_score", 0))
        if score < min_score:
            continue
        base = dict(items[idx])
        base.update(
            {
                "category": p.get("category", "Thinking"),
                "value_score": score,
                "zh_title": p.get("zh_title") or base["title"],
                "one_liner": p.get("one_liner", ""),
                "highlights": p.get("highlights", []) or [],
                "merged_urls": p.get("merged_urls", []) or [],
            }
        )
        out.append(base)
    return out


def _fallback(items: list[dict[str, Any]], min_score: int) -> list[dict[str, Any]]:
    """无 LLM 时的降级：原样输出，给中性默认值。"""
    out = []
    for it in items:
        base = dict(it)
        base.update(
            {
                "category": "Thinking",
                "value_score": min_score,
                "zh_title": it["title"],
                "one_liner": it.get("summary", "")[:120],
                "highlights": [],
                "merged_urls": [],
            }
        )
        out.append(base)
    return out
