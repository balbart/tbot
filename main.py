import os
import telegram
from dotenv import load_dotenv
import logging

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
from sheets_handler import GoogleTable
from handler import CsvHandler
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
load_dotenv()
table = GoogleTable(os.getenv('TABLE_NAME'))
csv_file = CsvHandler()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            telegram.KeyboardButton("Подтвердить", request_contact=True)
        ]
    ]
    reply = telegram.ReplyKeyboardMarkup(keyboard, one_time_keyboard=False, resize_keyboard=True)
    await update.message.reply_text(
        "Добрый день! Отправим чек-лист ... в этот чат. Нажмите на кнопку \"подтвердить\" для получения материалов.", reply_markup=reply)


async def send_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    table.append_contact(update.message.contact)
    csv_file.append_contact(update.message.contact)
    context.user_data['doc_send'] = True
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Спасибо... Узнайте больше о возможностях размещения рекламы на Novikov TV:\nhttps://novikovtv.tv", reply_markup=ReplyKeyboardRemove())
    await context.bot.send_document(chat_id=update.effective_chat.id, document='./file.pdf')
    await context.bot.send_contact(chat_id=update.effective_chat.id, phone_number='+79099092022', first_name='NovikovTV')


async def share(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = context.args[0]
    table.share(email)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Пользователю {} выдано разрешение на чтение".format(email))


async def send_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_document(chat_id=update.effective_chat.id, document="./contacts.csv")


async def send_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = table.get_url()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=url)


async def reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(type(update.effective_user.id))
    if str(update.effective_user.id) == os.getenv("ADMIN_ID"):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Привет повелитель")
    elif 'doc_send' not in context.user_data:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Нажмите на кнопку \"подтвердить\" для получения материалов.")


def main():
    load_dotenv()
    table = GoogleTable(os.getenv('TABLE_NAME'))
    app = Application.builder().token(os.getenv("BOT_TOKEN")).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('share_to', share))
    app.add_handler(CommandHandler('get_csv', send_csv))
    app.add_handler(CommandHandler('get_url', send_url))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reminder))
    app.add_handler(MessageHandler(filters.CONTACT, send_document))
    app.run_polling()


if __name__ == "__main__":
    main()