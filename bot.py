
import os
import asyncio
import aiohttp
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

API = "https://api.mail.tm"


async def create_email():
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API}/domains") as response:
            data = await response.json()

        domains = data.get("hydra:member", [])
        if not domains:
            return None, None

        domain = domains[0]["domain"]
        address = f"temp{os.urandom(5).hex()}@{domain}"
        password = os.urandom(16).hex()

        async with session.post(
            f"{API}/accounts",
            json={"address": address, "password": password},
        ) as response:
            if response.status not in (200, 201):
                return None, None

        return address, password


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to Tempora Mail!\n\n"
        "Use /new to create a temporary email address.\n"
        "Use /inbox to check your latest messages."
    )


async def new_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Creating your temporary email...")

    address, password = await create_email()

    if not address:
        await update.message.reply_text(
            "Sorry, Mail.tm is unavailable right now. Please try again later."
        )
        return

    context.user_data["email"] = address
    context.user_data["password"] = password

    await update.message.reply_text(
        f"Your temporary email is:\n\n{address}\n\n"
        "Use /inbox to check for messages."
    )


async def inbox(update: Update, context: ContextTypes.DEFAULT_TYPE):
    address = context.user_data.get("email")
    password = context.user_data.get("password")

    if not address or not password:
        await update.message.reply_text(
            "You don't have an email yet. Send /new first."
        )
        return

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{API}/token",
            json={"address": address, "password": password},
        ) as response:
            if response.status != 200:
                await update.message.reply_text(
                    "Could not connect to your mailbox. Try /new again."
                )
                return
            token_data = await response.json()

        headers = {
            "Authorization": f"Bearer {token_data['token']}"
        }

        async with session.get(
            f"{API}/messages",
            headers=headers,
        ) as response:
            if response.status != 200:
                await update.message.reply_text(
                    "Could not load messages. Please try again."
                )
                return
            data = await response.json()

    messages = data.get("hydra:member", [])

    if not messages:
        await update.message.reply_text("Your inbox is empty.")
        return

    for message in messages[:10]:
        sender = message.get("from", {}).get("address", "Unknown")
        subject = message.get("subject", "(No subject)")
        await update.message.reply_text(
            f"From: {sender}\nSubject: {subject}"
        )


def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN environment variable is missing")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("new", new_email))
    app.add_handler(CommandHandler("inbox", inbox))
    app.run_polling()


if __name__ == "__main__":
    main()
                  
