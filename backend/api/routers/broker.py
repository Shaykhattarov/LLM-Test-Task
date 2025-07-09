import json
from typing import Annotated
from faststream.rabbit.fastapi import RabbitRouter
from core.config import settings
from fastapi import Depends
from api.dependencies import get_session
from fastapi import (
    Depends,
)
from common.database.engine import sessionmaker
from service.answer import GeneratedAnswerService


rabbit_router = RabbitRouter(    
    host=settings.RABBITMQ_HOST,
    port=int(settings.RABBITMQ_PORT),
)

@rabbit_router.subscriber("backend_messages")
async def receive_model_messages(message: dict):
    
    async with sessionmaker() as session:
        service = GeneratedAnswerService(session)
        await service.create(message) # Добавляем ответ от модели в БД
