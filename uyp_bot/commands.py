from telegram import ParseMode
import database

HELP_TEXT = '''\
<i>USP Yellow Pages</i> is a directory for USP telegram study groups.

Commands:
/cancel -- Cancels the current multi-stage command
/help -- Display this help message
/about -- About this bot\
'''

ABOUT_TEXT = '''\
Submit PR/issues at on <a href="{url}">github</a>, or contact @ningyuan.\
'''.format(url='https://github.com/ningyuansg/USP-Yellow-Pages')

db = database.Connection()

def command_start(bot, update):
    command_help(bot, update)
    db.add_user(get_user_id(update))

def command_cancel(bot, update):
    state = db.get_user(get_user_id(update))[1]
    if state is None:
        bot.send_message(
            chat_id=get_chat_id(update),
            text=r"Okay, but I wasn't doing anything anyways ¯\_(ツ)_/¯"
        )
    else:
        bot.send_message(
            chat_id=get_chat_id(update),
            text="Command cancelled!"
        )
        db.update_user(get_user_id(update), None)

def command_help(bot, update):
    bot.send_message(
        chat_id=get_chat_id(update),
        parse_mode=ParseMode.HTML,
        text=HELP_TEXT
    )

def command_about(bot, update):
    bot.send_message(
        chat_id=get_chat_id(update),
        parse_mode=ParseMode.HTML,
        text=ABOUT_TEXT
    )

commands = [
    ('start' , command_start ),
    ('cancel', command_cancel),
    ('help'  , command_help  ),
    ('about' , command_about )
]

def get_chat_id(update):
    return update.message.chat_id

def get_user_id(update):
    return str(update.message.from_user.id)
