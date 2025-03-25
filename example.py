import time
from database.tasks import add_tasks,read_tasks,add_task,update_task,send_remind,remind_about_task
from bot import remind_task
from controller import *
data = [
    {'description': 'go to the darkness', 'deadline': '27.02.2025', 'chat_id': 123455},
    {'description': 'go to the sky', 'deadline': '01.02.2025', 'chat_id': 123455},
    {'description': 'go', 'deadline': '22.03.2025', 'chat_id': 987532}
]
# delete_on_date('25.03.2025',1494200750)
# data = {'description': 'go to the darkness', 'deadline': '27.02.2025', 'chat_id': 123455}

# res = add_tasks.delay(data)
# ids = res.get()
# a = read_tasks.delay(123455)
# # print(a.get())
# update_task.delay("67e060cbeb47c198ec86ab88", {'description': 'Updated task'})
# a = read_tasks.delay(123455)
# print(a.get())
# print(result.get())
#task_id = result.get()


# from celery import Celery

# app = Celery('myapp', broker='redis://localhost:6379/0')

# @app.task
# def add_tasks(x,y):
#     return x+y

# # Вызов задачи
# # tasks = [
# #     {'description': 'go to the darkness', 'deadline': '27.02.2025', 'chat_id': 123455},
# #     {'description': 'go to the sky', 'deadline': '01.02.2025', 'chat_id': 123455},
# #     {'description': 'go', 'deadline': '22.03.2025', 'chat_id': 987532}
# # ]

# add_tasks.delay(10,10)
    