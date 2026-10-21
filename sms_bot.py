
import os
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

TOKEN = os.getenv("SMS_BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to Tempora SMS! 📱\n\n"
        "Commands:\n"
        "/number - Request an SMS number\n"
        "/inbox - Check incoming messages\n"
        "/help - Show help\n\n"
        "SMS provider connection is not configured yet."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Tempora SMS Help\n\n"
        "/start - Start the bot\n"
        "/number - Request a number\n"
        "/inbox - Check incoming SMS\n"
        "/help - Show this message\n\n"
        "Use only numbers you own or are authorized to use."
    )


async def get_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "No SMS provider is connected yet.\n\n"
        "Next, we need to configure a provider that supplies "
        "phone numbers and supports incoming SMS."
    )


async def inbox(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Your inbox is not connected yet.\n\n"
        "Once an SMS provider is configured, this command "
        "can retrieve messages for your assigned number."
    )


def main():
    if not TOKEN:
        raise RuntimeError(
            "Missing SMS_BOT_TOKEN environment variable."
        )

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("number", get_number))
    app.add_handler(CommandHandler("inbox", inbox))

    print("Tempora SMS bot is starting...")
    app.run_polling()


if __name__ == "__main__":
    main()
  
