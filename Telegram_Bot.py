import os,requests,json
import telebot
import pymongo
from pymongo import MongoClient
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import re
import pandas as pd
import numpy as np




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
  { "command" :"recommendation",
    "description" : "suggests methods for use"
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
  return not isPackage(call) and not isClass(call) and not isBookmark(call) and call.data != "upvote" and not isRecommendation(call)

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

def isNotQuickSearch(message):
  return not isQuickSearch(message)

def isUpvote(call):
  return call.data == "upvote"

def isRecommendation(call):
  return "recommendation " in call.data
  
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
    button = InlineKeyboardButton(text = methods['method_name'],callback_data = "display bookmark " + str(bookmarked_methods.index(methods)))
    keyboard_inline.add(button)
  return keyboard_inline       
        
def keyboardForRemovingBookmarks(index):  
  keyboard_inline = InlineKeyboardMarkup()
  keyboard_inline.add(InlineKeyboardButton(text = "Remove Bookmark",callback_data = "removing bookmark " + str(index)))
  keyboard_inline.add(InlineKeyboardButton(text = "Back to Bookmarks",callback_data = "display all bookmarks " + str(index)))
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

def keyboardForRecommendation(data):
  df = pd.read_json(data, orient='columns')
  keyboard_inline = InlineKeyboardMarkup()
  for i in df.index.tolist():
    method = df.loc[i]
    keyboard_inline = keyboard_inline.add(InlineKeyboardButton(text = method["package_name"]+"."+method["class_name"] + "." +method["method_name"], callback_data = "recommendation " + str(i)))
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
  text += "Use /recommendation for a list of suggested methods"
  bot.send_message(message.chat.id,text)


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
  bot.delete_message (call.message.chat.id, call.message.id)
  bot.send_message(call.message.chat.id, "Which class?", reply_markup = keyboardForClasses(package_name))
  
  @bot.callback_query_handler(func= isClass)
  def whichMethod(call):
    package_collection = db[package_name]
    global class_
    class_ = package_collection.find_one({"classname" : call.data})
    bot.delete_message (call.message.chat.id, call.message.id)
    if len(class_["classmethods"]) == 0:
      bot.send_message(call.message.chat.id, "There are no methods in this class")
    else:  
      bot.send_message(call.message.chat.id, "Which method?", reply_markup = keyboardForMethods(class_))

    @bot.callback_query_handler(func= isMethod)
    def methodDescription(call):
      global methodID
      methodID = call.data 
      count = 0
      for methods in class_["classmethods"]:
        if methods["ID"] == call.data:
          global name
          global type
          global upvotes
          global description
          name = methods["method_name"]
          type = methods["method_modifier"]
          upvotes = methods["upvotes"]
          description = methods["method_description"].replace("\n", "")
          new = class_["classmethods"]
          new[count]["history"] = new[count]["history"] + 1
          package_collection.update_one({"classname" : class_["classname"]}, {'$set' : {"classmethods" : new}})
          msg = "Method Name: " + name + "\n" + "\n" + "Method Modifier: " + type + "\n" + "\n" + "Method Description: " + description + "\n" + "\n" + "Number of Upvotes: " + str(len(upvotes))
          bot.send_message(call.message.chat.id, msg, reply_markup = keyboardForAddingBookmark())
      count += 1
      
      @bot.callback_query_handler(func = isAddBookmark)
      def addBookmark(call):
        users = db["Bookmark"]
        if users.find_one({'chat_id' : call.message.chat.id}) != None:
          existing = users.find_one({'chat_id' : call.message.chat.id})
          existing = existing["Bookmarked_methods"] 
        else:
          existing = []  
        existing.append({"method_name":name,"method_modifier": type, "method_description": description, "upvotes": upvotes})
        users.update_one({'chat_id': call.message.chat.id},{'$set': {"Bookmarked_methods":existing}}, upsert=True)
        text = "Bookmark added!"
        bot.send_message(call.message.chat.id,text)
      
      @bot.callback_query_handler(func = isUpvote)
      def upvoteMethod(call):
        global newList
        newList = class_["classmethods"]
        for method in newList:
          if method["ID"] == methodID:
            if call.message.chat.id not in method["upvotes"]:
              method["upvotes"].append(call.message.chat.id)
              package_collection.update_one({"classname" : class_["classname"]}, {"$set" : {"classmethods" : newList}}, upsert = True)
    
              bot.send_message(call.message.chat.id, "Upvoted!")
            else:
              bot.send_message(call.message.chat.id, "Already upvoted!")





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
  method = bookmarked_methods[int(call.data.replace("display bookmark ", ""))]
  name = method["method_name"]
  type = method["method_modifier"]
  description = method["method_description"].replace("\n", "")
  msg = "Method Name: " + name + "\n" + "\n" + "Method Modifier: " + type + "\n" + "\n" + "Method Description: " + description
  bot.delete_message (call.message.chat.id, call.message.id)
  bot.send_message(call.message.chat.id, msg, reply_markup = keyboardForRemovingBookmarks(int(call.data.replace("display bookmark ", ""))))

@bot.callback_query_handler(func=isRemoveBookmark)
def removeBookmarkedMethod(call):
  users = db["Bookmark"]
  id = call.message.chat.id
  index = int(call.data.replace("removing bookmark ", ""))
  bookmarked_methods = users.find_one({'chat_id' : id})["Bookmarked_methods"]
  name = bookmarked_methods[index]["method_name"]
  bookmarked_methods = bookmarked_methods[:index] + bookmarked_methods[index+1 :]
  users.update_one({'chat_id': id},{'$set': {"Bookmarked_methods": bookmarked_methods}}, upsert=True)
  bot.delete_message (call.message.chat.id, call.message.id)
  bot.send_message(call.message.chat.id, "Bookmarked method " + name + " removed")
  
@bot.callback_query_handler(func=isReturnToBookmarks)
def returnToBookmarks(call):
  bot.delete_message(call.message.chat.id, call.message.id)
  return bookmarks(call.message)


####################
### QUICK SEARCH ###
####################
  
@bot.message_handler(commands = ['quick'])
def quickSearch(message):
  bot.send_message(message.chat.id, "What are you searching for?" + "\n" + "Please try it in this format 'java.util.Optional orElse'")

@bot.message_handler(func = isNotQuickSearch)
def wrongQuickSearch(message):
  bot.send_message(message.chat.id, "Invalid Search" + "\n" + "Please try again with this format 'java.util.Optional orElse' or check if there are spelling errors.")

@bot.message_handler(func = isQuickSearch)
def displayQuickSearchMethod(message):
  text = message.text.split(".")
  package = message.text.replace("." + text[-1],"")
  package_collection = db[package]
  classname = text[-1].split()[0]
  method = text[-1].split()[1]
  global class_
  class_ = package_collection.find_one({"classname" : classname})
  bot.send_message(message.chat.id, "Which method?", reply_markup = keyboardForQuickSearchMethods(class_, re.sub("\([^()]*\)", "", method)))
  
  
    
  @bot.callback_query_handler(func= isMethod)
  def methodDescription(call):
    global methodID
    methodID = call.data 
    count = 0
    for methods in class_["classmethods"]:
      if methods["ID"] == call.data:
        global name
        global type
        global upvotes
        global description
        name = methods["method_name"]
        type = methods["method_modifier"]
        upvotes = methods["upvotes"]
        description = methods["method_description"].replace("\n", "")
        new = class_["classmethods"]
        new[count]["history"] = new[count]["history"] + 1
        package_collection.update_one({"classname" : classname}, {'$set' : {"classmethods" : new}})
        msg = "Method Name: " + name + "\n" + "\n" + "Method Modifier: " + type + "\n" + "\n" + "Method Description: " + description + "\n" + "\n" + "Number of Upvotes: " + str(len(upvotes))
        bot.send_message(call.message.chat.id, msg, reply_markup = keyboardForAddingBookmark())
      count += 1

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

    @bot.callback_query_handler(func = isUpvote)
    def upvoteMethod(call):
      global newList
      newList = class_["classmethods"]
      for method in newList:
        if method["ID"] == methodID:
          if call.message.chat.id not in method["upvotes"]:
            method["upvotes"].append(call.message.chat.id)
            package_collection.update_one({"classname" : class_["classname"]}, {"$set" : {"classmethods" : newList}}, upsert = True)
            bot.send_message(call.message.chat.id, "Upvoted!")
          else:
            bot.send_message(call.message.chat.id, "Already upvoted!")


#######################
### RECOMMENDATIONS ###
#######################

@bot.message_handler(commands = ['recommendation'])
def recommendation(message):
  collection_names = db.list_collection_names()
  collection_names.remove("Bookmark")
  finaldf = pd.DataFrame()
  
  for collection in collection_names:
    package = db[collection]
    package_df = pd.DataFrame(list(package.find()))
    df = pd.DataFrame() 
    for index in list(package_df.index):
      class_df = pd.DataFrame(data = package_df['classmethods'][index],columns = ['ID','method_name', 'method_modifier', 'method_description', 'upvotes','history'])
      class_df["class_name"] = package_df.at[index, "classname"]
      df = df.append(class_df)
    df["package_name"] = collection
    finaldf = finaldf.append(df)

  finaldf = finaldf.reset_index(drop = True)
  finaldf = finaldf.loc[finaldf['history'] >= 1]
  finaldf["ID"] = finaldf.index.tolist()
  history_series = finaldf["history"]
  largest_history_id = pd.to_numeric(history_series).idxmax()
  d_items = pd.DataFrame(np.diag(finaldf["history"]), index = finaldf.index ,columns = history_series.index).fillna(0)

  recommendations_list= get_recommendations(d_items, largest_history_id)
  finaldf = finaldf[finaldf.index.isin(recommendations_list[:5])]
  bot.send_message(message.chat.id, "Which method?", reply_markup = keyboardForRecommendation(finaldf.to_json()))

  @bot.callback_query_handler(func = isRecommendation)
  def method_description(call):
    index = int(call.data.replace("recommendation ", ""))
    methods = finaldf.loc[index]
    global package_name
    package_name = methods["package_name"]
    classname = methods["class_name"]
    class_ = db[package_name].find_one({"classname" : classname})
    name = methods["method_name"]
    type = methods["method_modifier"]
    upvotes = methods["upvotes"]
    description = methods["method_description"].replace("\n", "")

    new = class_["classmethods"]
    new[get_list_index(name, new)]["history"] = new[get_list_index(name, new)]["history"] + 1

    db[package_name].update_one({"classname" : classname}, {'$set' : {"classmethods" : new}})
    msg = "Package Name:" + package_name + "\n \nClass Name:" + classname + "\n \nMethod Name: " + name + "\n" + "\n" + "Method Modifier: " + type + "\n" + "\n" + "Method Description: " + description + "\n" + "\n" + "Number of Upvotes: " + str(len(upvotes))
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

    @bot.callback_query_handler(func = isUpvote)
    def upvoteMethod(call):
      global newList
      newList = class_["classmethods"]
      for method in newList:
        if method["method_name"] == name:
          if call.message.chat.id not in method["upvotes"]:
            method["upvotes"].append(call.message.chat.id)
            db[package_name].update_one({"classname" : class_["classname"]}, {"$set" : {"classmethods" : newList}}, upsert = True)
            bot.send_message(call.message.chat.id, "Upvoted!")
          else:
            bot.send_message(call.message.chat.id, "Already upvoted!")

def get_recommendations(df, item):
    recommendations = df.corrwith(df[item])
    recommendations.dropna(inplace=True)
    recommendations = pd.DataFrame(recommendations, columns=['correlation'])
    recommendations = recommendations.sort_values(by='correlation', ascending=False)
    return recommendations.index.tolist()

def get_list_index(method_name, classmethods):
  count = 0
  for method in classmethods:
    if method["method_name"] == method_name:
      return count
    count += 1

bot.polling()

