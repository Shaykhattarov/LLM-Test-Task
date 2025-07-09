import os
import secrets
import logging

from datetime import datetime
from typing import (
    Annotated,
    Any,
)

from pydantic import (
    AnyUrl,
    BeforeValidator,
    computed_field,
)

from faststream.rabbit import RabbitBroker
from pydantic_settings import BaseSettings


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)



class Settings(BaseSettings):
    # model_config = SettingsConfigDict(
    #     env_file="../.env", env_ignore_empty=True, extra="ignore"
    # )
    # model_config['ignoring_types'] = True
    API_STR: str = "/api"
    SECRET_KEY: str = secrets.token_urlsafe(32)

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    # FRONTEND_HOST: str = "http://localhost:5173"
    # ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    BACKEND_CORS_ORIGIN: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = [

    ]

    @computed_field
    @property
    def all_cors_origins(self) -> list[str]:
        # return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGIN] + [
        #     self.FRONTEND_HOST
        # ]
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGIN]
    
    @property
    def rabbitmq_url(self) -> str:
        return f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/{self.RABBITMQ_VHOST}"

    RABBITMQ_HOST: str = os.getenv("RABBITMQ_HOST")
    RABBITMQ_PORT: str = os.getenv("RABBITMQ_PORT")
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"
    RABBITMQ_VHOST: str = "vhost"
    PROJECT_NAME: str = "IBS Test Task | Question-Answer Bot"
    POSTGRES_SERVER: str = os.getenv("DB_HOST")
    POSTGRES_PORT: int = os.getenv("DB_PORT")
    POSTGRES_USER: str = os.getenv("DB_USER")
    POSTGRES_PASSWORD: str = os.getenv("DB_PASSWORD")
    POSTGRES_DB: str = os.getenv("DB_NAME")
    # DATABASE_URL: str = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}/{POSTGRES_DB}"

settings = Settings()


# Создание брокера сообщений
rabbit_broker = RabbitBroker(
    host=settings.RABBITMQ_HOST,
    port=int(settings.RABBITMQ_PORT)
)