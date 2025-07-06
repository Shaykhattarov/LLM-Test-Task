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
async def command_start():
    ...