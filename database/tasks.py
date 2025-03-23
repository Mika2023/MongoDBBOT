from database.celery_bot import app
from database.mongodb import add_task_to_mongodb, update_data_in_mongodb, delete_data_in_mongodb, add_many_tasks_to_mongodb,read_data

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
def read_tasks(chat_id):
    return read_data(chat_id)