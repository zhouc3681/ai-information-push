"""推送层：把结构化条目渲染成各平台的卡片/消息并发送。

新增渠道 = 写一个 push_<x>(items, cfg) 构造该平台 payload 并 POST webhook，
然后在 push_all 里注册。各平台卡片规范见 references/setup-webhooks.md。

约定：每个 push_<x> 返回 (ok: bool, detail: str)，由 push_all 汇总日志。
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import os
import sys
import time
import urllib.parse
from typing import Any

import requests


def _resolve(cfg: dict, key: str) -> str:
    """优先读 cfg[key]，否则读 cfg[key+'_env'] 指向的环境变量。

    用法示例：
        webhook: ""
        webhook_env: WECOM_WEBHOOK   # 实际值由环境变量提供，避免凭证入库。
    """
    val = cfg.get(key, "")
    if val:
        return val
    env_name = cfg.get(f"{key}_env", "")
    if env_name:
        return os.environ.get(env_name, "")
    return ""

CATEGORY_EMOJI = {
    "Tool Mastery": "🛠️",
    "Workflow Mastery": "🔗",
    "Thinking": "💡",
    "Funding": "💰",
    "Research": "🔬",
}


def _log(msg: str) -> None:
    print(f"[pushers] {msg}", file=sys.stderr)


# ---------------------- 文本/Markdown 渲染 ----------------------

def render_markdown(items: list[dict[str, Any]], title: str) -> str:
    """生成通用 markdown 文本 (企业微信/钉钉/终端预览都用它)。"""
    lines = [f"## {title}", ""]
    for i, it in enumerate(items, 1):
        emoji = CATEGORY_EMOJI.get(it.get("category", ""), "📌")
        lines.append(f"**{i}. {emoji} [{it.get('category','')}] {it.get('zh_title')}**")
        if it.get("one_liner"):
            lines.append(f"> {it['one_liner']}")
        for h in it.get("highlights", []):
            lines.append(f"- {h}")
        lines.append(f"[阅读原文]({it['url']})  ·  来源: {it.get('source','')}")
        lines.append("")
    return "\n".join(lines)


def render_plain(items: list[dict[str, Any]], title: str) -> str:
    """纯文本预览 (--dry-run 在终端打印)。"""
    out = [f"=== {title} ===", ""]
    for i, it in enumerate(items, 1):
        out.append(
            f"{i}. [{it.get('category','')}|{it.get('value_score','')}分] {it.get('zh_title')}"
        )
        if it.get("one_liner"):
            out.append(f"   结论: {it['one_liner']}")
        for h in it.get("highlights", []):
            out.append(f"   - {h}")
        out.append(f"   链接: {it['url']}  (来源: {it.get('source','')})")
        if it.get("merged_urls"):
            out.append(f"   合并自: {', '.join(it['merged_urls'])}")
        out.append("")
    return "\n".join(out)


# ---------------------- 各渠道 ----------------------

def push_feishu(items, cfg, title) -> tuple[bool, str]:
    webhook = _resolve(cfg, "webhook")
    if not webhook or "xxxx" in webhook:
        return False, "飞书 webhook 未配置"
    elements = []
    for it in items:
        emoji = CATEGORY_EMOJI.get(it.get("category", ""), "📌")
        text = f"**{emoji} [{it.get('category','')}] {it.get('zh_title')}**\n"
        if it.get("one_liner"):
            text += f"{it['one_liner']}\n"
        for h in it.get("highlights", []):
            text += f"· {h}\n"
        text += f"[阅读原文]({it['url']})  来源: {it.get('source','')}"
        elements.append({"tag": "div", "text": {"tag": "lark_md", "content": text}})
        elements.append({"tag": "hr"})
    card = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": title},
                "template": "blue",
            },
            "elements": elements or [{"tag": "div", "text": {"tag": "plain_text", "content": "暂无新内容"}}],
        },
    }
    body = _feishu_sign(card, _resolve(cfg, "secret"))
    return _post(webhook, body, "飞书")


def push_wechat_work(items, cfg, title) -> tuple[bool, str]:
    webhook = _resolve(cfg, "webhook")
    if not webhook or "xxxx" in webhook:
        return False, "企业微信 webhook 未配置"
    md = render_markdown(items, title)
    # 企业微信 markdown 消息上限约 4096 字节，超长则截断
    if len(md.encode("utf-8")) > 4000:
        md = md.encode("utf-8")[:3900].decode("utf-8", "ignore") + "\n…(内容过长已截断)"
    body = {"msgtype": "markdown", "markdown": {"content": md}}
    return _post(webhook, body, "企业微信")


def push_dingtalk(items, cfg, title) -> tuple[bool, str]:
    webhook = _resolve(cfg, "webhook")
    if not webhook or "xxxx" in webhook:
        return False, "钉钉 webhook 未配置"
    md = render_markdown(items, title)
    url = _dingtalk_sign(webhook, _resolve(cfg, "secret"))
    body = {"msgtype": "markdown", "markdown": {"title": title, "text": md}}
    return _post(url, body, "钉钉")


def push_email(items, cfg, title) -> tuple[bool, str]:
    import smtplib
    from email.mime.text import MIMEText

    to_addrs = cfg.get("to_addrs", [])
    if not to_addrs:
        return False, "邮件 to_addrs 未配置"
    html = render_markdown(items, title).replace("\n", "<br>")
    msg = MIMEText(html, "html", "utf-8")
    msg["Subject"] = title
    msg["From"] = cfg.get("from_addr", cfg.get("username", ""))
    msg["To"] = ", ".join(to_addrs)
    password = _resolve(cfg, "password")
    try:
        if cfg.get("use_ssl", True):
            server = smtplib.SMTP_SSL(cfg["smtp_host"], int(cfg.get("smtp_port", 465)), timeout=30)
        else:
            server = smtplib.SMTP(cfg["smtp_host"], int(cfg.get("smtp_port", 587)), timeout=30)
            server.starttls()
        server.login(cfg["username"], password)
        server.sendmail(msg["From"], to_addrs, msg.as_string())
        server.quit()
        return True, "邮件发送成功"
    except Exception as exc:
        return False, f"邮件发送失败: {exc}"


# ---------------------- 编排 + 工具函数 ----------------------

PUSHERS = {
    "feishu": push_feishu,
    "wechat_work": push_wechat_work,
    "dingtalk": push_dingtalk,
    "email": push_email,
}


def push_all(items, push_cfg, title) -> list[str]:
    """对所有 enabled 渠道发送，返回每个渠道的结果日志。"""
    results = []
    for name, fn in PUSHERS.items():
        chan_cfg = push_cfg.get(name, {})
        if not chan_cfg.get("enabled"):
            continue
        try:
            ok, detail = fn(items, chan_cfg, title)
        except Exception as exc:
            ok, detail = False, f"异常: {exc}"
        results.append(f"[{name}] {'OK' if ok else 'FAIL'} - {detail}")
        _log(results[-1])
    if not results:
        results.append("没有任何启用的推送渠道 (push.*.enabled 均为 false)")
    return results


def _post(url, body, label) -> tuple[bool, str]:
    try:
        r = requests.post(url, json=body, timeout=20)
        data = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
        # 飞书/企业微信/钉钉成功时 errcode/code/StatusCode 多为 0
        code = data.get("code", data.get("errcode", data.get("StatusCode", 0)))
        if r.status_code == 200 and code in (0, None):
            return True, f"{label} 推送成功"
        return False, f"{label} 返回异常: {r.status_code} {r.text[:200]}"
    except Exception as exc:
        return False, f"{label} 请求失败: {exc}"


def _feishu_sign(card: dict, secret: str) -> dict:
    if not secret:
        return card
    ts = str(int(time.time()))
    string_to_sign = f"{ts}\n{secret}"
    sign = base64.b64encode(
        hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
    ).decode("utf-8")
    card = dict(card)
    card["timestamp"] = ts
    card["sign"] = sign
    return card


def _dingtalk_sign(webhook: str, secret: str) -> str:
    if not secret:
        return webhook
    ts = str(round(time.time() * 1000))
    string_to_sign = f"{ts}\n{secret}"
    sign = urllib.parse.quote_plus(
        base64.b64encode(
            hmac.new(secret.encode("utf-8"), string_to_sign.encode("utf-8"), hashlib.sha256).digest()
        )
    )
    sep = "&" if "?" in webhook else "?"
    return f"{webhook}{sep}timestamp={ts}&sign={sign}"
