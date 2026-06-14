"""
多通道通知分发终端
支持 Telegram / 飞书 / 钉钉 / 邮件 / Notion
"""

import os
import json
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone, timedelta
from typing import Optional

import requests

TZ_SHANGHAI = timezone(timedelta(hours=8))

# ===== 环境变量读取 =====
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

FEISHU_WEBHOOK = os.environ.get("FEISHU_WEBHOOK", "")
DINGTALK_WEBHOOK = os.environ.get("DINGTALK_WEBHOOK", "")

SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY", "")
EMAIL_FROM = os.environ.get("EMAIL_FROM", "")
EMAIL_TO = os.environ.get("EMAIL_TO", "")

NOTION_API_KEY = os.environ.get("NOTION_API_KEY", "")
NOTION_DATABASE_ID = os.environ.get("NOTION_DATABASE_ID", "")

# 推送模式选择
PUSH_MODE = os.environ.get("PUSH_MODE", "telegram")  # telegram | feishu | dingtalk | email | notion | all


def format_article(item: dict, index: int = 0, channel: str = "telegram") -> str:
    """根据渠道格式化文章"""
    emoji = {
        "技巧": "💡", "新工具": "🛠️", "技术突破": "🚀",
        "官方更新": "📢", "开源项目": "🌟", "论文解读": "📄",
        "未分类": "📌",
    }.get(item.get("category", ""), "📌")

    date_str = item.get("published_at", "")[:10] if item.get("published_at") else ""

    if channel == "telegram":
        # Telegram 支持 Markdown
        lines = [
            f"{emoji} *{item['title_cn'][:100]}*",
            f"_{item.get('category', '未分类')} | {item['source_name']} | {date_str}_",
            f"",
            f"{item.get('summary_cn', '')[:200]}",
            f"",
            f"🔗 [原文链接]({item['url']})",
        ]
        if item.get("key_takeaway"):
            lines.insert(3, f"💬 _{item['key_takeaway'][:120]}_")
        return "\n".join(lines)

    elif channel == "feishu":
        # 飞书富文本
        content = [
            [{"tag": "text", "text": f"{emoji} {item['title_cn'][:80]}\n"}],
            [{"tag": "text", "text": f"分类: {item.get('category','未分类')} | 来源: {item['source_name']} | {date_str}\n"}],
            [{"tag": "text", "text": f"{item.get('summary_cn','')[:150]}\n"}],
            [{"tag": "a", "text": "查看原文", "href": item['url']}],
        ]
        return content

    elif channel == "dingtalk":
        # 钉钉 Markdown
        lines = [
            f"### {emoji} {item['title_cn'][:60]}",
            f"**{item.get('category','未分类')}** | {item['source_name']} | {date_str}  \n",
            f"{item.get('summary_cn','')[:150]}  \n",
            f"[查看详情]({item['url']})  \n",
        ]
        return "\n".join(lines)

    else:
        # 纯文本
        lines = [
            f"[{item.get('category','未分类')}] {item['title_cn'][:100]}",
            f"来源: {item['source_name']} | {date_str}",
            f"摘要: {item.get('summary_cn','')[:200]}",
            f"链接: {item['url']}",
        ]
        return "\n".join(lines)


# ===== Telegram =====
def send_telegram(items: list[dict], verbose: bool = True) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram 配置缺失，跳过推送")
        return False

    # 先发汇总
    now = datetime.now(TZ_SHANGHAI).strftime("%Y-%m-%d %H:%M")
    header = f"🤖 *AI 情报日报* ({now})\n📊 本批次筛选出 {len(items)} 条高质量情报\n━━━━━━━━━━━━━━"
    _send_telegram_message(header)

    count = 0
    for i, item in enumerate(items[:15]):  # 最多推送15条
        text = format_article(item, i, "telegram")
        success = _send_telegram_message(text)
        if success:
            count += 1
        time.sleep(0.3)

    if verbose:
        print(f"📨 Telegram: 成功推送 {count}/{len(items[:15])} 条")
    return True


def _send_telegram_message(text: str) -> bool:
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        resp = requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text[:4096],
            "parse_mode": "Markdown",
            "disable_web_page_preview": False,
        }, timeout=10)
        return resp.status_code == 200
    except Exception as e:
        print(f"  ⚠️ Telegram 发送失败: {e}")
        return False


# ===== 飞书 =====
def send_feishu(items: list[dict], verbose: bool = True) -> bool:
    if not FEISHU_WEBHOOK:
        print("⚠️ 飞书 Webhook 配置缺失，跳过推送")
        return False

    now = datetime.now(TZ_SHANGHAI).strftime("%Y-%m-%d %H:%M")
    blocks = [
        {"tag": "div", "text": {"tag": "lark_md", "content": f"**🤖 AI 情报日报** ({now})\\n📊 本批次筛选出 {len(items)} 条高质量情报"}},
        {"tag": "hr"},
    ]

    for item in items[:10]:
        content = format_article(item, channel="feishu")
        for block in content:
            blocks.append({"tag": "div", "fields": block})
        blocks.append({"tag": "hr"})

    try:
        resp = requests.post(FEISHU_WEBHOOK, json={
            "msg_type": "interactive",
            "card": {
                "header": {"title": {"tag": "plain_text", "content": "🤖 AI 情报日报"}},
                "elements": blocks[:50],  # 飞书卡片元素限制
            }
        }, timeout=10)
        if verbose:
            print(f"📨 飞书: {'成功' if resp.status_code == 200 else '失败'}")
        return resp.status_code == 200
    except Exception as e:
        print(f"  ⚠️ 飞书推送失败: {e}")
        return False


# ===== 钉钉 =====
def send_dingtalk(items: list[dict], verbose: bool = True) -> bool:
    if not DINGTALK_WEBHOOK:
        print("⚠️ 钉钉 Webhook 配置缺失，跳过推送")
        return False

    now = datetime.now(TZ_SHANGHAI).strftime("%Y-%m-%d %H:%M")
    text = f"## 🤖 AI 情报日报 ({now})\n\n📊 本批次筛选出 {len(items)} 条高质量情报\n\n"

    for i, item in enumerate(items[:10]):
        text += format_article(item, i, "dingtalk")
        text += "\n---\n\n"

    try:
        resp = requests.post(DINGTALK_WEBHOOK, json={
            "msgtype": "markdown",
            "markdown": {"title": "AI 情报日报", "text": text[:20000]},
        }, timeout=10)
        if verbose:
            print(f"📨 钉钉: {'成功' if resp.status_code == 200 else '失败'}")
        return resp.status_code == 200
    except Exception as e:
        print(f"  ⚠️ 钉钉推送失败: {e}")
        return False


# ===== Email (SendGrid) =====
def send_email(items: list[dict], verbose: bool = True) -> bool:
    if not SENDGRID_API_KEY or not EMAIL_FROM or not EMAIL_TO:
        print("⚠️ Email 配置缺失，跳过推送")
        return False

    now = datetime.now(TZ_SHANGHAI).strftime("%Y-%m-%d")
    subject = f"🤖 AI 情报日报 - {now}"

    # 构建 HTML 邮件
    html_items = ""
    for item in items[:20]:
        html_items += f"""
        <div style="margin-bottom: 20px; padding: 15px; border-left: 4px solid #4A90D9; background: #f8f9fa;">
            <h3 style="margin:0 0 8px 0;"><a href="{item['url']}" style="color:#333;">{item['title_cn'][:100]}</a></h3>
            <p style="margin:4px 0; color:#666; font-size:13px;">
                {item.get('category','未分类')} | 来源: {item['source_name']} | {item.get('published_at','')[:10]}
            </p>
            <p style="margin:8px 0; color:#444;">{item.get('summary_cn','')[:200]}</p>
            {f'<p style="margin:4px 0; font-style:italic; color:#888;">💬 {item["key_takeaway"]}</p>' if item.get("key_takeaway") else ""}
        </div>
        """

    html = f"""
    <html><body style="font-family: -apple-system, sans-serif; max-width: 700px; margin: 0 auto;">
    <h1>🤖 AI 情报日报</h1>
    <p style="color:#666;">{now} | 本批次筛选出 {len(items)} 条高质量情报</p>
    <hr>
    {html_items}
    <hr>
    <p style="color:#999; font-size:12px;">由 AI Intelligence Task 自动生成 | <a href="#">退订</a></p>
    </body></html>
    """

    try:
        resp = requests.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers={
                "Authorization": f"Bearer {SENDGRID_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "personalizations": [{"to": [{"email": EMAIL_TO}]}],
                "from": {"email": EMAIL_FROM},
                "subject": subject,
                "content": [{"type": "text/html", "value": html}],
            },
            timeout=15,
        )
        if verbose:
            print(f"📨 Email: {'成功' if resp.status_code == 202 else f'失败({resp.status_code})'}")
        return resp.status_code == 202
    except Exception as e:
        print(f"  ⚠️ Email 推送失败: {e}")
        return False


# ===== Notion =====
def send_notion(items: list[dict], verbose: bool = True) -> bool:
    if not NOTION_API_KEY or not NOTION_DATABASE_ID:
        print("⚠️ Notion 配置缺失，跳过创建页面")
        # Notion 不好用的话，保存本地 JSON
        return _save_local_json(items, verbose)

    count = 0
    for item in items[:10]:
        try:
            props = {
                "Name": {"title": [{"text": {"content": item['title_cn'][:100]}}]},
                "Category": {"select": {"name": item.get('category', '未分类')}},
                "Source": {"rich_text": [{"text": {"content": item['source_name']}}]},
                "URL": {"url": item['url']},
                "Summary": {"rich_text": [{"text": {"content": item.get('summary_cn', '')[:500]}}]},
            }

            resp = requests.post(
                "https://api.notion.com/v1/pages",
                headers={
                    "Authorization": f"Bearer {NOTION_API_KEY}",
                    "Content-Type": "application/json",
                    "Notion-Version": "2022-06-28",
                },
                json={"parent": {"database_id": NOTION_DATABASE_ID}, "properties": props},
                timeout=10,
            )
            if resp.status_code == 200:
                count += 1
            time.sleep(0.3)
        except Exception as e:
            print(f"  ⚠️ Notion 写入失败: {e}")

    if verbose:
        print(f"📨 Notion: 成功写入 {count}/{len(items[:10])} 条")
    return True


def _save_local_json(items: list[dict], verbose: bool = True) -> bool:
    """本地 JSON 备份"""
    path = "data/intelligence_output.json"
    try:
        os.makedirs("data", exist_ok=True)
        existing = []
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                existing = json.load(f)

        # 合并去重
        existing_urls = {item["url"] for item in existing}
        new_items = [item for item in items if item["url"] not in existing_urls]
        existing.extend(new_items)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)

        if verbose:
            print(f"💾 本地 JSON: 新增 {len(new_items)} 条，总计 {len(existing)} 条 → {path}")
        return True
    except Exception as e:
        print(f"  ⚠️ 本地保存失败: {e}")
        return False


# ===== 汇总分发 =====
def dispatch(items: list[dict], verbose: bool = True):
    """根据 PUSH_MODE 分发到各渠道"""
    if not items:
        print("📭 无情报需要推送")
        return

    print(f"\n📤 开始分发 {len(items)} 条情报 (模式: {PUSH_MODE})")

    if PUSH_MODE in ("telegram", "all"):
        send_telegram(items, verbose)
    if PUSH_MODE in ("feishu", "all"):
        send_feishu(items, verbose)
    if PUSH_MODE in ("dingtalk", "all"):
        send_dingtalk(items, verbose)
    if PUSH_MODE in ("email", "all"):
        send_email(items, verbose)
    if PUSH_MODE in ("notion", "all"):
        send_notion(items, verbose)
    if PUSH_MODE == "json":
        _save_local_json(items, verbose)

    # 始终保存本地 JSON 备份
    if PUSH_MODE != "json":
        _save_local_json(items, verbose)

    print("✅ 分发完成")


if __name__ == "__main__":
    # 快速测试
    test_items = [{
        "title": "10 Hidden ChatGPT Features",
        "title_cn": "10个ChatGPT隐藏功能",
        "url": "https://example.com/test",
        "summary": "Test summary",
        "summary_cn": "测试摘要：发现10个大多数用户不知道的ChatGPT功能",
        "source_name": "r/ChatGPT",
        "lang": "en",
        "published_at": "2026-06-14T12:00:00+08:00",
        "category": "技巧",
        "key_takeaway": "使用自定义指令可以大幅提升ChatGPT输出质量",
        "score": 9,
    }]
    dispatch(test_items)
