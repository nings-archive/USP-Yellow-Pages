import re, datetime
from telegram import ParseMode
import telegram.ext
import sqlite3
import database

MOD_RE = '^[A-Z]{2,3}[0-9]{4}[A-Z]{0,1}$'
URL_RE = '^(https://t.me/joinchat/)[a-zA-Z0-9]*$'

RENEW_ALLOWANCE = datetime.timedelta(days=30)
REMOVE_ALLOWANCE = datetime.timedelta(days=60)

INVITE_LINK_PROMPT = '''\
Now, send me the <a href="{invite_url}">invite link</a>. \
It should look something like this: {sample_url}\
'''.format(
    invite_url='https://telegram.org/blog/invite-links',
    sample_url='https://t.me/joinchat/BLAivEHRggkWpKez7GZ8hw'
)

HELP_TEXT = '''\
<b>USP Yellow Pages</b> is a directory for USP telegram study groups.

Commands:
/add_group -- Add a group to the <i>Yellow Pages</i>
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

def command_add_group(bot, update):
    db.update_user(get_user_id(update), 'add_group@code', None, None)
    bot.send_message(
        chat_id=get_chat_id(update),
        parse_mode=ParseMode.HTML,
        text="Great! Send me the module code, e.g. <code>CS1101S</code>"
    )

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
        db.update_user(get_user_id(update), None, None, None)

def command_help(bot, update):
    bot.send_message(
        chat_id=get_chat_id(update),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
        text=HELP_TEXT
    )

def command_about(bot, update):
    bot.send_message(
        chat_id=get_chat_id(update),
        parse_mode=ParseMode.HTML,
        text=ABOUT_TEXT
    )

def handle_command_response(bot, update):
    user_id, state, code_temp, url_temp = db.get_user(get_user_id(update))
    if state is None:
        pass
    elif state == 'add_group@code':
        try:
            db.update_user(
                get_user_id(update), 'add_group@url',
                sanitise_mod(get_message_text(update)), None
            )
            bot.send_message(
                chat_id=get_chat_id(update),
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
                text=INVITE_LINK_PROMPT
            )
        except ValueError:
            bot.send_message(
                chat_id=get_chat_id(update),
                text="That doesn't seem to be a valid module code...?"
            )
    elif state == 'add_group@url':
        try:
            url = sanitise_url(get_message_text(update))
            renew_date, remove_date = get_dates()
            mod = db.get_user(get_user_id(update))[2]
            db.add_mod(url, mod, renew_date, remove_date, get_user_id(update))
            db.update_user(get_user_id(update), None, None, None)
            bot.send_message(chat_id=get_chat_id(update), text='Success!')
        except ValueError:
            bot.send_message(
                chat_id=get_chat_id(update),
                text="That doesn't seem to be a valid invite url...?"
            )
        except sqlite3.IntegrityError as e:
            if 'code' in str(e):
                bot.send_message(
                    chat_id=get_chat_id(update),
                    text="Looks like there's already a group for this mod. Enter another module code, or /cancel this command."
                )
                db.update_user(
                    get_user_id(update), 'add_group@code',
                    None, None
                )
            elif 'url' in str(e):
                bot.send_message(
                    chat_id=get_chat_id(update),
                    text="Looks like this group has already been linked to a mod. Check if you have copy-pasted correctly, or /cancel this command."
                )

commands = [
    ( 'start'     , command_start     ),
    ( 'add_group' , command_add_group ),
    ( 'cancel'    , command_cancel    ),
    ( 'help'      , command_help      ),
    ( 'about'     , command_about     )
]
message_handlers = [
    ( telegram.ext.Filters.text, handle_command_response )
]

def get_chat_id(update):
    return update.message.chat_id

def get_user_id(update):
    return str(update.message.from_user.id)

def get_message_text(update):
    return update.message.text

def get_dates():
    today = datetime.date.today()
    renew = today + RENEW_ALLOWANCE
    remove = today + REMOVE_ALLOWANCE
    return renew.isoformat(), remove.isoformat()

def sanitise_mod(mod):
    mod = mod.strip().upper()
    match = re.match(MOD_RE, mod)
    if match is not None:
        return mod
    else:
        raise ValueError('Invalid module code')

def sanitise_url(url):
    url = url.strip()
    match = re.match(URL_RE, url)
    if match is not None:
        return url
    else:
        raise ValueError('Invalid url')
