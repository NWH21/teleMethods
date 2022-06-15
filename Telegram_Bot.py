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

#########################
### CALLBACK CHECKERS ###
#########################

def isPackage(call):
  return "java." in call.data or "javax." in call.data

def isClass(call):
  string = call.data
  return string[0].isupper() and not isBookmark(call)

def isMethod(call):
  return not isPackage(call) and not isClass(call) and not isBookmark(call)

def isBookmark(call):
  return "bookmark" in call.data

def isAddBookmark(call):
  return call.data == "add bookmark"

def isDisplayBookmarks(call):
  return isBookmark(call) and "display bookmark " in call.data

def isRemoveBookmark(call):
  return isBookmark(call) and "removing bookmark " in call.data

def isReturnToBookmarks(call):
  return isBookmark(call) and "display all bookmarks " in call.data

  
#################
### KEYBOARDS ###
#################
  
def keyboardForPackages():
  keyboard_inline = InlineKeyboardMarkup()
  packages = db.list_collection_names()
  for package in packages:
    if package != "Bookmark":
      button = InlineKeyboardButton(text= package, callback_data= package)
      keyboard_inline.add(button)
    else:
      continue
  return keyboard_inline

def keyboardForClasses(classname):
    keyboard_inline = InlineKeyboardMarkup()
    posts = db[classname]
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

def keyboardForMethods(post):
  keyboard_inline = InlineKeyboardMarkup()
  list_id = []
  list = []
  for methods in post["classmethods"]:
    methodname = methods["method_name"]
    methodname = re.sub("\([^()]*\)", "", methodname)
    list_id.append(methods["ID"]) 
    list.append(methodname)
  if len(list) == 0:
    keyboard_inline = keyboard_inline.add(InlineKeyboardButton(text = "No methods", callback_data =None))
  else:
    for i in range(len(list)):
      if i % 2 == 0 and i != len(list) - 1: 
        keyboard_inline = keyboard_inline.add(InlineKeyboardButton(text = list[i], callback_data = list_id[i]),                                                                   InlineKeyboardButton(text = list[i+1], callback_data = list_id[i+1]))
      elif i % 2 == 0 and i == len(list) - 1:
        keyboard_inline = keyboard_inline.add(InlineKeyboardButton(text = list[i], callback_data = list_id[i]))
      else:
        continue
  return keyboard_inline 
      
def keyboardForAddingBookmark():
  keyboard_inline = InlineKeyboardMarkup()
  keyboard_inline = keyboard_inline.add(InlineKeyboardButton(text = "Bookmark",callback_data = "add bookmark"))
  return keyboard_inline

def keyboardForSearchingBookmarks(id):
  keyboard_inline = InlineKeyboardMarkup()
  users = db["Bookmark"]
  bookmarked_methods = users.find_one({'chat_id' : id})["Bookmarked_methods"]
  for methods in bookmarked_methods:
    button = InlineKeyboardButton(text = methods['method_name'],callback_data = "display bookmark " + methods['method_name'])
    keyboard_inline.add(button)
  return keyboard_inline       
        
def keyboardForRemovingBookmarks(bookmarked_method):  
  keyboard_inline = InlineKeyboardMarkup()
  keyboard_inline.add(InlineKeyboardButton(text = "Back to Bookmarks",callback_data = "display all bookmarks " + bookmarked_method))
  keyboard_inline.add(InlineKeyboardButton(text = "Remove Bookmark",callback_data = "removing bookmark " + bookmarked_method))
  return keyboard_inline   

  
#########################
### QUERTYING METHODS ###
#########################

@bot.message_handler(commands=['packages'])
def whichPackage(message):
  bot.send_message(message.chat.id, "Which package?",reply_markup = keyboardForPackages())

@bot.callback_query_handler(func= isPackage)
def whichClass(call):
  classname = call.data
  bot.delete_message (call.message.chat.id, call.message.id)
  bot.send_message(call.message.chat.id, "Which class?", reply_markup = keyboardForClasses(classname))
  
  @bot.callback_query_handler(func= isClass)
  def whichMethod(call):
    posts = db[classname]
    post = posts.find_one({"classname" : call.data})
    bot.delete_message (call.message.chat.id, call.message.id)
    bot.send_message(call.message.chat.id, "Which method?", reply_markup = keyboardForMethods(post))
    
    @bot.callback_query_handler(func= isMethod)
    def methodDescription(call):
      methods = post["classmethods"]
      for method in methods:
        if method["ID"] == call.data:
          name = method["method_name"]
          type = method["method_modifier"]
          description = method["method_description"].replace("\n", "")
          msg = "Method Name: " + name + "\n" + "\n" + "Method Modifier: " + type + "\n" + "\n" + "Method Description: " + description
          bot.send_message(call.message.chat.id, msg, reply_markup = keyboardForAddingBookmark())
  
      @bot.callback_query_handler(func = isAddBookmark)
      def addBookmark(call):
        users = db["Bookmark"]
        if users.find_one({'chat_id' : call.message.chat.id}) != None:
          existing = users.find_one({'chat_id' : call.message.chat.id})
          existing = existing["Bookmarked_methods"] 
        else:
          existing = []  
        existing.append({"method_name":name,"method_modifier": type, "method_description": description})
        users.update_one({'chat_id': call.message.chat.id},{'$set': {"Bookmarked_methods":existing}}, upsert=True)
        text = "Bookmark added!"
        bot.send_message(call.message.chat.id,text)


#################
### BOOKMARKS ###
#################

@bot.message_handler(commands = ['bookmarks'])
def bookmarks(message):
  users = db["Bookmark"]
  if users.find_one({'chat_id' : message.chat.id}) != None and users.find_one({'chat_id' : message.chat.id})["Bookmarked_methods"] != []:
      bot.send_message(message.chat.id,"Here are your bookmarks",reply_markup = keyboardForSearchingBookmarks(message.chat.id)) 
  else:
    bot.send_message(message.chat.id,"You have no bookmarks")
      
@bot.callback_query_handler(func=isDisplayBookmarks)
def displayBookmarkedMethod(call):
  users = db["Bookmark"]
  id = call.message.chat.id
  bookmarked_methods = users.find_one({'chat_id' : id})["Bookmarked_methods"]
  for i in bookmarked_methods:
    if i['method_name'] == call.data.replace("display bookmark ", ""):
      name = i["method_name"]
      type = i["method_modifier"]
      description = i["method_description"].replace("\n", "")
      msg = "Method Name: " + name + "\n" + "\n" + "Method Modifier: " + type + "\n" + "\n" + "Method Description: " + description
      bot.delete_message (call.message.chat.id, call.message.id)
      bot.send_message(call.message.chat.id, msg, reply_markup = keyboardForRemovingBookmarks(name))
      
@bot.callback_query_handler(func=isRemoveBookmark)
def removeBookmarkedMethod(call):
  users = db["Bookmark"]
  id = call.message.chat.id
  bookmarked_methods = users.find_one({'chat_id' : id})["Bookmarked_methods"]
  for i in bookmarked_methods:
    if i['method_name'] == call.data.replace("removing bookmark ", ""):
      name = i["method_name"]
      bookmarked_methods.remove(i)
      users.update_one({'chat_id': id},{'$set': {"Bookmarked_methods": bookmarked_methods}}, upsert=True)
      bot.delete_message (call.message.chat.id, call.message.id)
      bot.send_message(call.message.chat.id, "Bookmarked method " + name + " removed")
  
@bot.callback_query_handler(func=isReturnToBookmarks)
def returnToBookmarks(call):
  bot.delete_message (call.message.chat.id, call.message.id)
  return bookmarks(call.message)

bot.polling()
