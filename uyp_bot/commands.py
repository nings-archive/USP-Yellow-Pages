import sqlite3, telegram.ext, telegram.error
import database
from settings import Strings
from utils import *

MSG_CHAR_LIMIT = 3000  # max message len is 4096 UTF8 chars

db = database.Connection()

def command_start(bot, update):
    check_remove_ikey(bot, get_user_id(update), db)
    command_help(bot, update)
    db.add_user(get_user_id(update))

def command_list_all(bot, update):
    check_remove_ikey(bot, get_user_id(update), db)
    mods = db.get_mods_reg('')
    mod_strings = [ 
        Strings.LIST_ALL_SCHEMA.format(mod_code=mod[1], url=mod[0]) 
        for mod in mods
    ]
    if mod_strings == []:
        send(bot, update, Strings.LIST_ALL_IS_EMPTY)
    else:
        mod_strings.sort()
        messages = [ mod_strings[0] ]
        for mod_string in mod_strings[1:]:
            if len(messages[-1]) < MSG_CHAR_LIMIT:
                messages[-1] += ('\n' + mod_string)
            else:
                messages.append(mod_string)
        for message in messages:
            send(bot, update, message)

@restrict_to(is_private_message, Strings.ADD_GROUP_PM_ONLY)
def command_add_group(bot, update):
    check_remove_ikey(bot, get_user_id(update), db)
    db.update_user(get_user_id(update), 'add_group@code', None, None)
    send(bot, update, Strings.ADD_GROUP_MOD_PROMPT)

@restrict_to(is_private_message, Strings.REMOVE_GROUP_PM_ONLY)
@restrict_to(has_added_groups(db), Strings.REMOVE_GROUP_NONE)
def command_remove_group(bot, update):
    check_remove_ikey(bot, get_user_id(update), db)
    mods = db.get_users_mods(get_user_id(update))
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

def command_cancel(bot, update):
    check_remove_ikey(bot, get_user_id(update), db)
    state = db.get_user(get_user_id(update))[1]
    if state is None:
        send(bot, update, Strings.CANCEL_STATE_NONE)
    else:
        send(bot, update, Strings.CANCEL_STATE_SOME)
        db.update_user(get_user_id(update), None, None, None)

def command_help(bot, update):
    check_remove_ikey(bot, get_user_id(update), db)
    send(bot, update, Strings.HELP_TEXT)

def command_about(bot, update):
    check_remove_ikey(bot, get_user_id(update), db)
    send(bot, update, Strings.ABOUT_TEXT)

def response_handler(bot, update):
    check_remove_ikey(bot, get_user_id(update), db)
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
