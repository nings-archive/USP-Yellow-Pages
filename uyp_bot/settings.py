import datetime
from os import path
from configparser import ConfigParser

PACKAGE_DIR = path.dirname(path.realpath(__file__))
PROJECT_DIR = path.split(PACKAGE_DIR)[0]
VOLUME_DIR = path.join(PROJECT_DIR, 'volume')

FILENAME_CONFIG = path.join(PROJECT_DIR, 'volume/config.ini')
FILENAME_DB = path.join(VOLUME_DIR, 'uyp.db')

CONFIG = ConfigParser()
CONFIG.read(FILENAME_CONFIG)

RENEW_ALLOWANCE = datetime.timedelta(days=60)
REMOVE_ALLOWANCE = datetime.timedelta(days=67)


class Strings:
    LIST_ALL_SCHEMA = '''\
<code>{mod_code:9}</code>(<a href="{url}">Invite link</a>)\
'''

    LIST_ALL_IS_EMPTY = '''\
There doesn't seem to be anything here... \U0001f62d\
'''  # one teary boi

    ADD_GROUP_MOD_PROMPT = '''\
Great! Send me the module code, e.g. <code>CS1101S</code>\
'''
    ADD_GROUP_PM_ONLY = '''\
Please pm the bot for /add!\
'''

    REMOVE_GROUP_NONE = '''\
Groups can only be removed by the users that added them! \
It seems that you haven't added any groups...\
'''
    REMOVE_GROUP_SOME = '''\
Select a group to remove.\
'''
    REMOVE_GROUP_PM_ONLY = '''\
Please pm the bot for /remove!\
'''

    BUTTON_REMOVE_GROUP_OK = '''\
Entry for {} removed.\
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
    RESPONSE_SUCCESS = '''\
Success!\
'''

    HELP_TEXT = '''\
<b>USP Yellow Pages</b> is a directory for USP telegram study groups.

Commands:
/list -- Lists all groups
/add -- Add a group to the directory
/remove -- Remove a group from the directory
/cancel -- Cancels the current multi-stage command
/help -- Display this help message
/about -- About this bot

Entries in the directory have a lifetime of 60 days, after which you \
will receive a prompt for its renewal. There is a grace period of 7 \
days thereafter before removal. This ensures that groups linked in \
this directory are active---otherwise, more active groups can take \
its place.\
'''

    ABOUT_TEXT = '''\
<a href="{lic}">Provide without warranty.</a> \
Submit PR/issues at on <a href="{ghb}">github</a>, or contact @ningyuan.\
'''.format(
    lic='https://github.com/ningyuansg/USP-Yellow-Pages/blob/master/LICENSE',
    ghb='https://github.com/ningyuansg/USP-Yellow-Pages')

    JOB_PROMPT_RENEW = '''\
Hi! Your entry for <b>{}</b> in the directory is scheduled \
for removal on {}, unless renewed (just click the button below!). \
Alternatively, you may choose to delete the entry, if you wish.

Entries in the directory have a lifetime of 60 days, after which you \
will receive this message. There is a grace period of 7 days thereafter \
before removal. This ensures that groups linked in this directory are \
active---otherwise, more active groups can take its place.\
'''
    JOB_RENEW_OK = '''\
Renew success!\
'''
    JOB_DELETE_OK = '''\
Deleted!\
'''
    JOB_REMOVED = '''\
Your entry <b>{}</b> has expired, and was removed from the directory\
'''
