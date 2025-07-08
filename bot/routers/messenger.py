import os
import json
import logging
import aiohttp

from aiogram import Router
from aiogram.types import (
    Message,
)
from typing import Optional

from service.user import UserService
from common.database.models.user import UserModel
from common.database.engine import redis
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

    # Генерация хеш-ключа для кеша
    cache_key = generate_cache_key(message.text)
    
    # Поиск кеша по ключу
    cached_response = await redis.get(cache_key)
    if cached_response:
        # Если попали в кеш, то возвращаем ответ
        return await message.answer(
            text=cached_response
        )

    # Отправка сообщения на сервер 
    async with aiohttp.ClientSession() as session:
        url = os.getenv("BACKEND_ENDPOINT") + "/api/message/create"
        data = {
            "user_id": user.id,
            "text": message.text,
            "status": 'new'
        }
        headers = {
            'content-type': 'application/json',
            'accept': '*'
        }
        async with session.post(url, data=json.dumps(data), headers=headers) as response:           
            status_code = response.status
            headers = response.headers

            if status_code == 201:
                logging.info(f"Create new message with path: {headers['location']}")
            else:
                logging.error(f"Error in creating new message: {status_code} - {headers}")

    return await message.answer(
        text="Ожидание ответа..."
    )
    
    

        