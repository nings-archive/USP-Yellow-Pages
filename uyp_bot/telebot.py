import telegram, telegram.ext
from settings import CONFIG
from commands import commands, message_handlers

class Telebot:
    def __init__(self):
        self.core = telegram.Bot(token=CONFIG['telegram']['api_key'])
        self.updater = telegram.ext.Updater(bot=self.core)
        self.dispatcher = self.updater.dispatcher
        for command in commands:
            self.dispatcher.add_handler(
                telegram.ext.CommandHandler(*command)
            )
        for message_handler in message_handlers:
            self.dispatcher.add_handler(
                telegram.ext.MessageHandler(*message_handler)
            )

    def listen(self):
        self.updater.start_polling()
        self.updater.idle()
