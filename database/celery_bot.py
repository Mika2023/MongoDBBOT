from celery import Celery

app = Celery(
    'celery_bot',
    broker='rediss://:AaA5AAIjcDFhZjYxZmRhYzYxMDA0NGE0YmNkZTQ5NDU4MjNkYWZkZnAxMA@fast-crawdad-41017.upstash.io:6379?ssl_cert_reqs=required',
    backend='rediss://:AaA5AAIjcDFhZjYxZmRhYzYxMDA0NGE0YmNkZTQ5NDU4MjNkYWZkZnAxMA@fast-crawdad-41017.upstash.io:6379?ssl_cert_reqs=required',
    include=['database.tasks']
)

app.conf.update(
    result_expires=3600,
    broker_connection_retry_on_startup=True,  # Время жизни результата (1 час)
)

if __name__ == '__main__':
    app.start()