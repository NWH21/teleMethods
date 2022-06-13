import os
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY_SECRET")
supabase: Client = create_client(url, key)

API_KEY = os.environ['API_KEY']
bot = telebot.TeleBot(API_KEY)

bot.delete_my_commands(scope=None, language_code=None)

def keyboardForPackages():
  button1 = InlineKeyboardButton(text="java.util", callback_data="java.util")
  button2 = InlineKeyboardButton(text="java.lang", callback_data="java.lang")
  button3 = InlineKeyboardButton(text="java.math", callback_data="java.math")
  button4 = InlineKeyboardButton(text="...", callback_data="...")
  keyboard_inline = InlineKeyboardMarkup().add(button1, button2, button3, button4)
  return keyboard_inline

def keyboardForClasses():
  button1 = InlineKeyboardButton(text="Optional", callback_data="Optional")
  button2 = InlineKeyboardButton(text="Collections", callback_data="Collections")
  button3 = InlineKeyboardButton(text="Set", callback_data="Set")
  button4 = InlineKeyboardButton(text="...", callback_data="...")
  keyboard_inline = InlineKeyboardMarkup().add(button1, button2, button3, button4)
  return keyboard_inline


def isPackage(call):
  if "java." in call.data:
    return True
  return False

def isClass(call):
  string = call.data
  if string[0].isupper():
    return True
  return False

def isMethod(call):
  return not isPackage(call) and not isClass(call)



@bot.message_handler(commands=['packages'])
def whichPackage(message):
  bot.send_message(message.chat.id, "Which package?",reply_markup = keyboardForPackages())


@bot.callback_query_handler(func= isPackage)
def whichClass(call):
  if call.data == "java.util":
    bot.send_message(call.message.chat.id, "Which class?", reply_markup = keyboardForClasses())


@bot.callback_query_handler(func= isClass)
def whichMethod(call):
  data1 = supabase.table(call.data)
  data2 = supabase.table(call.data).select("*").execute().data
  def keyboardForMethods():
    keyboard_inline = InlineKeyboardMarkup()
    for dict in data2:
      method_name = dict.get("Method Name")
      keyboard_inline = keyboard_inline.add(InlineKeyboardButton(text = method_name, callback_data = method_name ))
    return keyboard_inline  
  bot.send_message(call.message.chat.id, "Which method?", reply_markup = keyboardForMethods()) 

  @bot.callback_query_handler(func= isMethod)
  def methodDescription(call):
    data = data1.select('*').execute().data
    for methods in data:
      if methods.get("Method Name") == call.data:
        msg = methods.get("Method Description")
        bot.send_message(call.message.chat.id, msg)
        break
    

bot.polling()
