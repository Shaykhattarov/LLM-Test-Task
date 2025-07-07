import os
import logging
import aiohttp

from aiogram import Router
from aiogram.types import (
    Message,
)
from typing import Optional
from pydantic import ValidationError


from service.user import UserService
from service.messenger import MessengerService
from schemas.message import CreateMessageSchema
from database.models.user import UserModel
from database.redis import redis_client
from utils.caching import generate_cache_key

from sqlalchemy.ext.asyncio import AsyncSession


router = Router(name="messenger-router")

@router.message()
async def messenger_handler(message: Message, session: AsyncSession):
    
    user_service = UserService(session)
    user: Optional[UserModel] = await user_service.get_by_chatid(message.chat.id)

    if not user:
        return await message.answer(
            text="Ооо, вы новый пользователь бота. Начните работу выполнив команду: /start"
        )
    
    messenger_service = MessengerService(session)
    try:
        message_schema = CreateMessageSchema(
            user_id=user.id,
            text=message.text
        )
    except ValidationError as err:
        return await message.answer(
            text="Длина сообщения не может быть больше 4096 символов"
        )
        
    # Добавляем в БД новое сообщение и получаем id
    message_id: int = await messenger_service.create(message_schema)
    if message_id is None:
        return await message.answer(
            text="Произошла неожиданная ошибка при отправке сообщения :("
        )
    
    # Генерация хеш-ключа для кеша
    cache_key = generate_cache_key(message.text)
    
    # Поиск кеша по ключу
    cached_response = await redis_client.get(cache_key)
    if cached_response:
        # Если попали в кеш, то возвращаем ответ
        return await message.answer(
            text=cached_response
        )

    # Если сообщения нет в кеше, то обрабатываем дальше (передаем на backend через celery)
    # settings.celery_host.send_task("process_message_task", args=[message_id, ])

    async with aiohttp.ClientSession() as session:
        url = os.getenv("BACKEND_ENDPOINT") + "/message/create"
        data = {
            "user_id": user.id,
            "text": message.text,
            "status": 'new'
        }
        headers = {}
        async with session.post(url, data=data) as response:           
            status_code = response.status
            headers = response.headers
            if status_code == 201:
                logging.info(f"Create new message with path: {headers['location']}")
            else:
                logging.error(f"Error in creating new message: {status_code}")
    
    

        