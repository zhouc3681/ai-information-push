# 真实资讯推送接入说明

当前产品已经和 `ai-agent-news-push` Skill 接上：

1. `ai-agent-news-push/scripts/` 负责真实采集、去重、LLM 摘要和渠道推送。
2. `ai_news_config.yaml` 负责配置数据源、关键词、模型、飞书/企业微信/邮件。
3. `data/dashboard-news.json` 是 Skill 生成给 Dashboard 读取的数据。
4. `AI-index.html` + `app.js` 会优先读取 `data/dashboard-news.json`，没有数据时才显示内置示例。

## 预览真实采集

```powershell
.\run-real-news-push.ps1
```

如果 Windows 阻止运行脚本，可以用：

```powershell
powershell -ExecutionPolicy Bypass -File .\run-real-news-push.ps1
```

这会执行 dry-run：

- 抓取 RSS、Hacker News、配置的高价值页面
- 只保留 `ai_news_config.yaml` 中 `delivery.recent_hours` 定义的最近时间窗口
- 生成 `data/dashboard-news.json`
- 同步生成 `data/dashboard-news.js`，直接打开 Dashboard 也能读取
- 不推送到任何群或邮箱
- 不更新去重存档

## 实时刷新

当前已创建一个每小时自动刷新的任务：`AI 情报实时刷新`。

它每小时执行一次 dry-run，只更新：

- `data/dashboard-news.json`
- `data/dashboard-news.js`

它不会发送企业微信、飞书或邮件。这样 Dashboard 始终展示最近窗口内的最新资讯。

## 链接展示规则

所有推送渠道都会显式展示完整 URL，不再只使用“点击查看”这类富文本链接。

推送正文会包含：

```text
原文链接：https://...
官网链接：https://...
```

这样复制到微信、Word、Notion 或归档日报后，链接仍然可见。

实时窗口在 `ai_news_config.yaml` 中配置：

```yaml
delivery:
  recent_hours: 96

dashboard:
  window_label: "最近 96 小时实时采集"
  refresh_minutes: 60
```

## 正式推送

先在 `ai_news_config.yaml` 填好至少一个渠道：

```yaml
push:
  feishu:
    enabled: true
    webhook: "https://open.feishu.cn/open-apis/bot/v2/hook/..."
    secret: ""

  wechat_work:
    enabled: true
    webhook: "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=..."

  email:
    enabled: true
    smtp_host: smtp.example.com
    smtp_port: 465
    use_ssl: true
    username: you@example.com
    password: "邮箱应用密码"
    from_addr: you@example.com
    to_addrs: [team@example.com]
```

再运行：

```powershell
.\run-real-news-push.ps1 -Push
```

或：

```powershell
powershell -ExecutionPolicy Bypass -File .\run-real-news-push.ps1 -Push
```

正式推送成功后，会更新 `data/pushed.json`，下次只推送新内容。

## 配置大模型

如果不配置大模型，系统仍会真实采集并生成降级简报，但中文摘要和去重合并质量会弱一些。

推荐配置 OpenAI 兼容网关：

```powershell
$env:AI_GATEWAY_BASE_URL="https://your-gateway.example.com"
$env:AI_GATEWAY_API_KEY="your-api-key"
```

也可以直接在 `ai_news_config.yaml` 写：

```yaml
llm:
  base_url: https://api.openai.com/v1
  api_key: sk-...
  model: gpt-4.1-mini
```

## 每天自动推送

这个环境支持后续加自动化任务。建议节奏：

- 每天 09:00：正式推送早报
- 每天 18:00：dry-run 生成页面，必要时人工转发

正式部署时，建议把 `ai_news_config.yaml` 中的 Webhook 和邮箱密码放到环境变量或内网配置中心，不要提交到公开仓库。
