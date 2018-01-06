import logging
import telebot, database

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)

bot = telebot.Telebot()
bot.listen()
