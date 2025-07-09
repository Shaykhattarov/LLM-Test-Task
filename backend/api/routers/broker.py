import json
from typing import Annotated
from faststream.rabbit.fastapi import RabbitRouter
from core.config import settings
from api.dependencies import get_session
from fastapi import (
    Depends,
)
from service.answer import GeneratedAnswerService
from sqlalchemy.ext.asyncio import AsyncSession


rabbit_router = RabbitRouter(    
    host=settings.RABBITMQ_HOST,
    port=int(settings.RABBITMQ_PORT),
)

@rabbit_router.subscriber("backend_messages")
async def receive_model_messages(message: dict):
    print(message)
    with get_session() as session:
        service = GeneratedAnswerService(session)
        await service.create(message) # Добавляем ответ от модели в БД


@rabbit_router.subscriber("tgbackend_messages")
async def receive_telegram_messages(message: dict):
    print(message)
    # with get_session() as session:
        #service = GeneratedAnswerService(session)
        #wait service.create(message) # Добавляем ответ от модели в БД
    