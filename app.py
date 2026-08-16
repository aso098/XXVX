import os
import subprocess
import logging
import threading
from flask import Flask, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ====== إعداد Flask ======
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return jsonify({"status": "running", "message": "🤖 Bot is active"})

@flask_app.route('/health')
def health():
    return jsonify({"status": "healthy"})

# ====== إعداد البوت ======
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN غير مضبوط")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ====== أوامر البوت ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔒 أداة اختبار التحمل الدفاعية\n\n"
        "/test <URL> - تشغيل اختبار\n"
        "/help - المساعدة"
    )

async def run_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ أضف رابط: /test https://example.com")
        return
    
    url = context.args[0]
    await update.message.reply_text(f"🔄 جاري اختبار {url} ...")
    
    try:
        os.makedirs("reports", exist_ok=True)
        cmd = [
            "locust", "-f", "locustfile.py",
            "--host", url,
            "--users", "5",
            "--spawn-rate", "2",
            "--run-time", "5s",
            "--headless",
            "--html", "reports/report.html"
        ]
        subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        await update.message.reply_text("✅ اكتمل الاختبار!")
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {str(e)}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/test <URL> - تشغيل اختبار تحمل")

# ====== تشغيل البوت ======
def run_bot():
    logger.info("🚀 بدء البوت...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("test", run_test))
    app.add_handler(CommandHandler("help", help_command))
    logger.info("✅ البوت جاهز!")
    app.run_polling()

# ====== التشغيل الكامل ======
if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"🌐 تشغيل Flask على المنفذ {port}")
    flask_app.run(host='0.0.0.0', port=port)
