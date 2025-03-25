
# from database.celery_bot import app
from ast import literal_eval
from datetime import datetime, timedelta
import json
from pymongo import MongoClient
import redis
from bson.objectid import ObjectId  # для idшников в бд

# Подключение к MongoDB
mongo_client = MongoClient('mongodb://mongo:MoumIPCDVnbgIkjltvuKHNDUJVdhZqBR@mongodb.railway.internal:27017')
db = mongo_client['TelegramBotDB']
tasks_collection = db['tasks']

# Подключение к Redis
redis_client = redis.Redis(
  host='fast-crawdad-41017.upstash.io',
  port=6379,
  password='AaA5AAIjcDFhZjYxZmRhYzYxMDA0NGE0YmNkZTQ5NDU4MjNkYWZkZnAxMA',
  ssl=True
)

# insert
# @app.task
def add_task_to_mongodb(data):
    result = tasks_collection.insert_one(data)

    # Сохранение данных в Redis
    redis_key = f"task:{str(result.inserted_id)}"
    redis_client.hset(redis_key, mapping=data)  # Используем mapping для словаря

    return str(result.inserted_id)

# @app.task
def add_many_tasks_to_mongodb(data):
    try:
        result = tasks_collection.insert_many(data)
        insert_id = result.inserted_ids
        # Сохранение данных в Redis
        for i, task_id in enumerate(insert_id):
            redis_key = f"task:{str(task_id)}"
            task_data = data[i].copy()  # Создаём копию данных
            task_data['_id'] = str(task_id)  # Добавляем ID в данные
            redis_client.hset(redis_key, mapping=task_data)  # Сохраняем данные в Redis

        inserted_ids_str = [str(task_id) for task_id in insert_id]
        return inserted_ids_str  # Возвращаем список строк
    except Exception as e:
        print("add many tasks завершилось с ошибкой: ", e)
        raise
        
    

# update
# @app.task
def update_data_in_mongodb(task_id, new_data):
    result = tasks_collection.update_one({'_id': ObjectId(task_id)}, {'$set': new_data})
    if result.modified_count > 0:
        # Redis
        redis_key = f"task:{task_id}"
        redis_client.hset(redis_key, mapping=new_data)  # Используем mapping для словаря
        print(f"Данные обновлены в Redis для ключа: {redis_key}")
        return True
    else:
        print(f"Задача с ID {task_id} не найдена.")
        return False
    
def update_data_in_mongodb_params(description,date,chat_id, new_data):
    result = tasks_collection.update_one({'description': description,'deadline':date,'chat_id':chat_id}, {'$set': new_data})
    if result.modified_count > 0:
        # Redis
        for key in redis_client.scan_iter("task:*"):
            task = redis_client.hgetall(key)
            task_dict = {}
            for key_task,value in task.items():
                task_dict[key_task.decode('utf-8')] = value.decode('utf-8')
            if 'deadline' in task_dict.keys() and 'chat_id' in task_dict.keys() and 'description' in task_dict.keys():
                if task_dict['chat_id']==chat_id and task_dict['deadline']==date and task_dict['description']==description:
                    redis_client.hset(key,mapping=new_data)
        print(f"Данные обновлены в Redis для ключа: {description}")
        return True
    else:
        print(f"Задача с ID {chat_id} не найдена.")
        return False

# delete
def delete_data_in_mongodb(task_id):
    result = tasks_collection.delete_one({'_id': ObjectId(task_id)})

    if result.deleted_count > 0:  # Используем deleted_count
        # Redis
        redis_key = f"task:{task_id}"
        redis_client.delete(redis_key)
        print(f"Данные удалены в Redis для ключа: {redis_key}")
        return True
    else:
        print(f"Задача с ID {task_id} не найдена.")
        return False

#delete all tasks on date    
def delete_tasks_on_date(deadline,chat_id):
    # target_date = datetime.strftime(deadline,"%d.%m.%Y")
    # start_date = datetime(target_date.year, target_date.month, target_date.day)
    # end_date = start_date + timedelta(days=1)
    
    # Удаляем и получаем количество
    result = tasks_collection.delete_many({
        "deadline": 
            {"$regex": f"^{deadline}"},
        "chat_id":chat_id
    })

    if result.deleted_count > 0:  # Используем deleted_count
        # Redis
        for key in redis_client.scan_iter("task:*"):
            task = redis_client.hgetall(key)
            task_dict = {}
            for key_task,value in task.items():
                task_dict[key_task.decode('utf-8')] = value.decode('utf-8')
            # print(task_dict,task_dict.keys())  
            if 'deadline' in task_dict.keys() and 'chat_id' in task_dict.keys() and task_dict['deadline'].startswith(deadline) and task_dict['chat_id']==chat_id:
                redis_client.delete(key)
                print(f"Данные удалены в Redis для ключа: {key}")
        return True
    else:
        print(f"Задача с дедлайном {deadline} не найдена.")
        return False

#delete an array of tasks
def delete_arr_tasks(tasks_arr):
    result = tasks_collection.delete_many({'_id':{
        "$in":[ObjectId(task) for task in tasks_arr]
    }})

    if result.deleted_count > 0:  # Используем deleted_count
        # Redis
        redis_client.delete(*[f'task:{task_id}' for task_id in tasks_arr])
        return True
    else:
        print(f"Задача не найдена.")
        return False

def delete_task_params(description,date,chat_id):
    # result = tasks_collection.delete_one({'deadline':date,'chat_id':chat_id,'description':description})
    
    result = tasks_collection.delete_one({'deadline':date,'chat_id':chat_id,'description':description})

    if result.deleted_count > 0:  # Используем deleted_count
        # Redis
        redis_key = f"task:{date}:{chat_id}:{description}"
        redis_client.delete(redis_key)
        print(f"Данные удалены в Redis для ключа: {redis_key}")
        return True
    else:
        print(f"Задача с дедлайном {date} не найдена.")
        return False
    
# @app.task
def read_data(chat_id):
    # Сначала смотрим Redis
    redis_key = f"chat_id:{chat_id}"

    tasks = []
    
    for key in redis_client.scan_iter("task:*"):
        if redis_client.type(key)==b'hash':
            task = redis_client.hgetall(key)
        else: task = redis_client.get(key)
        task_dict = {}
        for key_task,value in task.items():
            task_dict[key_task.decode('utf-8')] = value.decode('utf-8')
        if 'chat_id' in task_dict and task_dict['chat_id'] == chat_id:
            tasks.append(task_dict)
    if tasks: return tasks  # Данные в Redis хранятся в виде строки

    # Если данных нет в Redis, загружаем из MongoDB
    results = list(tasks_collection.find({'chat_id': chat_id},{'_id': 0}))
    if results:
        print("Данные получены из MongoDB")

        # Сохраняем данные в Redis
        # redis_client.hset(redis_key, str(results))  # Сохраняем как строку
        # redis_client.expire(redis_key, 3600)  # Устанавливаем время жизни ключа (1 час)

        return results
    else:
        print(f"Данные для chat_id {chat_id} не найдены.")
        return None

def read_task(task_id):
    redis_key = f"task:{task_id}"

    tasks = []
    
    for key in redis_client.scan_iter("task:*"):
        if redis_client.type(key)==b'hash':
            task = redis_client.hgetall(key)
        else: task = redis_client.get(key)
        task_dict = {}
        for key_task,value in task.items():
            task_dict[key_task.decode('utf-8')] = value.decode('utf-8')
        if '_id' in task_dict.keys() and task_dict['_id']==task_id:
            tasks.append(task_dict)
    if tasks: return tasks 

    # Если данных нет в Redis, загружаем из MongoDB
    results = list(tasks_collection.find({'task': task_id}))
    if results:
        print("Данные получены из MongoDB")

        # Сохраняем данные в Redis
        # redis_client.hset(redis_key, str(results))  # Сохраняем как строку

        return results
    else:
        print(f"Данные для task_id {task_id} не найдены.")
        return None

def read_date_tasks(date,chat_id):
    redis_key = f"task:{date}:{chat_id}"
    tasks = []
    
    # for key in redis_client.scan_iter("task:*"):
    #     task = redis_client.get(key).decode('utf-8')
    #     task = task.replace("'", '"')
    #     res = []
    #     try:    
    #         res = json.loads(task)
    #     except json.JSONDecodeError:
    #         # Вариант 2: Используем literal_eval как запасной вариант
    #         res = literal_eval(task)
    #     print(res)
    #     task_dict = {}
    #     # for key_task,value in task.items():
    #     #     task_dict[key_task.decode('utf-8')] = value.decode('utf-8')
        
    #     # if 'deadline' in task_dict.keys() and 'chat_id' in task_dict.keys() and task_dict['deadline'].startswith(date) and task_dict['chat_id']==chat_id:
    #     #     tasks.append(task_dict)
    #     break
    # if tasks: return tasks
    
    results = [str(doc['_id']) for doc in tasks_collection.find({
    "deadline": {"$regex": f"^{date}"},
    "chat_id": chat_id
    })]
    results = list(results)
    if results:
        print("Данные получены из MongoDB")

        # Сохраняем данные в Redis
        # redis_client.hset(redis_key, str(results))  # Сохраняем как строку

        return results
    else:
        print(f"Данные для date {date} не найдены.")
        return None
    
def read_desc_task(description,date,chat_id):
    redis_key = f"task:{description}:{chat_id}"

    tasks=[]
    for key in redis_client.scan_iter("task:*"):
        task = redis_client.hgetall(key)
        task_dict = {}
        for key_task,value in task.items():
            task_dict[key_task.decode('utf-8')] = value.decode('utf-8')
        if task_dict['deadline'].startswith(date) and task_dict['description']==description and task_dict['chat_id']==chat_id:
            tasks.append(task_dict)
    if tasks: return tasks
    
    results = tasks_collection.find_one({'description':description,'chat_id':chat_id,'deadline':date})
    if results:
        print("Данные получены из MongoDB")

        # Сохраняем данные в Redis
        redis_client.set(redis_key, str(results))  # Сохраняем как строку

        return results
    else:
        print(f"Данные для date {description} не найдены.")
        return None

# Пример использования
# if __name__ == "__main__":
#     # Добавление задач через Celery и ожидание их завершения
#     data = [
#         {'description': 'go to the darkness', 'deadline': '27.02.2025', 'chat_id': 123455},
#         {'description': 'go to the sky', 'deadline': '01.02.2025', 'chat_id': 123455},
#         {'description': 'go', 'deadline': '22.03.2025', 'chat_id': 987532}
#     ]
#     task1 = add_many_tasks_to_mongodb.delay(data)
#     # task1 = add_task_to_mongodb.delay({'description': 'go to the darkness', 'deadline': '27.02.2025', 'chat_id': 123455})
#     # task2 = add_task_to_mongodb.delay({'description': 'go to the sky', 'deadline': '01.02.2025', 'chat_id': 123455})
#     # task3 = add_task_to_mongodb.delay({'description': 'go', 'deadline': '22.03.2025', 'chat_id': 987532})

#     # Ждём завершения задач и получаем их task_id
#     task_result = task1.get()
#     # # Чтение данных для chat_id = 123455
#     a = read_data(123455)
#     print("Данные после добавления задач:")
#     print(a)

#     # # # Обновление задачи
#     update_data_in_mongodb.delay("67dec4414c73a2a2d8f7f233", {'description': 'Updated task'})

#     # # # Чтение данных после обновления
#     a = read_data(123455)
#     print("Данные после обновления задачи:")
#     print(a)

#     # # Удаление задачи
#     # delete_data_in_mongodb.delay(task_id)

#     # # Чтение данных после удаления
#     a = read_data(123455)
#     print("Данные после удаления задачи:")
#     print(a)