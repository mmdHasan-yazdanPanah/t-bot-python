from telegram import Update, ForceReply
from telegram.ext import Application, ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters
from constants import token

START_ADD_EVENT, TYPE_EVENT = range(2)
START_ADD_USER, TYPING_USER = range(2)


async def show_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '/add_event -> To Add Event\n'
        '/add_user -> To Add User to current Event\n'
        '/show_events -> To Show and Switch current event\n'
        '/add_transaction -> To Add Transaction to current event\n'
        '/cancel -> To cancel current job',
    )


async def add_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Type Your Event name:\n or use /cancel to stop making event')

    return TYPE_EVENT


async def type_event_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    event = update.message.text

    if ('events' in context.user_data):
        if (event in context.user_data['events']):
            await update.message.reply_text('This Event already exists. Try a new name:\nor use /cancel to stop making event')
            return TYPE_EVENT
    else:
        context.user_data['events'] = {}

    context.user_data['events'][event] = {'users': [], 'transactions': []}
    context.user_data['active-event'] = context.user_data['events'][event]

    await update.message.reply_text(f'Event {event} Successfully added.\nNow Try Adding Your Users to it with /add_user:')
    return ConversationHandler.END


async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if ('active-event' not in context.user_data):
        await update.message.reply_text(
            'No Active-event found\n'
            'Try /add_event to create one',
        )
        return ConversationHandler.END

    await update.message.reply_text(
        'Type username:\n'
        'use /cancel to stop adding user.'
    )
    return TYPING_USER


async def type_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text
    active_event = context.user_data['active-event']

    if (username in active_event['users']):
        await update.message.reply_text(
            'This user currently exists\n'
            'Try Adding another User with /add_user\n'
            'Try Adding Transaction with /add_transaction'
        )
        return ConversationHandler.END

    active_event['users'].append(username)
    await update.message.reply_text(
        f'User {username} successfully added.\n'
        'Try Adding another User with /add_user\n'
        'Try Adding Transaction with /add_transaction'
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Canceled job\n'
        'Try Use /show_commands To see commands',
    )
    return ConversationHandler.END


def main() -> None:
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler('start', show_commands))
    application.add_handler(CommandHandler('help', show_commands))
    application.add_handler(CommandHandler('show_commands', show_commands))

    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler('add_event', add_event)],
        states={
            TYPE_EVENT: [MessageHandler(
                filters.TEXT & ~filters.COMMAND, type_event_name)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    ))

    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler('add_user', add_user)],
        states={
            TYPING_USER: [MessageHandler(
                filters.TEXT & ~filters.COMMAND, type_user)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]

    ))

    application.run_polling()


main()
