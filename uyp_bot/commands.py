import re, datetime
from telegram import ParseMode
import sqlite3, telegram.ext, telegram.error
import database
from settings import Strings

# TODO: all commands must remove past inlinequeries

MOD_RE = '^[A-Z]{2,3}[0-9]{4}[A-Z]{0,1}$'
URL_RE = '^(https://t.me/joinchat/)[a-zA-Z0-9]*$'

MSG_CHAR_LIMIT = 4000  # max message len is 4096 UTF8 chars
RENEW_ALLOWANCE = datetime.timedelta(days=30)
REMOVE_ALLOWANCE = datetime.timedelta(days=60)

db = database.Connection()

def command_start(bot, update):
    check_remove_ikey(bot, update)
    command_help(bot, update)
    db.add_user(get_user_id(update))

def command_list_all(bot, update):
    check_remove_ikey(bot, update)
    mods = db.get_mods_reg('')
    mod_strings = [ 
        Strings.LIST_ALL_SCHEMA.format(mod_code=mod[1], url=mod[0]) 
        for mod in mods
    ]
    if mod_strings == []:
        send(bot, update, Strings.LIST_ALL_IS_EMPTY)
    else:
        messages = [ mod_strings[0] ]
        for mod_string in mod_strings[1:]:
            if len(messages[-1]) < MSG_CHAR_LIMIT:
                messages[-1] += ('\n' + mod_string)
            else:
                messages.append(mod_string)
        for message in messages:
            send(bot, update, message)

def command_add_group(bot, update):
    check_remove_ikey(bot, update)
    db.update_user(get_user_id(update), 'add_group@code', None, None)
    send(bot, update, Strings.ADD_GROUP_MOD_PROMPT)

def command_remove_group(bot, update):
    check_remove_ikey(bot, update)
    mods = db.get_users_mods(get_user_id(update))
    if mods == []:
        send(bot, update, Strings.REMOVE_GROUP_NONE)
    else:
        mod_strs = [ mod[1] for mod in mods ]
        msg = bot.send_message(
            chat_id=get_chat_id(update),
            text=Strings.REMOVE_GROUP_SOME,
            reply_markup=telegram.InlineKeyboardMarkup(
                build_ikey_markup(mod_strs)
            )
        )
        db.update_user(get_user_id(update), 'remove_group@keyboard',
            None, str(msg.message_id))

def button_remove_group(bot, update):
    query = update.callback_query.data
    if query == 'cancel':
        pass
    else:
        db.delete_mod(query)
        send(bot, update, Strings.BUTTON_REMOVE_GROUP_OK.format(query))
    # clean-up---delete inlinekeyboard, reset user state
    check_remove_ikey(bot, update)

def command_cancel(bot, update):
    check_remove_ikey(bot, update)
    state = db.get_user(get_user_id(update))[1]
    if state is None:
        send(bot, update, Strings.CANCEL_STATE_NONE)
    else:
        send(bot, update, Strings.CANCEL_STATE_SOME)
        db.update_user(get_user_id(update), None, None, None)

def command_help(bot, update):
    check_remove_ikey(bot, update)
    send(bot, update, Strings.HELP_TEXT)

def command_about(bot, update):
    check_remove_ikey(bot, update)
    send(bot, update, Strings.ABOUT_TEXT)

def response_handler(bot, update):
    check_remove_ikey(bot, update)
    user_id, state, code_temp, url_temp = db.get_user(get_user_id(update))
    if state is None:
        pass
    elif state == 'add_group@code':
        try:
            db.update_user(
                get_user_id(update), 'add_group@url',
                sanitise_mod(get_message_text(update)), None
            )
            send(bot, update, Strings.RESPONSE_PROMPT_URL)
        except ValueError:
            send(bot, update, Strings.RESPONSE_INVALID_MOD)
    elif state == 'add_group@url':
        try:
            url = sanitise_url(get_message_text(update))
            renew_date, remove_date = get_dates()
            mod = db.get_user(get_user_id(update))[2]
            db.add_mod(
                url, mod, renew_date, remove_date, get_user_id(update))
            db.update_user(get_user_id(update), None, None, None)
            send(bot, update, Strings.RESPONSE_SUCCESS)
        except ValueError:
            send(bot, update, Strings.RESPONSE_INVALID_URL)
        except sqlite3.IntegrityError as e:
            if 'code' in str(e):
                send(bot, update, Strings.RESPONSE_ALREADY_MOD)
                db.update_user(
                    get_user_id(update), 'add_group@code',
                    None, None
                )
            elif 'url' in str(e):
                send(bot, update, Strings.RESPONSE_ALREADY_URL)

commands = [
    ( 'start'        , command_start        ),
    ( 'list_all'     , command_list_all     ),
    ( 'add_group'    , command_add_group    ),
    ( 'remove_group' , command_remove_group ),
    ( 'cancel'       , command_cancel       ),
    ( 'help'         , command_help         ),
    ( 'about'        , command_about        )
]
message_handlers = [
    ( telegram.ext.Filters.text, response_handler )
]
callback_handler = button_remove_group

def send(bot, update, message):
    bot.send_message(
        chat_id=get_chat_id(update),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
        text=message
    )

def check_remove_ikey(bot, update):
    old_entry = db.get_user(get_user_id(update))
    ikey_msg_id = old_entry[3]
    if ikey_msg_id is not None:
        try:
            bot.delete_message(
                chat_id=get_chat_id(update), 
                message_id=int(ikey_msg_id)
            )
        except telegram.error.BadRequest:
            # If this ever happens, and is uncaught, users will be
            #     locked out forever
            pass
        new_entry = list(old_entry)
        new_entry[3] = None
        db.update_user(*new_entry)

def get_chat_id(update):
    if update.message is not None:
        return str(update.message.chat_id)
    else:
        return str(update.callback_query.from_user.id)

def get_user_id(update):
    if update.message is not None:
        return str(update.message.from_user.id)
    else:
        return str(update.callback_query.from_user.id)

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

def build_ikey_markup(mods):
    buttons = [ 
        [telegram.InlineKeyboardButton(text=mod, callback_data=mod)]
        for mod in mods 
    ]
    buttons.append([ telegram.InlineKeyboardButton(
        text='Cancel', callback_data='cancel') ])
    return buttons
