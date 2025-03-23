
# from database.celery_bot import app
from pymongo import MongoClient
import redis
from bson.objectid import ObjectId  # для idшников в бд

# Подключение к MongoDB
mongo_client = MongoClient('mongodb://localhost:27017/')
db = mongo_client['TelegramBotDB']
tasks_collection = db['tasks']

# Подключение к Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# insert
# @app.task
def add_task_to_mongodb(data):
    result = tasks_collection.insert_one(data)

    # Сохранение данных в Redis
    redis_key = f"task:{result.inserted_id}"
    redis_client.hset(redis_key, mapping=data)  # Используем mapping для словаря

    return str(result.inserted_id)

# @app.task
def add_many_tasks_to_mongodb(data):
    try:
        result = tasks_collection.insert_many(data)
        insert_id = result.inserted_ids
        # Сохранение данных в Redis
        for i, task_id in enumerate(insert_id):
            redis_key = f"task:{task_id}"
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

# @app.task
def read_data(chat_id):
    # Сначала смотрим Redis
    redis_key = f"chat_id:{chat_id}"

    # Попытка получить данные из Redis
    cached_data = redis_client.get(redis_key)
    if cached_data:
        print("Данные получены из Redis")
        return cached_data.decode('utf-8')  # Данные в Redis хранятся в виде строки

    # Если данных нет в Redis, загружаем из MongoDB
    results = list(tasks_collection.find({'chat_id': chat_id}, {'_id': 0}))
    if results:
        print("Данные получены из MongoDB")

        # Сохраняем данные в Redis
        redis_client.set(redis_key, str(results))  # Сохраняем как строку
        redis_client.expire(redis_key, 3600)  # Устанавливаем время жизни ключа (1 час)

        return results
    else:
        print(f"Данные для chat_id {chat_id} не найдены.")
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