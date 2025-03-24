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
    bot.send_message(message.chat.id,"Отлично! Давайте составим список задач, чтобы достичь своей мечты! Напишите задачи в следующем формате:\n\nописание задачи - дедлайн\nописание задачи - дедлайн <i>дд.мм.гггг ч:м</i>",parse_mode="HTML")
    bot.register_next_step_handler(message,add_tasks_to_plan)

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
       tasks_arr.append({'description':description,'deadline':deadline,'chat_id':message.chat.id,'checked':'False'})
    res = add_tasks_list(tasks_arr)
    if res: bot.send_message(message.chat.id,"Оооооо, очень крутые задачи, а еще...\n\nОни успешно добавлены!")
    else:bot.send_message(message.chat.id,"Какая-то хрень произошла с сервером, попробуйте снова пжпжпж")

@bot.message_handler(commands=["set_reminder"])
def set_reminder_bot(message):
    bot.send_message(message.chat.id,"Очень мудрое решение! С напоминаниями задачи всегда быстрее выполняются! Скорее, напишите текст напоминания и дату, когда напомнить, формате\nописание - дд.мм.гггг ч:м")
    bot.register_next_step_handler(message,set_reminder_text)

def set_reminder_text(message):
    dif_rem = message.text.split(sep=' - ')
    if len(dif_rem)!=2:
           bot.send_message(message.chat.id,"Кажется, вы неправильно набрали напоминание... Попробуйте снова, нажмите на /set_reminder!")
           return
    description = dif_rem[0]
    deadline = dif_rem[1]
    res = set_reminder(message.chat.id,deadline,description)
    if res: bot.send_message(message.chat.id,"Аааага, запомнилось!\n<i>Вы получать +15 социальных кредитов и кошка жену за это</i>",parse_mode="HTML")
    else: bot.send_message(message.chat.id,"Плакать охота, что-то пошло не так, повторите позже)")

@bot.message_handler(commands=["get_all_tasks"])
def print_all_tasks(message):
    res = get_all_tasks(message.chat.id)
    if res=="":
        bot.send_message(message.chat.id,"<i>О-Оуууууу...</i>\nУ вас нет никаких задач. Плохо это или хорошо?",parse_mode="HTML")
        return
    res = "Вы просили, мы сделали)\nВот список всех ваших задач:\n"+res
    bot.send_message(message.chat.id,res,parse_mode="HTML")

@bot.message_handler(commands=["get_tasks_on_date"])
def get_tasks_on_date_bot(message):
    bot.send_message(message.chat.id,"Ждем от вас дату, напомню формат:\n<i>дд.мм.гггг</i>\nВсе просто)",parse_mode="HTML")
    bot.register_next_step_handler(message,get_tasks_on_date_date)

def get_tasks_on_date_date(message):
    # try:
        res = get_date_tasks(message.text,message.chat.id)
        res = f"Ваш список мечты на дату: {message.text}\n"+res
        bot.send_message(message.chat.id,res,parse_mode="HTML")
    # except Exception as e:
    #     bot.send_message(message.chat.id,"Вы неправильно ввели дату(\nОбязательно попробуйте снова!")


def dd_run_out(chat_id, task):
    task_desc = task['description']
    bot.send_message(chat_id,f"Кажется, ваша задача <i>{task_desc}</i> истекла...\nНичего страшного, она продлена на 1 день, но кое-кому пора ее выполнить!",parse_mode="HTML")

def send_reminder(text,chat_id):
    bot.send_message(chat_id,f"Помнится, некоторое время назад вы сказали сами себе\n\n<b>{text}</b>\n\nПора выполнить обещание!",parse_mode="HTML")

def remind_task(chat_id,task_desc):
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