from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, ContextTypes, PicklePersistence, CommandHandler, ConversationHandler, MessageHandler, filters
from constants import token

START_ADD_EVENT, TYPE_EVENT = range(2)
START_ADD_USER, TYPING_USER = range(2)
SWITH_EVENT_START, SWITCH_EVENT_TYPE = range(2)
START_TRANSACTION, TYPE_TRANSACTION_NAME, CHOOSE_USERS, ENTER_PRICE, USER_PRICE = range(
    5)
TRANSFER_START, TRANSFER_TYPE, TRANSFER_SENDER, TRANSFER_PRICE, TRANSFER_RECIVER = range(
    5)


async def show_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '/add_event -> To Add Event\n'
        '/add_user -> To Add User to current Event\n'
        '/switch_event -> To Switch Event\n'
        '/show_status -> To Show Users Accoutn Status in current event\n'
        '/transfer -> Transfer money throgh current Event\n'
        '/export_status -> To export paiment status in a file\n'
        '/add_transaction -> To Add Transaction to current event\n'
        '/cancel -> To cancel current job',
        reply_markup=ReplyKeyboardRemove()
    )


async def add_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Type Your Event name:\n or use /cancel to stop making event', reply_markup=ReplyKeyboardRemove())

    return TYPE_EVENT


async def type_event_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    event = update.message.text

    if ('events' in context.user_data):
        if (event in context.user_data['events']):
            await update.message.reply_text('This Event already exists. Try a new name:\nor use /cancel to stop making event')
            return TYPE_EVENT
    else:
        context.user_data['events'] = {}

    context.user_data['events'][event] = {
        'name': event, 'users': {}, 'transactions': [], 'transfers': []}
    context.user_data['active-event'] = context.user_data['events'][event]

    await update.message.reply_text(f'Event {event} Successfully added.\nNow Try Adding Your Users to it with /add_user:')
    return ConversationHandler.END


async def swith_event_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if ('events' not in context.user_data):
        await update.message.reply_text(
            'You have no event\n'
            'Try Adding one with /add_event',
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    events = list(context.user_data['events'].keys())
    active_event = context.user_data['active-event']['name']

    if (len(events) == 1):
        await update.message.reply_text(
            'You have only 1 event\n'
            'Try Adding another with /add_event',
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    await update.message.reply_text(
        f'Current event is: {active_event}\n'
        'Choose one event to swith:\n'
        'or hit /cancel to stop switching',
        reply_markup=ReplyKeyboardMarkup([events])
    )
    return SWITCH_EVENT_TYPE


async def switch_event_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    event = update.message.text

    events = list(context.user_data['events'].keys())

    if (event not in events):
        await update.message.reply_text(
            'This event not exist\n'
            'Try Choosing an event:',
            reply_markup=ReplyKeyboardMarkup([events])
        )
        return SWITCH_EVENT_TYPE

    context.user_data['active-event'] = context.user_data['events'][event]

    await update.message.reply_text(f'Successfully switched to event "{event}"', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


async def show_status(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if ('events' not in context.user_data):
        await update.message.reply_text(
            'You have no event\n'
            'Try Adding one with /add_event',
            reply_markup=ReplyKeyboardRemove()
        )
        return

    active_event = context.user_data['active-event']
    active_event_name = context.user_data['active-event']['name']
    users_string = str(active_event['users'])
    t_string = str(active_event['transactions'])

    await update.message.reply_text(
        f'Current event is: "{active_event_name}"\n\n'
        f'Sum: {users_string}\n\n'
        'Transaction Details: \n'
        f'{t_string}',
        reply_markup=ReplyKeyboardRemove()
    )


async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if ('active-event' not in context.user_data):
        await update.message.reply_text(
            'No Active-event found\n'
            'Try /add_event to create one',
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    await update.message.reply_text(
        'Type username:\n'
        'use /cancel to stop adding user.',
        reply_markup=ReplyKeyboardRemove()
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

    if (username == 'Done'):
        await update.message.reply_text(
            'username cannot be "Done" \n'
            'Try Adding another User with /add_user\n'
            'Try Adding Transaction with /add_transaction'
        )
        return ConversationHandler.END

    active_event['users'][username] = 0
    await update.message.reply_text(
        f'User {username} successfully added.\n'
        'Try Adding another User with /add_user\n'
        'Try Adding Transaction with /add_transaction'
    )
    return ConversationHandler.END


async def add_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if ('active-event' not in context.user_data):
        await update.message.reply_text(
            'No Active-event found\n'
            'Try /add_event to create one',
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    active_event = context.user_data['active-event']
    users = list(active_event['users'].keys())

    if (len(users) == 0):
        await update.message.reply_text(
            'No Users found\n'
            'Try /add_user to create one',
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    await update.message.reply_text(
        'Type Transaction name: \n'
        'use /cancel to stop adding transaction.',
        reply_markup=ReplyKeyboardRemove()
    )

    return TYPE_TRANSACTION_NAME


async def type_transaction_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    t_name = update.message.text

    if (t_name in context.user_data['active-event']['transactions']):
        await update.message.reply_text(
            f'Transaction {t_name} already exists, Try a new name for your transaction:'
            'Or use /cancel to stop adding transaction'
        )
        return TYPE_TRANSACTION_NAME

    transaction = {'users': {}, 'price': None, 'name': t_name}
    active_event = context.user_data['active-event']
    users = list(active_event['users'].keys())
    print('type name t')
    print(users)
    context.user_data['active-transaction'] = transaction

    markup = ReplyKeyboardMarkup(
        [users],
        one_time_keyboard=True,
        input_field_placeholder="Choose member:"
    )

    await update.message.reply_text(
        f'Transaction {t_name} successfully added. Now Try Adding user participants:',
        reply_markup=markup
    )

    return CHOOSE_USERS


async def add_user_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text
    active_event = context.user_data['active-event']
    users = list(active_event['users'].keys())
    active_t = context.user_data['active-transaction']

    added_users = list(active_t['users'].keys())
    filtered_users = list(filter(lambda u: u not in added_users, users))

    if (len(added_users) > 0):
        markup = ReplyKeyboardMarkup(
            [filtered_users, ['Done']],
            one_time_keyboard=True,
            input_field_placeholder="Choose member:"
        )
    else:
        markup = ReplyKeyboardMarkup(
            [filtered_users],
            one_time_keyboard=True,
            input_field_placeholder="Choose member:"
        )

    if (username not in users):
        await update.message.reply_text(
            'This User Does not exist \n'
            'Try Choosing from Existing users \n'
            'Or Adding User with /add_user command',
            reply_markup=markup
        )
        return CHOOSE_USERS

    if (username in added_users):
        await update.message.reply_text('This User already added, Try Adding another User:', reply_markup=markup)
        return CHOOSE_USERS

    active_t['users'][username] = 0
    added_users = list(active_t['users'].keys())
    filtered_users = list(filter(lambda u: u not in added_users, users))

    print('added user to tr')
    print(context.user_data)

    markup = ReplyKeyboardMarkup(
        [filtered_users, ['Done']],
        one_time_keyboard=True,
        input_field_placeholder="Choose member:"
    )

    await update.message.reply_text(
        f'User {username} successfully added \n'
        'Try Adding another user participant:',
        reply_markup=markup
    )

    return CHOOSE_USERS


async def finish_add_user_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Users successfully added to transaction.\n'
        'Now Try Entering the price:',
        reply_markup=ReplyKeyboardRemove()
    )

    return ENTER_PRICE


async def enter_price(update: Update, context: ContextTypes):
    t_price = update.message.text

    if not (t_price.isnumeric()):
        await update.message.reply_text(
            'You Have entered a non numeric value'
            'Please Enter a number as price:'
        )

        return ENTER_PRICE

    active_t = context.user_data['active-transaction']
    users = list(active_t['users'].keys())

    price = float(t_price)
    active_t['price'] = price

    print('added Price')
    print(context.user_data)

    context.user_data['active_user_index'] = 0

    await update.message.reply_text(
        'Price saved.\n'
        'Now Pick a share for Every User, \n'
        f'How much User "{users[0]}" paid?'
    )

    return USER_PRICE


async def enter_user_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    t_price = update.message.text

    active_t = context.user_data['active-transaction']
    t_users = active_t['users']
    active_event = context.user_data['active-event']
    users = list(t_users.keys())
    active_user_index = context.user_data['active_user_index']
    active_user = users[active_user_index]
    each_share_price = active_t['price'] / len(users)

    if not (t_price.isnumeric()):
        await update.message.reply_text(
            'You Have entered a non numeric value'
            'Please Enter a number as price:'
            f'How much User "{active_user}" paid?'
        )
        return USER_PRICE

    price = float(t_price)
    active_t['users'][active_user] = price - each_share_price

    print('user share added')
    print(context.user_data)

    if (active_user_index + 1 == len(users)):
        event_users = active_event['users']

        for u_t in t_users:
            event_users[u_t] += t_users[u_t]

        active_event['transactions'].append(active_t)
        users_string = str(event_users)

        await update.message.reply_text(
            'Excelent, Now All shares acounted\n'
            'Now Users state in this event with considering of this transaction are:\n'
            f'{users_string}'
        )

        return ConversationHandler.END

    context.user_data['active_user_index'] += 1
    active_user = users[active_user_index + 1]

    await update.message.reply_text(
        'Share succesfully Added '
        f'How much User "{active_user}" paid?',
    )
    return USER_PRICE


async def start_transfer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if ('events' not in context.user_data):
        await update.message.reply_text(
            'You have no event\n'
            'Try Adding one with /add_event',
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    event = context.user_data['active-event']
    event_name = event['name']
    users = list(event['users'].keys())

    if (len(users) < 2):
        await update.message.reply_text(
            f'You have fewer than 2 users in event "{event_name}"\n'
            'Try adding user with /add_user',
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    await update.message.reply_text(
        'Type Transfer name:\n\n'
        'Or canecl transfer with with /cancel',
        reply_markup=ReplyKeyboardRemove()
    )
    return TRANSFER_TYPE


async def type_transfer_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    t_name = update.message.text

    context.user_data['active-transfer'] = {
        'name': t_name,
        'sender': None,
        'reciver': None,
        'price': None
    }

    active_event = context.user_data['active-event']
    users = active_event['users']
    users_list = list(users.keys())

    await update.message.reply_text(
        f'Transfer name "{t_name}" added\n'
        'Now Choose the sender user:\n\n'
        'or cancel with /cancel',
        reply_markup=ReplyKeyboardMarkup([users_list])
    )
    return TRANSFER_SENDER


async def sender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text

    active_event = context.user_data['active-event']
    users = active_event['users']
    users_list = list(users.keys())

    if (username not in users):
        await update.message.reply_text(
            'This user does not exist, Try Choosing a user:\n\n'
            'or cancel with /cancel',
            reply_markup=ReplyKeyboardMarkup([users_list])

        )
        return TRANSFER_SENDER

    transfer = context.user_data['active-transfer']
    transfer['sender'] = username

    await update.message.reply_text(
        'Sender successfully added\n'
        'Now type the Price to transfer:\n\n'
        'or cancel with /cancel',
        reply_markup=ReplyKeyboardRemove()
    )
    return TRANSFER_PRICE


async def transfer_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    t_price = update.message.text

    if not (t_price.isnumeric()):
        await update.message.reply_text(
            'You Have entered a non numeric value'
            'Please Enter a number as price:'
        )
        return TRANSFER_PRICE

    price = float(t_price)
    active_event = context.user_data['active-event']
    users = active_event['users']
    transfer = context.user_data['active-transfer']
    filtered_users = list(filter(lambda u: (u != transfer['sender']), users))
    transfer['price'] = price

    await update.message.reply_text(
        'Price successfully added\n'
        'Now Choose the reciver to transfer:\n\n'
        'or cancel with /cancel',
        reply_markup=ReplyKeyboardMarkup([filtered_users])
    )
    return TRANSFER_RECIVER


async def reciver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    r_name: update.message.text

    active_event = context.user_data['active-event']
    users = active_event['users']
    transfer = context.user_data['active-transfer']
    filtered_users = list(
        filter(lambda u: (u != transfer['sender']), users))

    if (r_name not in users):
        await update.message.reply_text(
            'This user does not exist, Try Choosing a user:\n\n'
            'or cancel with /cancel',
            reply_markup=ReplyKeyboardMarkup([filtered_users])

        )
        return TRANSFER_RECIVER

    if (r_name == transfer['sender']):
        await update.message.reply_text(
            'User sender and reciver cannot be the same\n'
            'Try Choosing a user:\n\n'
            'or cancel with /cancel',
            reply_markup=ReplyKeyboardMarkup([filtered_users])
        )
        return TRANSFER_RECIVER

    transfer['reciver'] = r_name
    users[transfer['sender']] += transfer['price']
    users[transfer['reciver']] -= transfer['price']
    active_event['transfers'].append(transfer)
    del active_event['active-transfer']

    users_string = str(active_event['users'])

    await update.message.reply_text(
        'Transfer is Done.'
        'Users status:\n'
        f'{users_string}',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if ('active-transaction' in context.user_data):
        del context.user_data['active-transaction']

    if ('active-transfer' in context.user_data):
        del context.user_data['active-transfer']

    await update.message.reply_text(
        'Canceled job\n'
        'Try Use /show_commands To see commands',
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    persistence = PicklePersistence(filepath="conversationbot")
    application = Application.builder().token(
        token).persistence(persistence).build()

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
        entry_points=[CommandHandler('switch_event', swith_event_start)],
        states={
            SWITCH_EVENT_TYPE: [MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                switch_event_type
            )]
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

    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler('add_transaction', add_transaction)],
        states={
            TYPE_TRANSACTION_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, type_transaction_name)],
            CHOOSE_USERS: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND |
                                     filters.Regex('^Done$')),
                    add_user_transaction
                ),
                MessageHandler(filters.Regex('^Done$'),
                               finish_add_user_transaction)
            ],
            ENTER_PRICE: [MessageHandler(filters.TEXT & ~(filters.COMMAND), enter_price)],
            USER_PRICE: [MessageHandler(filters.TEXT & ~(filters.COMMAND), enter_user_price)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    ))

    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler('transfer', start_transfer)],
        states={
            TRANSFER_TYPE: [MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                type_transfer_name
            )],
            TRANSFER_SENDER: [MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                sender
            )],
            TRANSFER_PRICE: [MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                transfer_price
            )],
            TRANSFER_RECIVER: [MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                reciver
            )]
        },
        fallbacks=[CommandHandler('cancel', cancel)]

    ))

    application.add_handler(CommandHandler('show_status', show_status))

    application.run_polling()


main()
