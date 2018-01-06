from telegram import ParseMode

HELP_TEXT = '''\
<i>USP Yellow Pages</i> is a directory for USP telegram study groups.

Commands:
/help -- Display this help message
/about -- About this bot\
'''

ABOUT_TEXT = '''\
Submit PR/issues at on <a href="{url}">github</a>, or contact @ningyuan.\
'''.format(url='https://github.com/ningyuansg/USP-Yellow-Pages')

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
    ('start', command_help),
    ('help' , command_help),
    ('about', command_about)
]

def get_chat_id(update):
    return update.message.chat_id
