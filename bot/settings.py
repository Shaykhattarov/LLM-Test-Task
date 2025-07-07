import os

from redis import Redis
from celery import Celery

from pydantic_settings import BaseSettings 




class Settings(BaseSettings):

    redis_host = Redis(
        host=os.getenv("REDIS_HOST"),
        port=os.getenv("REDIS_PORT"),
        db=0,
        decode_responses=True
    )

    celery_host = Celery('bot', broker=os.getenv("CELERY_BROKER_URL"))

settings = Settings()