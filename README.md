# AI 情报雷达

一个轻量级企业 AI / Agent 资讯推送工具。

它不是新闻站、RSS 阅读器或复杂 SaaS，而是一个面向企业内部员工、AI 产品经理、研究员和管理层的情报助手：每天自动抓取最新 AI / Agent 资讯，筛选真正值得关注的信息，生成中文简报，并支持推送到企业微信、飞书或邮箱。

## 当前能力

- 实时采集 AI / Agent 资讯：RSS、Google News、Hacker News、高价值官方页面。
- 只保留最近时间窗口内的新内容，默认最近 96 小时。
- 关键词过滤、去重、后台排序和摘要生成。
- Dashboard 页面展示今日简报、趋势、PoC 建议和原文链接。
- 所有资讯都显式展示完整 URL，复制到微信、Word、Notion 或日报归档后链接不丢失。
- 支持企业微信、飞书、钉钉和邮件推送。
- Skill / 工作流页面默认隐藏，内部查看时在地址后加 `?internal=1`。

## 目录结构

```text
AI-index.html                 # Dashboard 页面入口
app.js                        # 页面交互逻辑，优先读取真实采集数据
styles.css                    # 页面样式
ai_news_config.yaml           # 共享配置模板，不要写真实密钥后提交
run-real-news-push.ps1        # 一键刷新 / 推送脚本
REAL_PUSH_SETUP.md            # 更详细的推送配置说明
ai-agent-news-push/           # 资讯采集、处理、推送 Skill
data/                         # 自动生成数据，GitHub 不需要同步
```

## 快速开始

首次使用先安装依赖并生成真实数据：

```powershell
powershell -ExecutionPolicy Bypass -File .\run-real-news-push.ps1
```

这会执行 dry-run：

- 抓取最新资讯
- 生成 `data/dashboard-news.json`
- 生成 `data/dashboard-news.js`
- 不推送到任何群或邮箱
- 不更新去重存档

然后打开：

```text
AI-index.html
```

如果需要查看内部 Skill 和工作流页面，在地址后加：

```text
?internal=1
```

## 配置推送

不要直接把真实 webhook、邮箱密码、API Key 写进要提交的配置里。

推荐每个人复制一份本地私有配置：

```powershell
Copy-Item .\ai_news_config.yaml .\ai_news_config.local.yaml
```

`run-real-news-push.ps1` 会优先读取 `ai_news_config.local.yaml`，没有它才读取 `ai_news_config.yaml`。

### 企业微信

在企业微信群里添加“自定义机器人”，复制 webhook：

```yaml
push:
  wechat_work:
    enabled: true
    webhook: "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxx"
```

### 飞书

在飞书群里添加“自定义机器人”，复制 webhook：

```yaml
push:
  feishu:
    enabled: true
    webhook: "https://open.feishu.cn/open-apis/bot/v2/hook/xxxx"
    secret: ""
```

如果飞书机器人开启了签名校验，把密钥填到 `secret`。

### 邮件

填写 SMTP 信息：

```yaml
push:
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

## 配置大模型

不配置大模型也能真实采集和推送，但摘要会是降级版。

推荐配置 OpenAI 兼容接口：

```powershell
$env:AI_GATEWAY_BASE_URL="https://your-gateway.example.com"
$env:AI_GATEWAY_API_KEY="your-api-key"
```

也可以直接在本地私有配置中写：

```yaml
llm:
  base_url: https://api.openai.com/v1
  api_key: sk-...
  model: gpt-4.1-mini
```

## 刷新与推送

只刷新 Dashboard，不发送：

```powershell
powershell -ExecutionPolicy Bypass -File .\run-real-news-push.ps1
```

真实推送到已启用渠道：

```powershell
powershell -ExecutionPolicy Bypass -File .\run-real-news-push.ps1 -Push
```

正式推送成功后，会更新去重存档，避免下次重复推送同一条内容。

## 链接永久可复制

产品要求所有渠道都不能只依赖富文本超链接。

Dashboard、今日简报、企业微信、飞书、钉钉和邮件都会显式展示：

```text
项目名称：xxx
一句话介绍：xxx
来源：xxx
原文链接：https://...
官网链接：https://...
推荐理由：xxx
```

即使用户复制到微信、Word、Notion，或导出为本地日报，仍然可以看到完整 URL。

## 实时更新

当前配置默认：

```yaml
delivery:
  recent_hours: 96

dashboard:
  window_label: "最近 96 小时实时采集"
  refresh_minutes: 60
```

也就是说，系统只展示最近 96 小时内的新资讯。当前工作区已创建自动刷新任务：`AI 情报实时刷新`，每小时生成一次最新 Dashboard 数据，但不会自动往企业微信、飞书或邮箱发送。

## GitHub 协作建议

建议同步到 GitHub 的文件：

```text
AI-index.html
app.js
styles.css
README.md
REAL_PUSH_SETUP.md
run-real-news-push.ps1
ai_news_config.yaml
.gitignore
ai-agent-news-push/
```

不要同步到 GitHub 的内容：

```text
.venv/
.pip-cache/
data/
ai_news_config.local.yaml
*.log
*.zip
```

特别注意：

- `ai_news_config.yaml` 应作为团队共享模板，里面不要放真实 webhook、SMTP 密码或 API Key。
- 每个协作者本地复制 `ai_news_config.local.yaml`，在里面填自己的 webhook、邮箱和模型配置。
- `data/` 是运行后自动生成的 Dashboard 数据和去重记录，不需要提交。
- 如果要在服务器上部署，可以把真实配置放到服务器环境变量或私有配置文件中。

## 推荐协作流程

1. 从 GitHub 拉取代码。
2. 复制 `ai_news_config.yaml` 为 `ai_news_config.local.yaml`。
3. 在本地配置 webhook、邮箱或 LLM。
4. 先 dry-run 预览。
5. 确认内容后再 `-Push` 正式推送。
6. 修改数据源、关键词、页面或推送逻辑后提交代码，但不要提交本地私有配置。
