from telegram import Update, ForceReply
from telegram.ext import Application, ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters
from constants import token

ADD_USER, TYPE_ADD_USER = range(2)


async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Type Your Username:', reply_markup=ForceReply())

    return TYPE_ADD_USER


async def type_add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if ('users' not in context.user_data):
        context.user_data['users'] = []
    username = update.message.text
    context.user_data['users'].append(username)
    print(context.user_data['users'])
    await update.message.reply_text(f'User {username} Added')


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Canceled job')


def main() -> None:
    application = Application.builder().token(token).build()

    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler('add_user', add_user)],
        states={
            TYPE_ADD_USER: [MessageHandler(filters.TEXT, type_add_user)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    ))

    application.run_polling()


main()
