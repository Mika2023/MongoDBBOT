import telebot
from telebot import types
import os
import flask
from flask import Flask,app,request

mytoken = "7612716429:AAH1RMJeUJGJC6_kiB7T-R2RkRxmPGD1G5k"
bot = telebot.TeleBot(mytoken,threaded=False)

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id,"Приветствую, новый пользователь! Я - бот <i>Планнер твоей мечты</i>\nЧтобы получить помощь по командам, нажми /help", parse_mode="HTML")

@bot.message_handler(commands=["help"])
def start(message):
    bot.send_message(message.chat.id,"")

app = Flask(__name__)

@app.route(f'/{mytoken}', methods=['POST'])
def webhook():
    print(bot.message_handlers)
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates(updates=[update])
    return 'OK', 200

@app.route('/', methods=['GET'])
def home():
    return 'bot is working', 200

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.getenv("PORT",8080)))