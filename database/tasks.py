from database.celery_bot import app
from database.mongodb import *

from datetime import datetime,timedelta,date,time
import json

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

@app.task
def deadline_come_out(task_id):

    task_str = read_task(task_id)
    if task_str=="": return #если ничего нет
    task = json.loads(task_str)
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
def remind_about_task(task,task_id):
    task_str = read_task(task_id)
    if task_str==None: return #если ничего нет
    task = json.loads(task_str)
    if task['checked']=='True': return #если задача выполнена

    from bot import remind_task
    chat_id = task['chat_id']
    remind_task(task,chat_id)

@app.task
def read_tasks_on_date(date,chat_id):
    return read_date_tasks(date,chat_id)

@app.task
def read_description(description,chat_id):
    return read_desc_task(description,chat_id)
