import os

from celery import Celery


celery = Celery(
    'celery',
    broker=f"redis://{os.getenv("REDIS_HOST")}:{os.getenv("REDIS_PORT")}/0",
    backend=f"redis://{os.getenv("REDIS_HOST")}:{os.getenv("REDIS_PORT")}/1",
    include=["worker.tasks"]
)

celery.conf.update(task_track_started=True)