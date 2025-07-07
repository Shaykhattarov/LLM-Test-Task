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

from bot.settings import settings
from bot.utils.caching import generate_cache_key

from sqlalchemy.ext.asyncio import AsyncSession


router = Router(name="messenger-router")

@router.message()
async def messenger_handler(message: Message, session: AsyncSession):
    
    user_service = UserService(session)
    user: Optional[UserModel] = user_service.get_by_chatid(message.chat.id)

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
    cached_response = settings.redis_host.get(cache_key)
    if cached_response:
        # Если попали в кеш, то возвращаем ответ
        return await message.answer(
            text=cached_response
        )

    # Если сообщения нет в кеше, то обрабатываем дальше (передаем на backend через celery)
    settings.celery_host.send_task("process_message_task", kwargs={"user": user.id, "message": message.text})

    

        