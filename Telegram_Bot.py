import os
import telebot
import pymongo
from pymongo import MongoClient
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import re

client = pymongo.MongoClient("mongodb+srv://kkennyllow:Something1.@cluster0.nmjspdx.mongodb.net/teleMethods?retryWrites=true&w=majority")
db = client["teleMethods"]

API_KEY = os.environ['API_KEY']
bot = telebot.TeleBot(API_KEY)
bot.delete_my_commands(scope=None, language_code=None)


def keyboardForPackages():
  keyboard_inline = InlineKeyboardMarkup()
  packages = db.list_collection_names()
  for package in packages:
    button = InlineKeyboardButton(text= package, callback_data= package)
    keyboard_inline.add(button)
  return keyboard_inline

def isPackage(call):
  if "java." in call.data or "javax." in call.data:
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
  classname = call.data
  
  def keyboardForClasses():
    keyboard_inline = InlineKeyboardMarkup()
    posts = db[call.data]
    list = []
    for post in posts.find():
      list.append(post["classname"])
    for i in range(len(list)):
      if i % 2 == 0 and i != len(list) - 1: 
        keyboard_inline = keyboard_inline.add(InlineKeyboardButton(text = list[i], callback_data = list[i]),                                                                   InlineKeyboardButton(text = list[i+1], callback_data = list[i+1]))
      elif i % 2 == 0 and i == len(list) - 1:
        keyboard_inline = keyboard_inline.add(InlineKeyboardButton(text = list[i], callback_data = list[i]))
      else:
          continue
    return keyboard_inline
    
  bot.delete_message (call.message.chat.id, call.message.id)
  bot.send_message(call.message.chat.id, "Which class?", reply_markup = keyboardForClasses())
  
  
  @bot.callback_query_handler(func= isClass)
  def whichMethod(call):
    posts = db[classname]
    post = posts.find_one({"classname" : call.data})
    
    def keyboardForMethods():
      keyboard_inline = InlineKeyboardMarkup()
      list_id = []
      list = []
  
      for methods in post["classmethods"]:
        methodname = methods["method_name"]
        methodname = re.sub("\([^()]*\)", "", methodname)
        list_id.append(methods["ID"]) 
        list.append(methodname)
      if len(list) == 0:
        keyboard_inline = keyboard_inline.add(InlineKeyboardButton(text = "No methods", callback_data = list_id[i]))
      else:
        for i in range(len(list)):
          if i % 2 == 0 and i != len(list) - 1: 
            keyboard_inline = keyboard_inline.add(InlineKeyboardButton(text = list[i], callback_data = list_id[i]),                                                                   InlineKeyboardButton(text = list[i+1], callback_data = list_id[i+1]))
          elif i % 2 == 0 and i == len(list) - 1:
            keyboard_inline = keyboard_inline.add(InlineKeyboardButton(text = list[i], callback_data = list_id[i]))
          else:
            continue
      return keyboard_inline 
      
    bot.delete_message (call.message.chat.id, call.message.id)
    bot.send_message(call.message.chat.id, "Which method?", reply_markup = keyboardForMethods())
    
    
    
    @bot.callback_query_handler(func= isMethod)
    def methodDescription(call):
      methods = post["classmethods"]
      for method in methods:
        if method["ID"] == call.data:
          name = method["method_name"]
          type = method["method_modifier"]
          description = method["method_description"].replace("\n", "")
          msg = "Method Name: " + name + "\n" + "\n" + "Method Modifier: " + type + "\n" + "\n" + "Method Description: " + description
          bot.send_message(call.message.chat.id, msg)
          break


bot.polling()
