from celery import Celery

app = Celery(
    'celery_bot',
    broker='redis://127.0.0.1:6379/0',
    backend='redis://127.0.0.1:6379/0',
    include=['database.tasks']
)

app.conf.update(
    result_expires=3600,
    broker_connection_retry_on_startup=True,  # Время жизни результата (1 час)
)

if __name__ == '__main__':
    app.start()