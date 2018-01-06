import telegram, telegram.ext
from settings import CONFIG
from commands import commands

class Telebot:
    def __init__(self):
        self.core = telegram.Bot(token=CONFIG['telegram']['api_key'])
        self.updater = telegram.ext.Updater(bot=self.core)
        self.dispatcher = self.updater.dispatcher
        for command in commands:
            self.dispatcher.add_handler(
                telegram.ext.CommandHandler(*command)
            )

    def listen(self):
        self.updater.start_polling()
        self.updater.idle()
