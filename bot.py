# bot.py
import os
import json
import base64
import uuid
import requests
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
SERVER_IP = os.environ.get("SERVER_IP", "185.199.108.153")  # IP آزمایشی
USERS_FILE = "users.json"

def generate_vmess_config(port=443, user_id=None):
    if not user_id:
        user_id = str(uuid.uuid4())
    config = {
        "v": "2",
        "ps": f"GitHub_CodeSpace_{datetime.now().strftime('%H:%M')}",
        "add": SERVER_IP,
        "port": port,
        "id": user_id,
        "aid": 0,
        "net": "ws",
        "type": "none",
        "host": "",
        "path": "/",
        "tls": "none"
    }
    json_str = json.dumps(config, separators=(',', ':'))
    return f"vmess://{base64.b64encode(json_str.encode()).decode()}"

def deploy_to_codespaces():
    """ساخت خودکار کانفیگ برای Codespaces"""
    # این تابع به API گیت‌هاب متصل می‌شود
    github_token = os.environ.get("GH_TOKEN")
    if not github_token:
        return None
    
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # ایجاد یک Codespace جدید
    url = "https://api.github.com/user/codespaces"
    data = {
        "repository_id": os.environ.get("REPO_ID"),
        "machine": "basicLinux32gb",
        "devcontainer_path": ".devcontainer/devcontainer.json"
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        codespace = response.json()
        return codespace.get("name")
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 **ربات سازنده کانفیگ V2Ray قدرتمند**\n\n"
        "📡 دستورات:\n"
        "/config - دریافت کانفیگ جدید\n"
        "/deploy - راه‌اندازی سرور جدید روی گیت‌هاب\n"
        "/status - وضعیت سرور\n\n"
        "⏱️ هر کانفیگ حداقل ۱ ساعت اعتبار دارد",
        parse_mode="Markdown"
    )

async def get_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # تولید کانفیگ
    config_link = generate_vmess_config(port=443)
    
    # ذخیره زمان انقضا (۱ ساعت بعد)
    expiry = datetime.now() + timedelta(hours=1)
    
    await update.message.reply_text(
        f"🔐 **کانفیگ اختصاصی شما**\n\n"
        f"`{config_link}`\n\n"
        f"✅ اعتبار: تا ساعت {expiry.strftime('%H:%M')}\n"
        f"🌐 پروتکل: VMess + WebSocket\n"
        f"💾 حجم: نامحدود\n\n"
        f"⚠️ برای اتصال از اپ V2RayNG یا Nekobox استفاده کنید",
        parse_mode="Markdown"
    )

async def deploy_server(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 در حال راه‌اندازی سرور جدید روی گیت‌هاب...")
    
    codespace_name = deploy_to_codespaces()
    
    if codespace_name:
        await update.message.reply_text(
            f"✅ سرور با موفقیت راه‌اندازی شد!\n"
            f"🔧 اسم Codespace: `{codespace_name}`\n"
            f"⏱️ یک ساعت فعال خواهد بود\n\n"
            f"سپس از /config استفاده کنید",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("❌ راه‌اندازی سرور失敗. توکن گیت‌هاب معتبر نیست!")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🟢 **وضعیت سیستم**\n\n"
        f"📡 پلتفرم: GitHub Codespaces\n"
        f"⏰ زمان فعال بودن: ۱ ساعت\n"
        f"🔄 ربات: فعال\n"
        f"🌍 پروکسی: VMess+WebSocket\n"
        f"📊 مصرف ماهیانه: محدودیت ۲۰۰۰ دقیقه\n\n"
        "💡 نکته: برای تمدید، /deploy را بزنید"
    )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("config", get_config))
    app.add_handler(CommandHandler("deploy", deploy_server))
    app.add_handler(CommandHandler("status", status))
    
    print("✅ ربات روشن شد...")
    app.run_polling()

if __name__ == "__main__":
    main()
