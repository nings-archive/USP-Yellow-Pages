from utils import *
from settings import Strings
import database

db = database.Connection()

def handle_onclick(bot, update):
    query = update.callback_query.data
    if query == 'cancel':
        pass
    elif 'renew' in query:
        # jobs.send_prompt_renew_msg
        mod_code = query.split(';')[1]
        old_entry = db.get_mod(mod_code)
        new_entry = list(old_entry)
        new_entry[2], new_entry[3] = get_dates()
        db.update_mod(*new_entry)
        send(bot, update, Strings.JOB_RENEW_OK)
    elif 'delete' in query:
        # jobs.send_prompt_renew_msg
        mod_code = query.split(';')[1]
        db.delete_mod(mod_code)
        send(bot, update, Strings.JOB_DELETE_OK)
    else:
        db.delete_mod(query)
        send(bot, update, Strings.BUTTON_REMOVE_GROUP_OK.format(query))
    # clean-up---delete inlinekeyboard, reset user state
    check_remove_ikey(bot, get_user_id(update), db)
