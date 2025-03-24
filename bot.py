import telebot
from telebot import types
import os
import flask
from flask import Flask,app,request
from controller import *

mytoken = "7612716429:AAH1RMJeUJGJC6_kiB7T-R2RkRxmPGD1G5k"
bot = telebot.TeleBot(mytoken,threaded=False)

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id,"Приветствую, новый пользователь! Я - бот <i>Планнер твоей мечты</i>\nЧтобы получить помощь по командам, нажми /help", parse_mode="HTML")

@bot.message_handler(commands=["help"])
def help(message):
    bot.send_message(message.chat.id,"")

@bot.message_handler(commands=["set_tasks"])
def set_tasks(message):
    bot.send_message(message.chat.id,"Отлично! Давайте составим список задач, чтобы достичь своей мечты! Напишите задачи в следующем формате:\n\n"
    "<описание задачи> - <дедлайн>\n<описание задачи> - <дедлайн <i>дд.мм.гггг ч:м></i>",parse_mode="HTML")
    bot.register_next_step_handler(add_tasks_to_plan)

def add_tasks_to_plan(message):
    tasks_str = message.text.split(sep='\n')
    tasks_arr = []
    for task in tasks_str:
       dif_task = task.split(sep=' - ')
       if len(dif_task)!=2:
           bot.send_message(message.chat.id,"Кажется, вы неправильно набрали задачу... Попробуйте снова, нажмите на /set_tasks!")
           return
       description = dif_task[0]
       deadline = dif_task[1]
       tasks_arr.append({'description':description,'deadline':deadline,'chat_id':message.chat.id})
    add_tasks_list(tasks_arr)
    


def dd_run_out(chat_id, task):
    task_desc = task['description']
    bot.send_message(chat_id,f"Кажется, ваша задача <i>{task_desc}</i> истекла...\nНичего страшного, она продлена на 1 день, но кое-кому пора ее выполнить!",parse_mode="HTML")

def send_reminder(text,chat_id):
    bot.send_message(chat_id,f"Помнится, некоторое время назад вы сказали сами себе\n\n<b>{text}</b>\n\nПора выполнить обещание!",parse_mode="HTML")

def remind_task(chat_id,task):
    task_desc = task['description']
    bot.send_message(chat_id,f"До дедлайна вашей задачи <i>{task_desc}</i> осталось всего 3 часа\nЗнайте, рак на горе уже свистнул, самое время взяться за дело!",parse_mode="HTML")

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