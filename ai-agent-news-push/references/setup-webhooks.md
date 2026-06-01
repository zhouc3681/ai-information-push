# 各平台机器人 Webhook 获取与消息格式

读这份文档来正确获取 webhook 地址、构造消息体、排查推送失败。不要凭记忆猜测格式。

## 飞书 (Feishu / Lark) 自定义机器人

**获取 webhook**：飞书群 → 右上角设置 → 群机器人 → 添加机器人 → 自定义机器人 → 复制 Webhook 地址（形如 `https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx`）。

**安全设置**：自定义机器人支持三种安全校验，任选其一：
- 自定义关键词：消息里必须含某关键词（最简单，本工具默认 title 含 "AI" 通常即可）
- 签名校验：会给一个 `secret`，填到 config 的 `feishu.secret`，本工具会自动按 `timestamp\nsecret` 做 HmacSHA256 + base64 签名。
- IP 白名单：服务器固定 IP 时用。

**消息体（交互式卡片）**：
```json
{
  "msg_type": "interactive",
  "timestamp": "1699...",   // 仅签名校验时需要
  "sign": "....",            // 仅签名校验时需要
  "card": {
    "header": {"title": {"tag": "plain_text", "content": "标题"}, "template": "blue"},
    "elements": [
      {"tag": "div", "text": {"tag": "lark_md", "content": "**加粗** 普通文本 [链接](https://...)"}},
      {"tag": "hr"}
    ]
  }
}
```
注意：飞书富文本用 `lark_md`，支持 `**bold**`、`[text](url)`，但**不支持** `##` 标题语法，标题放 header。

**常见失败**：
- `19021` / sign 校验失败 → secret 没填或填错。
- 文本里关键词校验不通过 → 关掉关键词校验或确保内容含关键词。

## 企业微信 (WeChat Work) 群机器人

**获取 webhook**：企业微信群 → 右上角 → 添加群机器人 → 新创建 → 复制 Webhook 地址（形如 `https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxxxxxx`）。无需签名。

**消息体（markdown）**：
```json
{"msgtype": "markdown", "markdown": {"content": "## 标题\n**加粗** [链接](https://...)"}}
```
关键限制：
- markdown 内容上限约 **4096 字节**，超长必须截断（本工具已自动截断到 ~3900 字节）。
- 支持 `#`~`######` 标题、`**bold**`、`>` 引用、`[text](url)` 链接、`<font color="info">`。
- 每个机器人**每分钟最多 20 条**，条数多时合并成一条卡片发送（本工具默认合并）。

**常见失败**：`errcode: 93000` webhook key 失效；`45009` 触发频率限制。

## 钉钉 (DingTalk) 自定义机器人

**获取 webhook**：钉钉群 → 群设置 → 智能群助手 → 添加机器人 → 自定义 → 复制 Webhook（形如 `https://oapi.dingtalk.com/robot/send?access_token=xxxxxxxx`）。

**安全设置**：建议选「加签」，得到 `secret`（以 `SEC` 开头），填到 `dingtalk.secret`，本工具会按 `timestamp\nsecret` 做 HmacSHA256 并把 `timestamp`、`sign` 拼到 URL 上。

**消息体（markdown）**：
```json
{"msgtype": "markdown", "markdown": {"title": "标题", "text": "## 标题\n内容"}}
```
注意：钉钉的 markdown 必须有 `title`（消息列表里的展示文字）。同样有关键词/加签/IP 三选一的安全校验。

## 邮件 (SMTP)

不是 webhook，用标准 SMTP。config 里填 `smtp_host / smtp_port / use_ssl / username / password / from_addr / to_addrs`。
- QQ/163 等邮箱需用「授权码」而非登录密码。
- 465 端口用 SSL（`use_ssl: true`），587 用 STARTTLS（`use_ssl: false`）。

## 调试技巧

任何渠道接不通时，先用 curl 单独验证 webhook 是否有效，再回到工具排查：
```bash
# 企业微信示例
curl -X POST '<webhook>' -H 'Content-Type: application/json' \
  -d '{"msgtype":"text","text":{"content":"测试 hello"}}'
```
能收到说明 webhook 没问题，问题在消息体；收不到则是 webhook/安全设置问题。
