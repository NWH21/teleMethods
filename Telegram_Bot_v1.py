import os
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

API_KEY = os.environ['API_KEY']
bot = telebot.TeleBot(API_KEY)


bot.delete_my_commands(scope=None, language_code=None)

def keyboard1():
  markup = ReplyKeyboardMarkup(row_width=10, one_time_keyboard = True)
  markup.add("java.util")
  markup.add("java.lang")
  markup.add("java.math")
  markup.add("...")
  return markup

@bot.message_handler(commands=['packages'])
def packages(message):
  bot.send_message(message.chat.id, "Which package?",reply_markup = keyboard1())


@bot.message_handler(func=lambda message:True)
def classes(message):
  if message.text == "java.util":
    response = "Which class?" + "\n" + "/Optional" + "\n" + "/Collections" + "\n" + "/Set" + "\n" + "etc"
    bot.send_message(message.chat.id, response)
  elif message.text == "/Optional":
    response = "Which method?" + "\n" + "/ifElse" + "\n" + "/isEmpty" + "\n" + "/isPresent" + "\n" + "etc"
    bot.send_message(message.chat.id, response)
  elif message.text == "/isEmpty":
    response = "isEmpty() returns true if value is present otherwise returns false"
    bot.send_message(message.chat.id, response)
  
bot.polling()
