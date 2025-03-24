from ast import literal_eval
from database.celery_bot import app
from database.mongodb import *
import sys

from datetime import datetime,timedelta,date,time
import json

# setting path
sys.path.append('../mongodbbot')

@app.task
def add_task(data):
    return add_task_to_mongodb(data)

@app.task
def add_tasks(data):
    return add_many_tasks_to_mongodb(data)

@app.task
def update_task(task_id, new_data):
    return update_data_in_mongodb(task_id, new_data)

@app.task
def delete_task(task_id):
    return delete_data_in_mongodb(task_id)

@app.task
def delete_task_date(date,chat_id):
    return delete_tasks_on_date(date,chat_id)

@app.task
def delete_many_tasks(tasks_arr):
    return delete_arr_tasks(tasks_arr)

@app.task
def read_tasks(chat_id):
    return read_data(chat_id)

@app.task
def read_task_task(task_id):
    return read_task(task_id)

def decode_redis_data(redis_dict):
    """Преобразует словарь с bytes-ключами и значениями в обычный dict."""
    decoded = {}
    for key, value in redis_dict.items():
        # Декодируем ключ и значение из bytes в str
        decoded[key.decode('utf-8')] = value.decode('utf-8')
    return decoded

def decode_redis_arr_dict(redis_dict):
    """Преобразует список словарей с bytes-ключами и значениями в обычный arr."""
    """Ручной парсинг для особо сложных случаев"""
    json_str = redis_dict.replace("'", '"')
        
        # Экранируем оставшиеся кавычки внутри строк
    json_str = json_str.replace('": "', '": \\"').replace('", "', '\\", "')
    try:    
        return json.loads(json_str)
    except json.JSONDecodeError:
            # Вариант 2: Используем literal_eval как запасной вариант
        return literal_eval(redis_dict)
    


@app.task
def deadline_come_out(task_id):

    task_str = read_task(task_id)
    if task_str==None: return #если ничего нет
    # task = json.loads(task_str)
    task = decode_redis_data(task_str)
    if task['checked']=='True': return #если задача выполнена

    deadline = datetime.strptime(task['deadline'],"%d.%m.%Y %H:%M")
    new_deadline = deadline + timedelta(days=1)
    update_data_in_mongodb(task_id,{"deadline":new_deadline.strftime("%d.%m.%Y %H:%M")})
    from bot import dd_run_out
    chat_id = task['chat_id']
    dd_run_out(chat_id,task)



@app.task
def send_remind(text,chat_id):
    from bot import send_reminder
    send_reminder(text,chat_id)

@app.task
def remind_about_task(task_id):
    task_str = read_task(task_id)
    if task_str==None: return #если ничего нет
    # task = json.loads(task_str)
    task = decode_redis_data(task_str)
    if task['checked']=='True': return #если задача выполнена

    # from .tasks_and_bot import remind_task_and_bot
    from bot import remind_task
    chat_id = task['chat_id']
    remind_task(chat_id,task_desc=task['description'])

@app.task
def read_tasks_on_date(date,chat_id):
    return read_date_tasks(date,chat_id)

@app.task
def read_description(description,chat_id):
    return read_desc_task(description,chat_id)

