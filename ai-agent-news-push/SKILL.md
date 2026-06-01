---
name: ai-agent-news-push
description: >-
  Build and run a low-code tool that aggregates enterprise AI / AI-Agent news
  (funding, model/product launches, GitHub & Hacker News, papers, newsletters)
  from RSS and other sources, then uses an LLM to dedupe, classify, score, and
  write Chinese bilingual summaries, and pushes a digest card to Feishu (飞书),
  WeChat Work (企业微信), DingTalk, or email bots. Use this skill whenever the
  user wants to set up, configure, schedule, or run automated news / 资讯 /
  情报 pushes to 飞书 / 企业微信 / 钉钉 group robots — especially for AI, Agent,
  LLM, 大模型, 融资, or any vertical-domain information feed. Trigger it even if
  the user just says "推送资讯到飞书/企业微信", "做个AI快讯机器人", "build a news
  bot", or "聚合AI新闻定时推送", without naming this tool explicitly.
---

# AI / Agent 资讯智能推送工具（低代码）

This skill ships a **config-driven Python tool** that turns "搭一个把 AI/Agent 资讯定时推送到飞书/企业微信的小工具" into editing one YAML file and running one command. The user should almost never need to write code — the whole behavior (sources, keywords, LLM model, push channels, frequency) lives in `config.yaml`.

The pipeline mirrors a four-stage flow: **采集 (ingest) → AI 处理 (dedupe / classify / score / 中文摘要) → 推送 (push) → 去重存档 (dedup store)**. Keeping these stages decoupled is what makes the tool easy to extend — a new source is just another fetcher, a new channel is just another pusher.

## When you are invoked

Figure out which situation you're in and act accordingly:

1. **"帮我搭/做一个推送工具"** → Set up the tool: copy `assets/config.example.yaml` into the user's workspace as `config.yaml`, walk them through filling in the webhook URL(s) and picking sources, then do a dry-run.
2. **"我已经配好了，跑一下 / 测试一下"** → Run the tool (dry-run first, then live push).
3. **"加一个数据源 / 加一个推送渠道 / 改一下摘要格式"** → Extend the tool by editing the relevant module (see Architecture below). Prefer small, surgical edits.
4. **"让它每天早上自动推"** → Help set up scheduling (cron, or suggest an `<automation />` if the host supports it).

Always start by reading the user's existing `config.yaml` if one exists, so you build on their setup rather than overwriting it.

## Quick start (the happy path)

```bash
# 1. Copy the bundled tool + config into the user's workspace
cp -r <skill-dir>/scripts ./ai_news_push
cp <skill-dir>/assets/config.example.yaml ./config.yaml

# 2. Install deps (only feedparser, requests, pyyaml)
pip install -r ./ai_news_push/requirements.txt

# 3. Edit config.yaml — at minimum fill in one push webhook (see references/setup-webhooks.md)

# 4. Dry run: fetch + summarize, print the digest to the terminal, DO NOT push
python ./ai_news_push/news_push.py --config ./config.yaml --dry-run

# 5. Live run: actually push to the configured bots
python ./ai_news_push/news_push.py --config ./config.yaml
```

`--dry-run` is the single most important habit: it exercises the full ingest + LLM pipeline and prints exactly what *would* be pushed, without spamming a real group. Always dry-run before the first live push and after any config change.

## How the config works (this is the "low-code" surface)

`config.yaml` is the only file most users touch. The full annotated template lives in `assets/config.example.yaml`; the key sections:

- **`llm`** — defaults to the environment's built-in AI gateway (reads `AI_GATEWAY_BASE_URL` / `AI_GATEWAY_API_KEY`, OpenAI-compatible). The user can override with their own `base_url` + `api_key` for OpenAI/any compatible provider. Pick a cheap fast model (e.g. `anthropic/claude-haiku-4.5`) for summarization to keep cost down.
- **`sources`** — `rss` is a list of `{name, url}`; `hackernews` filters by score + keywords. Adding a feed = adding one line. A curated starter list of high-quality AI/Agent RSS feeds is in `references/sources-catalog.md` — offer these when the user hasn't picked sources.
- **`keywords_include` / `keywords_exclude`** — cheap pre-filter applied *before* the LLM, so you don't pay tokens to summarize irrelevant items. Leave `keywords_include` empty to keep everything.
- **`push`** — one block per channel (`feishu`, `wechat_work`, `dingtalk`, `email`), each with `enabled` + its webhook/credentials. Multiple channels can be on at once.
- **`delivery`** — `max_items`, `min_value_score` (LLM 价值度评分阈值 1-10), `dedup_store` path, digest title, and `summary_style`.

## Architecture (read this before extending)

The tool is intentionally split into small modules under `scripts/` so each stage can change independently:

| File | Responsibility | Extend it when… |
| :--- | :--- | :--- |
| `news_push.py` | CLI entry + orchestration of the 4 stages | rarely; only to change the overall flow |
| `sources.py` | Fetchers: RSS, Hacker News → normalized `Item` dicts | adding a new data source |
| `processor.py` | One batched LLM call: dedupe + classify + score + 中文摘要 → structured items | changing summary format, categories, or scoring |
| `pushers.py` | Channel adapters: Feishu / WeChat Work / DingTalk / email card builders + send | adding a push channel |
| `store.py` | JSON-file dedup store (URL hashes already pushed) | changing dedup strategy |

A normalized `Item` flowing through the pipeline looks like:
`{"title", "url", "source", "summary", "published"}`. After `processor.py` it gains
`{"category", "value_score", "zh_title", "one_liner", "highlights": [...], "merged_urls": [...]}`.

**To add a source**: write a `fetch_<x>(cfg) -> list[Item]` in `sources.py` and register it in `gather_items`. Keep network failures non-fatal (log + return `[]`) — one dead feed must never break the whole run.

**To add a channel**: write a `push_<x>(items, cfg)` in `pushers.py` that builds that platform's card/markdown payload and POSTs the webhook, then register it in `push_all`. Reference the platform's webhook card spec in `references/setup-webhooks.md`.

## AI processing details

`processor.py` sends all keyword-filtered, not-yet-pushed candidates to the LLM in **one batched call** and asks for structured JSON back. This single-call design is deliberate: it lets the model see all items together so it can merge duplicates (e.g. the same Claude release reported by 5 newsletters) and rank them relative to each other, while costing far fewer tokens than per-item calls.

The model is asked to, for each kept item: classify into one of **Tool Mastery / Workflow Mastery / Thinking / Funding / Research**, assign a 1-10 价值度评分, write a Chinese `one_liner` (一句话结论) plus 2-3 `highlights` (核心看点, 保留专业术语英文), and list any `merged_urls` it folded in. Items below `min_value_score` are dropped.

If the LLM call fails or returns unparseable JSON, fall back to pushing the raw keyword-filtered items with their original titles/summaries rather than pushing nothing — a degraded digest beats a silent failure. This fallback is already implemented; preserve it when editing.

## Setting up webhooks

Don't guess webhook formats. `references/setup-webhooks.md` has step-by-step instructions for getting a 飞书自定义机器人 / 企业微信群机器人 / 钉钉 webhook URL and the exact JSON card payload each platform expects (including 企业微信 markdown length limits and 飞书 interactive card structure). Read it before writing or debugging a pusher.

## Scheduling

For "每天早上推送" type requests:
- **Cron**: `0 9 * * * cd <dir> && python ai_news_push/news_push.py --config config.yaml >> push.log 2>&1`
- If the host environment supports automations, suggest one instead of cron.

Remind the user that frequency is also shaped by `delivery.max_items` and the dedup store — running hourly with a persistent store yields "only what's new since last run", which is usually what they want for 实时/早报 modes.
