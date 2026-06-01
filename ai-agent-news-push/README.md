# ai-agent-news-push

低代码、配置驱动的小工具：把**企业级 AI / Agent 资讯**自动推送到**飞书 / 企业微信 / 钉钉 / 邮件**。

编辑一个 `config.yaml`，运行一条命令即可。同时作为 [Claude Code Skill](https://docs.claude.com/en/docs/claude-code/skills) 使用 —— 让 Claude 帮你搭建、配置、运行和扩展。

## 它做什么

```
采集               过滤/去重           AI 处理                      推送
RSS + Hacker News → 关键词 + JSON 去重 → LLM 去重合并/分类/        → 飞书 / 企业微信
                                          价值评分(1-10)/中文摘要      钉钉 / 邮件
```

- **多源采集**：任意 RSS（大厂博客、Agent 框架、GitHub Releases、arXiv、中文媒体…）+ Hacker News。
- **关键词过滤 + 去重**：本地 JSON 存档记录已推送条目，不重复刷屏。
- **AI 富集**：调用 OpenAI 兼容接口对内容去重合并、分类(Tool Mastery / Workflow Mastery / Thinking / Funding / Research)、打价值分、生成中文摘要。
- **多渠道推送**：飞书互动卡片、企业微信 markdown、钉钉(支持加签)、SMTP 邮件。
- **优雅降级**：LLM 调用失败时自动回退为原始条目，不中断推送。

## 快速开始

```bash
pip install -r scripts/requirements.txt

# 1. 复制示例配置并按需修改
cp assets/config.example.yaml config.yaml

# 2. 先预览（不真正发送）
python scripts/news_push.py --config config.yaml --dry-run

# 3. 正式推送
python scripts/news_push.py --config config.yaml
```

## 配置（config.yaml）

| 区块 | 作用 |
|------|------|
| `llm` | OpenAI 兼容接口（base_url / api_key / model），用于分类、评分、中文摘要 |
| `keywords_include` / `keywords_exclude` | 关键词过滤白/黑名单 |
| `sources.rss` | RSS 源列表，一行一个 `{name, url}` |
| `sources.hackernews` | Hacker News 抓取（最低分数 + 关键词） |
| `push.{feishu,wechat_work,dingtalk,email}` | 各渠道开关 + Webhook / 密钥 |
| `delivery` | 推送条数、最低价值分、去重存档路径、标题、摘要风格 |

各平台 Webhook 获取与签名方式见 [`references/setup-webhooks.md`](references/setup-webhooks.md)；可选数据源清单见 [`references/sources-catalog.md`](references/sources-catalog.md)。

## 定时运行（cron 示例：每天早 9 点）

```cron
0 9 * * * cd /path/to/ai-agent-news-push && python scripts/news_push.py --config config.yaml >> push.log 2>&1
```

## 目录结构

```
SKILL.md                      # Claude Code skill 入口
assets/config.example.yaml    # 配置模板（唯一需要编辑的文件）
scripts/
  news_push.py                # CLI 编排入口
  sources.py                  # 采集层（RSS / Hacker News）
  processor.py                # LLM 处理层（分类/评分/摘要/去重合并）
  pushers.py                  # 推送层（飞书/企业微信/钉钉/邮件）
  store.py                    # JSON 去重存档
references/                   # Webhook 配置 & 数据源清单
```

## 备注

- 企业微信群机器人无需「加签」，`secret` 留空即可；钉钉若开启「加签」需填 `secret`。
- 企业微信单机器人每分钟最多 20 条、单条 markdown 约 4096 字节（工具已自动截断）。
- `config.yaml` 与 `pushed.json` 已在 `.gitignore` 中，避免把真实 Webhook / 密钥提交到仓库。
