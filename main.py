import os

import telegram
from dotenv import load_dotenv
import logging
from typing import Dict

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, MessageEntity
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

CHOOSE, REPLY, TYPE = range(3)


contact_button = telegram.KeyboardButton(text="Номер телефона", request_contact=True)


reply_keyboard = [
    [contact_button, "Email"],
    ["Закрыть"],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


async def debug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "Данные для проверки и отладки!\nНомер: " + context.user_data['phone'] + "\nEmail: " + context.user_data['email']
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "Привет! Дай данные", reply_markup=markup
    )
    return CHOOSE


async def get_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    print(contact)
    context.user_data['phone'] = contact.phone_number
    if not isOk(context):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Спасибо!", reply_markup=markup)
        return CHOOSE
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Спасибо за данные!")
        print(context.user_data)
        await context.bot.send_document(chat_id=update.effective_chat.id, document='./file.pdf')
        await debug(update, context)
        return ConversationHandler.END


async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Введите email")
    return TYPE


async def close(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return ConversationHandler.END


async def type_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text
    print(email)
    context.user_data['email'] = email
    if not isOk(context):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Спасибо за мыло", reply_markup=markup)
        return CHOOSE
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Спасибо за данные")
        print(context.user_data)
        await context.bot.send_document(chat_id=update.effective_chat.id, document='./file.pdf')
        await debug(update, context)
        return ConversationHandler.END


def isOk(context: ContextTypes.DEFAULT_TYPE) ->bool:
    return 'phone' in context.user_data and 'email' in context.user_data


def main():
    load_dotenv()
    app = Application.builder().token(os.getenv("BOT_TOKEN")).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSE: [
                MessageHandler(filters.Regex("^Email$"), get_email),
                MessageHandler(filters.CONTACT, get_contact)
            ],
            TYPE: [
                MessageHandler(filters.Entity(MessageEntity.EMAIL), type_email)
            ]
        },
        fallbacks=[MessageHandler(filters.Regex("^Закрыть$"), close)]
    )

    app.add_handler(conv_handler)
    app.run_polling()


if __name__ == "__main__":
    main()