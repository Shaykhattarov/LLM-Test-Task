import os
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)

from bot.database.middleware import DbSessionMiddleware


async def main():
    """ Входная точка программы """
    
    # Создание асинхронного движка для SQLAlchemy
    engine = create_async_engine(
        url=f"postgresql+asyncpg://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}/{os.getenv("DB_NAME")}"
    )
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

    # Созданеи диспетчера
    dp = Dispatcher()
    dp.update.middleware(DbSessionMiddleware(session_pool=sessionmaker))

    # Автоматическое добавление сессий на все callback-функции
    dp.callback_query.middleware(CallbackAnswerMiddleware())

    # Инициализация роутов
    dp.include_routers(

    )

    # Создание экземпляра бота
    bot = Bot(token=os.getenv("TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # Запуск основного потока
    await dp.start_polling(bot)


if __name__ == "__main__":
    # logging.basicConfig(
    #     level=logging.INFO,
        
    # )
    asyncio.run(main())
