from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from pydantic import ValidationError
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from service.user import UserService
from schemas.user import CreateUserSchema
from database.models.user import UserModel


router = Router(name="welcome-router")

@router.message(CommandStart())
async def welcome_handler(message: Message, session: AsyncSession):
    
    user_service = UserService(session)
    user_model: Optional[UserModel] = await user_service.get_by_chatid(chat_id=message.chat.id)

    if user_model is None:
        try:
            user_schema = CreateUserSchema(
                chat_id=message.chat.id,
                user_id=message.from_user.id,
                name=message.from_user.first_name,
                username=message.from_user.username,
            )
        except ValidationError as err:
            await message.answer(
                text="При авторизации произошла неожиданная ошибка"
            )
        else:
            is_create: bool = await user_service.create(user_schema)
            if not is_create:
                # Логирование
                await message.answer(
                    text="При авторизации произошла неожиданная ошибка"
                )
                return 

    await message.answer(
        text="Привет! Я Ollama. \n Задай вопрос, что я могу для вас сделать?"
    )