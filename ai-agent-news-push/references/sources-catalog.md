# 推荐数据源目录（企业级 AI / Agent 垂直领域）

当用户没指定来源时，从这里挑一组帮他填进 `config.yaml` 的 `sources.rss`。
RSS 地址会变动，接入前最好快速核实一下能否解析（`--dry-run` 看抓取条数即可）。

## 大厂模型与产品发布（高价值，建议默认全开）

| 来源 | RSS（如失效请到官网找 feed） |
| :--- | :--- |
| Anthropic News | https://www.anthropic.com/rss.xml |
| OpenAI Blog | https://openai.com/blog/rss.xml |
| Google AI / DeepMind | https://blog.google/technology/ai/rss/ |
| Microsoft AI Blog | https://blogs.microsoft.com/ai/feed/ |
| Meta AI | https://ai.meta.com/blog/rss/ |
| Hugging Face Blog | https://huggingface.co/blog/feed.xml |
| Mistral AI | https://mistral.ai/news/feed.xml |

## Agent 框架与平台（PM/开发者关注）

| 来源 | 说明 |
| :--- | :--- |
| LangChain Blog | https://blog.langchain.dev/rss/ |
| LlamaIndex Blog | https://www.llamaindex.ai/blog/feed |
| GitHub Releases | 用 `https://github.com/<org>/<repo>/releases.atom`，如 crewAI / langgraph / autogen |

> 提示：GitHub 任意仓库的 release/commit/tag 都有 `.atom` feed，例如
> `https://github.com/langchain-ai/langgraph/releases.atom`。把要追的开源 Agent 项目逐个加进来即可，这是追踪「框架新版本」最省事的方式。

## 社区与学术

| 来源 | 接入方式 |
| :--- | :--- |
| Hacker News | 本工具内置 `sources.hackernews`，按分数+关键词过滤 |
| Reddit 子版块 | RSS：`https://www.reddit.com/r/AI_Agents/.rss`、`/r/LocalLLaMA/.rss`、`/r/artificial/.rss` |
| arXiv cs.AI / cs.CL | `http://export.arxiv.org/rss/cs.AI`、`http://export.arxiv.org/rss/cs.CL` |
| Papers with Code | https://paperswithcode.com/ （需另写 fetcher，暂用 arXiv 替代） |

## 中文资讯与播客

| 来源 | 说明 |
| :--- | :--- |
| 机器之心 | https://www.jiqizhixin.com/rss |
| 量子位 | 公众号为主，RSS 可用第三方镜像 |
| 播客（Latent Space / OnBoard! / 42章经） | 多数有 RSS，订阅后本工具只取标题+简介；完整音频转写属进阶功能（见下） |

## 进阶：超出 RSS 的来源

PRD 里提到的这些源**不是 RSS**，需要为 `sources.py` 各写一个 fetcher（属于「扩展数据源」工作量，按需做）：

- **Crunchbase 融资**：官方 API 需付费 key；或用 Apify 的 Crunchbase Scraper。写 `fetch_crunchbase(cfg)` 调其 API，把结果映射成标准 Item。
- **SEC EDGAR Form D**：早期私募融资，EDGAR 有免费全文检索 API（`https://efts.sec.gov/LATEST/search-index?q=...&forms=D`）。
- **播客 ASR 转写**：取 RSS 里的音频 enclosure URL → 下载 → Whisper/ASR 转文字 → 交给 processor 走「长文摘要」分支。这是 token 大户，建议只对少数精选播客开启。

接入新源时遵循 `sources.py` 的约定：返回标准 Item 列表，单源失败要被捕获（打日志 + 返回 `[]`），绝不让一个源拖垮整次运行。
