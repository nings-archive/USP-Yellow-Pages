import datetime, re
import telegram
from telegram import ParseMode
import settings

MOD_RE = '^[A-Z]{2,3}[0-9]{4}[A-Z]{0,1}$'
URL_RE = '^(https://t.me/joinchat/)[a-zA-Z0-9]*$'

def restrict_to(pred, err_msg):
    '''Returns a decorator, i.e. decorator factory'''
    def decorator(func):
        def modified_func(bot, update):
            if pred(update):
                return func(bot,update)
            else:
                bot.send_message(
                    chat_id=get_chat_id(update),
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                    text=err_msg
                )
        return modified_func
    return decorator

def is_private_message(update):
    '''Pred for decorator factory restrict_to'''
    return update.message.from_user.id == update.message.chat_id

def has_added_groups(db):
    '''Pred for decorator factory restrict_to'''
    # db is in the namespace of commands module, so curry this func
    def inner(update):
        mods = db.get_users_mods(get_user_id(update))
        return mods != []
    return inner

def send(bot, update, message):
    bot.send_message(
        chat_id=get_chat_id(update),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
        text=message
    )

def check_remove_ikey(bot, user_id, db):
    old_entry = db.get_user(user_id)
    ikey_msg_id = old_entry[3]
    if ikey_msg_id is not None:
        try:
            bot.delete_message(chat_id=user_id, message_id=int(ikey_msg_id))
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
    renew = today + settings.RENEW_ALLOWANCE
    remove = today + settings.REMOVE_ALLOWANCE
    return renew.isoformat(), remove.isoformat()

def get_date_from_str(datetime_str):
    return datetime.datetime.strptime(datetime_str, '%Y-%m-%d').date()

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
