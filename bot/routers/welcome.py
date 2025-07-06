from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)

from sqlalchemy.ext.asyncio import AsyncSession



router = Router(name="welcome-router")


@router.message(CommandStart())
async def command_start(message: Message):
    
    await message.answer(
        text="Привет! Я хорошо умею отвечать на вопросы.\n Давай попробуем! Задай мне вопрос или задачку!"
    )