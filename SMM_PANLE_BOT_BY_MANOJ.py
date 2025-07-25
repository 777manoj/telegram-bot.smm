import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# === CONFIG ===
BOT_TOKEN = "8086903911:AAET2LySb45-Y8AzeV4RtPuMq3iZQeyQuio"
UPI_ID = "9382777247@ybl"
CHANNEL_USERNAME = "@smmpanelpament"
MINIMUM_AMOUNT = 10
ADMIN_ID = 8086903911
SMM_API_URL = "https://tntsmm.in/api/v2"
SMM_API_KEY = "35f4e886bfa3cd37ea77f9500696565c"

# === LOGGING ===
logging.basicConfig(level=logging.INFO)

# === /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to the SMM Payment Bot!\n"
        "Use /addfunds to view UPI payment info.\n"
        "Use /services to view all available services."
    )

# === /addfunds ===
async def addfunds(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "💰 *Add Funds Info:*\n\n"
        f"📌 UPI ID: `{UPI_ID}`\n"
        f"✅ Minimum Amount: ₹{MINIMUM_AMOUNT}\n"
        "📤 After payment, send screenshot to the Admin.\n"
        "🕐 Funds will be added within 5–10 minutes."
    )
    await update.message.reply_text(message, parse_mode="Markdown")

# === /payment ===
async def payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ You're not authorized to use this command.")
        return

    if len(context.args) != 2:
        await update.message.reply_text("❌ Usage:\n/payment <user_id> <received/denied>")
        return

    user_id = context.args[0]
    status = context.args[1].lower()

    if status == "received":
        text = f"✅ *Payment received* from user `{user_id}`."
    elif status == "denied":
        text = f"❌ *Payment denied* for user `{user_id}`."
    else:
        await update.message.reply_text("❌ Invalid status. Use: received or denied")
        return

    await context.bot.send_message(chat_id=CHANNEL_USERNAME, text=text, parse_mode="Markdown")
    await update.message.reply_text("✅ Notification sent to channel.")

# === /services (Full List Line-by-Line) ===
async def services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        payload = {
            'key': SMM_API_KEY,
            'action': 'services'
        }
        response = requests.post(SMM_API_URL, data=payload)
        services_data = response.json()

        if not isinstance(services_data, list):
            await update.message.reply_text("⚠️ Could not fetch services.")
            return

        count = 0
        batch = ""
        for service in services_data:
            count += 1
            sid = service.get("service", "N/A")
            name = service.get("name", "N/A")
            rate = service.get("rate", "?")
            min_val = service.get("min", "?")
            max_val = service.get("max", "?")
            category = service.get("category", "Unknown")

            line = f"{sid}. {name}\n📂 {category}\n💸 ₹{rate}/1K | Min: {min_val}, Max: {max_val}\n\n"
            batch += line

            # Send in chunks of 10
            if count % 10 == 0:
                await update.message.reply_text(batch)
                batch = ""

        if batch:
            await update.message.reply_text(batch)

    except Exception as e:
        await update.message.reply_text("❌ Error getting services.")

# === Main ===
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addfunds", addfunds))
    app.add_handler(CommandHandler("payment", payment))
    app.add_handler(CommandHandler("services", services))
    print("✅ Bot running...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()

# === Run (PyDroid safe) ===
if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()