import os,requests,json
import telebot
import pymongo
from pymongo import MongoClient
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import re



client = pymongo.MongoClient("mongodb+srv://kkennyllow:Something1.@cluster0.nmjspdx.mongodb.net/teleMethods?retryWrites=true&w=majority")
db = client["teleMethods"]
API_KEY = "5424123226:AAG2yTG5kdgMwfk6vyOMr7DYQ3fTkMhNFbs"

bot = telebot.TeleBot(API_KEY)
bot.delete_my_commands(scope=None, language_code=None)




#########################
######### MENU ##########
#########################
url = "https://api.telegram.org/bot"+API_KEY+"/setMyCommands?commands="
cmd = [{
  "command":"packages",
  "description": "shows the various packages for selection"
  },
  { "command" : "bookmarks",
    "description": "shows your bookmarked methods"
  },
  { "command" :"quick",
    "description" : "performs quick search"
  },
  { "command" :"upvote",
    "description" : "gives top 10 most upvoted methods by other users"
    }]
cmd = json.dumps(cmd)
url = url + str(cmd)
response = requests.get(url)







#########################
### CALLBACK CHECKERS ###
#########################


def isBackToPackages(call):
  return call.data == "back to packages"

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

def isQuickSearch(message):
  text = message.text.split(".")
  if len(message.text.split(".")) < 3 or len(text[-1].split()) < 2:
    return False
  package = message.text.replace("." + text[-1],"")
  classname = text[-1].split()[0]
  method = text[-1].split()[1]
  if package in db.list_collection_names():
    class_ = db[package].find_one({"classname" : classname})
    for methods in class_["classmethods"]:
      if re.sub("\([^()]*\)", "", method) == re.sub("\([^()]*\)", "", methods["method_name"]):
        return True
  return False
  
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
        keyboard_inline = keyboard_inline.add(InlineKeyboardButton(text = list[i], callback_data = list[i]),InlineKeyboardButton(text = list[i+1], callback_data = list[i+1]))
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
  for i in range(len(list)):
    if i % 2 == 0 and i != len(list) - 1: 
      keyboard_inline = keyboard_inline.add(InlineKeyboardButton(text = list[i], callback_data = list_id[i]),InlineKeyboardButton(text = list[i+1], callback_data = list_id[i+1]))
    elif i % 2 == 0 and i == len(list) - 1:
      keyboard_inline = keyboard_inline.add(InlineKeyboardButton(text = list[i], callback_data = list_id[i]))
    else:
      continue
  return keyboard_inline 
      
def keyboardForAddingBookmark():
  keyboard_inline = InlineKeyboardMarkup()
  keyboard_inline = keyboard_inline.add(InlineKeyboardButton(text = "Bookmark",callback_data = "add bookmark"))
  keyboard_inline = keyboard_inline.add(InlineKeyboardButton(text = "Upvote", callback_data = "upvote"))
  keyboard_inline = keyboard_inline.add(InlineKeyboardButton(text = "Back to Packages",callback_data = "back to packages"))
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
  keyboard_inline.add(InlineKeyboardButton(text = "Remove Bookmark",callback_data = "removing bookmark " + bookmarked_method))
  keyboard_inline.add(InlineKeyboardButton(text = "Back to Bookmarks",callback_data = "display all bookmarks " + bookmarked_method))
  return keyboard_inline   

def keyboardForQuickSearchMethods(post, method):
  keyboard_inline = InlineKeyboardMarkup()
  list_id = []
  list = []
  for methods in post["classmethods"]:
    methodname = methods["method_name"]
    methodname = re.sub("\([^()]*\)", "", methodname)
    if methodname == method:
      list_id.append(methods["ID"]) 
      list.append(methodname)
  if len(list) == 0:
    keyboard_inline = keyboard_inline.add(InlineKeyboardButton(text = "No methods", callback_data =None))
  else:
    for i in range(len(list)):
      if i % 2 == 0 and i != len(list) - 1: 
        keyboard_inline = keyboard_inline.add(InlineKeyboardButton(text = list[i], callback_data = list_id[i]),InlineKeyboardButton(text = list[i+1], callback_data = list_id[i+1]))
      elif i % 2 == 0 and i == len(list) - 1:
        keyboard_inline = keyboard_inline.add(InlineKeyboardButton(text = list[i], callback_data = list_id[i]))
      else:
        continue
  return keyboard_inline

def keyboardForUpvoted():
  keyboard_inline = InlineKeyboardMarkup()
  packages = db.list_collection_names()
  for package in packages:
    col = db[package]
    cursor = col.find({})
    for document in cursor:
      try:
        for i in range(len(document['classmethods'])):
          if(document['classmethods'][i]['upvotes']) > 0:
            keyboard_inline = keyboard_inline.add(InlineKeyboardButton(text = document['classmethods'][i]['method_modifier'],callback_data = "method_name"))#document['classmethods'][i]['method_modifier'][0]))  #need to show description of upvoted method
      except KeyError:
        continue
      except IndexError:
        continue
  return keyboard_inline




#############
### START ###
#############
@bot.message_handler(commands = ['start','help'])
def startMenu(message):
  user_first_name = str(message.chat.first_name)
  user_last_name = str(message.chat.last_name)
  text = f"Hey {user_first_name} {user_last_name}!\nWelcome to teleMethods! Have the knowledge for the java packages at the palm of your hand!\n \n"
  text += "Use /packages to choose from the packages available \n"
  text += "Use /bookmarks to choose from your bookmarked methods \n"
  text += "Use /quick to perform a quick search for a certain method \n"
  text += "Use /upvote to check on upvoted methods by other users"
  bot.send_message(message.chat.id,text)


##############
### UPVOTE ###
##############

@bot.message_handler(commands = ['upvote'])
def upvoteMenu(message):
  user_first_name = str(message.chat.first_name)
  user_last_name = str(message.chat.last_name)
  text = f"Hey {user_first_name} {user_last_name}!\n"
  text += "Here are the upvoted methods"
  bot.send_message(message.chat.id,text,reply_markup = keyboardForUpvoted())

  
#########################
### QUERYING METHODS  ###
#########################

@bot.message_handler(commands=['packages'])
def whichPackage(message):
  bot.send_message(message.chat.id, "Which package?",reply_markup = keyboardForPackages())

@bot.callback_query_handler(func= isBackToPackages)
def whichPackage(call):
  bot.send_message(call.message.chat.id, "Which package?",reply_markup = keyboardForPackages())

@bot.callback_query_handler(func= isPackage)
def whichClass(call):
  global package_name
  package_name = call.data
  print(package_name)
  bot.delete_message (call.message.chat.id, call.message.id)
  bot.send_message(call.message.chat.id, "Which class?", reply_markup = keyboardForClasses(package_name))
  
  @bot.callback_query_handler(func= isClass)
  def whichMethod(call):
    posts = db[package_name]
    global post
    post = posts.find_one({"classname" : call.data})
    bot.delete_message (call.message.chat.id, call.message.id)
    bot.send_message(call.message.chat.id, "Which method?", reply_markup = keyboardForMethods(post))
    

    @bot.callback_query_handler(func= isMethod)
    def methodDescription(call):
      methods = post["classmethods"]
      for method in methods:
        if method["ID"] == call.data:
          print(method["method_name"])
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

     
##
##    except TypeError as e:
##      print(e)
##      text = "There are no methods in this class!"
##      bot.send_message(call.message.chat.id,text)
##      return text

      

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


####################
### QUICK SEARCH ###
####################
  
@bot.message_handler(commands = ['quick'])
def quickSearch(message):
  bot.send_message(message.chat.id, "What are you searching for?")

  
@bot.message_handler(func = isQuickSearch)
def displayQuickSearchMethod(message):
  text = message.text.split(".")
  package = message.text.replace("." + text[-1],"")
  classname = text[-1].split()[0]
  method = text[-1].split()[1]
  class_ = db[package].find_one({"classname" : classname})
  bot.send_message(message.chat.id, "Which method?", reply_markup = keyboardForQuickSearchMethods(class_, re.sub("\([^()]*\)", "", method)))
    
  @bot.callback_query_handler(func= isMethod)
  def methodDescription(call): 
    for methods in class_["classmethods"]:
      if methods["ID"] == call.data:
        name = methods["method_name"]
        type = methods["method_modifier"]
        description = methods["method_description"].replace("\n", "")
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


bot.polling()

