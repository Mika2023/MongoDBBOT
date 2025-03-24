from database.tasks import *
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo  
import json

#нужно
#TODO:
#сделать получалки task_id 

tasks_ids_arr = []#для id задач
saved_tasks = [] #когда пользователь просит вывести задачи, они сохраняются
def get_task_id(description,chat_id):
    result_str = read_description.delay(description,chat_id)
    result = json.loads(result_str.get())
    return result["task"] if result['task'] else result['_id']

def get_task(description,chat_id):
    result_str = read_description.delay(description,chat_id)
    result = json.loads(result_str.get())
    res_str = result['description']+'\n' + f"сделать до:{result['deadline']}"
    return res_str


#добавить задачу в очередь, когда истечет - прислать напоминалку и продлить на день
def add_task_to_celery(task,task_id):
    deadline = datetime.strptime(task['deadline'],"%d.%m.%Y %H:%M").replace(tzinfo=ZoneInfo("Europe/Moscow")).astimezone(ZoneInfo("UTC")) #01.01.2025 23:59
    deadline_come_out.apply_async(args=[task_id],eta=deadline)

#устанавливать напоминания для определенной задачи - добавить напоминалку в очередь
def set_reminder(chat_id,deadline_str,text):
    try:
        deadline = datetime.strptime(deadline_str,"%d.%m.%Y %H:%M").replace(tzinfo=ZoneInfo("Europe/Moscow")).astimezone(ZoneInfo("UTC"))
        send_remind.apply_async(args=[text,chat_id],eta=deadline)
        return True
    except Exception as e:
        return False

#напоминать за некоторое время до дд о задаче
def remind_tasks(task,task_id):
    deadline = datetime.strptime(task['deadline'],"%d.%m.%Y %H:%M").replace(tzinfo=ZoneInfo("Europe/Moscow")).astimezone(ZoneInfo("UTC")) #01.01.2025 23:59
    remind_dd = deadline - timedelta(hours=3)
    from bot import remind_task
    remind_about_task.apply_async(args=[task_id],eta=remind_dd)

#добавить задачу - функция добавления одной задачи, функционал тот же, что и выше
def add_one_task(task):
    result = add_task.delay(task)
    task_id = result.get()
    add_task_to_celery(task,task_id)
    remind_tasks(task,task_id)

#составить список дел - функция добавления нескольких задач, внутри также в очередь добавляется счетчик до дд каждой задачи
def add_tasks_list(tasks_arr):
    result = add_tasks.delay(tasks_arr)
    tasks_ids = result.get()
    if tasks_ids==None: return False 
    for i in range(len(tasks_arr)):
        add_task_to_celery(tasks_arr[i],tasks_ids[i])
        remind_tasks(tasks_arr[i],tasks_ids[i])
    return True


#поставить задачу выполненной - обновить ее в бд и снять с очереди
def set_checked(task_num):
    task_id = ''
    for item in tasks_ids_arr:
        if item[0]==task_num:
            task_id = item[1]
            break
    if task_id=='': return
    update_task.delay(task_id,{'checked':'True'})

#изменить текст задачи - обновить ее в бд
def edit_text(task_num,text):
    task_id = ''
    print(tasks_ids_arr)
    for item in tasks_ids_arr:
        if item[0]==task_num:
            task_id = item[1]
            break
    if task_id=='': return
    update_task.delay(task_id,{'description':text})


#удалять все задачи на определенную дату
def delete_on_date(date,chat_id):
    delete_task_date.delay(date,chat_id)

#удалять определенные задачи на дату
def delete_concrete_task(tasks_nums):
    tasks_arr = []
    for item in tasks_ids_arr:
        if item[0] in tasks_nums: tasks_arr.append(item[1])
    delete_many_tasks.delay(tasks_arr)

#выводить задачи с оставшимся временем до них
def get_all_tasks(chat_id):
    result = read_tasks.delay(chat_id)
    tasks = result.get()
    if tasks==None:return ""
    # tasks = decode_redis_arr_dict(tasks_str)
    # tasks_str = tasks_str.replace("'", '"')
    # print(type(tasks_str),tasks_str)
    # tasks = json.loads(tasks_str)

    tasks_ids_arr.clear()
    res_str = ""
    i = 1
    for task in tasks:
        if task['checked']=='False': 
            res_str+=f"{i}. {task['description']}\n\t\tВремени осталось - "
            try:
                deadline = datetime.strptime(task['deadline'],"%d.%m.%Y %H:%M")
                time_left = deadline - datetime.now()
                res_str+=str(time_left)+"\n"
            except: print("к черту")
        else: res_str+=f"{i}. <s>{task['description']}</s>\n"
        tasks_ids_arr.append({i:task.get('_id')})
        i+=1
    return res_str

#выводить задачи на определенную дату
def get_date_tasks(date,chat_id):
    result = read_tasks_on_date.delay(date,chat_id)
    tasks_str = result.get()
    if tasks_str==None:return ""
    # tasks = decode_redis_arr_dict(tasks_str)

    res_str = ""
    i = 1
    tasks_ids_arr.clear()
    for task in tasks_str:
        if task['checked']=='False': 
            res_str+=f"{i}. {task['description']}\n\t\tВремени осталось - "
            try:
                deadline = datetime.strptime(task['deadline'],"%d.%m.%Y %H:%M")
                time_left = deadline - datetime.now()
                res_str+=str(time_left)+"\n"
            except: print("к черту")
        else: res_str+=f"{i}. <s>{task['description']}</s>\n"
        tasks_ids_arr.append({i:task.get('_id')})
        i+=1
    return res_str
