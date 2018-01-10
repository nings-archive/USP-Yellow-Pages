import datetime
import telegram
import database
from utils import *
from settings import Strings

db = database.Connection()

def job_prompt_renew(bot, job):
    today = datetime.datetime.now().date()
    mods_all = db.get_mods_reg('')
    mods_to_renew = list(filter(
        lambda xs: get_date_from_str(xs[2]) < today, mods_all))
    for mod in mods_to_renew:
        send_prompt_renew_msg(bot, mod)

def send_prompt_renew_msg(bot, mod):
    user_id, expiry, mod_code = mod[4], mod[3], mod[1]
    check_remove_ikey(bot, user_id, db)
    buttons = [
        [telegram.InlineKeyboardButton(
            text='Renew', callback_data='renew;'+mod_code)],
        [telegram.InlineKeyboardButton(
            text='Delete', callback_data='delete;'+mod_code)],
        [telegram.InlineKeyboardButton(
            text='Cancel', callback_data='cancel')]
    ]
    msg = bot.send_message(
        chat_id=user_id,
        text=Strings.JOB_PROMPT_RENEW.format(mod_code, expiry),
        parse_mode=telegram.ParseMode.HTML,
        reply_markup=telegram.InlineKeyboardMarkup(buttons)
    )
    db.update_user(user_id, 'prompt_renew@keyboard',
        None, str(msg.message_id))

def job_remove(bot, job):
    today = datetime.datetime.now().date()
    mods_all = db.get_mods_reg('')
    mods_to_remove = list(filter(
        lambda xs: get_date_from_str(xs[3]) < today, mods_all))
    for mod in mods_to_remove:
        check_remove_ikey(bot, mod[4], db)
        db.delete_mod(mod[1])
        bot.send_message(
            chat_id=mod[4], 
            parse_mode=telegram.ParseMode.HTML,
            text=Strings.JOB_REMOVED.format(mod[1])
        )

daily_jobs = [
    {'callback': job_prompt_renew, 'time': settings.JOB_EXECUTE_TIME},
    {'callback': job_remove,       'time': settings.JOB_EXECUTE_TIME}
]
