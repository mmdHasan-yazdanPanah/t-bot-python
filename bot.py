from telegram import Update
from telegram.ext import Application, ContextTypes, CommandHandler
from constants import token


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello there!')


def main() -> None:
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler('hello', hello))

    application.run_polling()


main()
