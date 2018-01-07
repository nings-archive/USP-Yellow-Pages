import re, datetime
from telegram import ParseMode
import telegram.ext
import sqlite3
import database

MOD_RE = '^[A-Z]{2,3}[0-9]{4}[A-Z]{0,1}$'
URL_RE = '^(https://t.me/joinchat/)[a-zA-Z0-9]*$'

MSG_CHAR_LIMIT = 4000  # max message len is 4096 UTF8 chars
RENEW_ALLOWANCE = datetime.timedelta(days=30)
REMOVE_ALLOWANCE = datetime.timedelta(days=60)

LIST_ALL_SCHEMA = '''\
<b>{mod_code}</b> (<a href="{url}">Invite link</a>)\
'''
LIST_ALL_IS_EMPTY = '''\
There doesn't seem to be anything here... \U0001f62d\
'''  # one teary boi

ADD_GROUP_MOD_PROMPT = '''\
Great! Send me the module code, e.g. <code>CS1101S</code>\
'''

CANCEL_STATE_NONE = '''\
Okay, but I wasn't doing anything anyways \
\u00af\u005c\u005f\u0028\u30c4\u0029\u005f\u002f\u00af\
'''  # one shruggy boi
CANCEL_STATE_SOME = '''\
Okie, cancelled!\
'''

RESPONSE_PROMPT_URL = '''\
Now, send me the <a href="{invite_url}">invite link</a>. \
It should look something like this: {sample_url}\
'''.format(
    invite_url='https://telegram.org/blog/invite-links',
    sample_url='https://t.me/joinchat/BLAivEHRggkWpKez7GZ8hw'
)
RESPONSE_INVALID_MOD = '''\
That doesn't seem to be a valid module code \U0001f617\
'''  # one -3- boi
RESPONSE_INVALID_URL = '''\
That doesn't seem to be a valid url \U0001f617\
'''  # one -3- boi
RESPONSE_ALREADY_MOD = '''\
Looks like there's already a group for this mod. \
Enter another module code, or /cancel this command.\
'''
RESPONSE_ALREADY_URL = '''\
Looks like this url has already been linked to a mod. \
Check if you have copy-pasted correctly, or /cancel this command.\
'''

HELP_TEXT = '''\
<b>USP Yellow Pages</b> is a directory for USP telegram study groups.

Commands:
/list_all -- Lists all groups
/add_group -- Add a group to the directory
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

def command_list_all(bot, update):
    mods = db.get_mods_reg('')
    mod_strings = [ 
        LIST_ALL_SCHEMA.format(mod_code=mod[1], url=mod[0]) 
        for mod in mods
    ]
    if mod_strings == []:
        bot.send_message(
            chat_id=get_chat_id(update),
            text=LIST_ALL_IS_EMPTY
        )
    else:
        messages = [ mod_strings[0] ]
        for mod_string in mod_strings[1:]:
            if len(messages[-1]) < MSG_CHAR_LIMIT:
                messages[-1] += ('\n' + mod_string)
            else:
                messages.append(mod_string)
        for message in messages:
            bot.send_message(
                chat_id=get_chat_id(update),
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
                text=message
            )

def command_add_group(bot, update):
    db.update_user(get_user_id(update), 'add_group@code', None, None)
    bot.send_message(
        chat_id=get_chat_id(update),
        parse_mode=ParseMode.HTML,
        text=ADD_GROUP_MOD_PROMPT
    )

def command_cancel(bot, update):
    state = db.get_user(get_user_id(update))[1]
    if state is None:
        bot.send_message(
            chat_id=get_chat_id(update),
            text=CANCEL_STATE_NONE
        )
    else:
        bot.send_message(
            chat_id=get_chat_id(update),
            text=CANCEL_STATE_SOME
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
        disable_web_page_preview=True,
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
                text=RESPONSE_PROMPT_URL
            )
        except ValueError:
            bot.send_message(
                chat_id=get_chat_id(update),
                text=RESPONSE_INVALID_MOD
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
                text=RESPONSE_INVALID_URL
            )
        except sqlite3.IntegrityError as e:
            if 'code' in str(e):
                bot.send_message(
                    chat_id=get_chat_id(update),
                    text=RESPONSE_ALREADY_MOD
                )
                db.update_user(
                    get_user_id(update), 'add_group@code',
                    None, None
                )
            elif 'url' in str(e):
                bot.send_message(
                    chat_id=get_chat_id(update),
                    text=RESPONSE_ALREADY_URL
                )

commands = [
    ( 'start'     , command_start     ),
    ( 'list_all'  , command_list_all  ),
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
