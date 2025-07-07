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
        

    is_create: bool = await messenger_service.create(message_schema)
    if not is_create:
        return await message.answer(
            text="Произошла неожиданная ошибка при отправке сообщения :("
        )
        