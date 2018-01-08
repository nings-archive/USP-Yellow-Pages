import telegram, telegram.ext
from settings import CONFIG
from commands import commands, message_handlers
from inlinekeyboardhandler import handle_onclick
from jobs import daily_jobs

class Telebot:
    def __init__(self):
        self.core = telegram.Bot(token=CONFIG['telegram']['api_key'])
        self.updater = telegram.ext.Updater(bot=self.core)
        self.dispatcher = self.updater.dispatcher
        self.job_queue = self.updater.job_queue
        for command in commands:
            self.dispatcher.add_handler(
                telegram.ext.CommandHandler(*command)
            )
        for message_handler in message_handlers:
            self.dispatcher.add_handler(
                telegram.ext.MessageHandler(*message_handler)
            )
        self.dispatcher.add_handler(
            telegram.ext.CallbackQueryHandler(handle_onclick)
        )
        for jobs in daily_jobs:
            self.job_queue.run_daily(**jobs)

    def listen(self):
        self.updater.start_polling()
        self.updater.idle()
