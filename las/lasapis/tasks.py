# any app, e.g. myapp/tasks.py

from celery import shared_task
import time

@shared_task
def slow_add(x, y):
    time.sleep(5)
    return x + y
