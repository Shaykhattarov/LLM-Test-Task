from contextlib import asynccontextmanager
import os
import asyncio
import logging

from datetime import datetime
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

from common.database.engine import sessionmaker
from faststream.rabbit import RabbitBroker

from core.middleware import DbSessionMiddleware
from core.config import on_startup_callback, on_shutdown_callback

from routers import (
    welcome,
    messenger,
    broker
)

# Создание экземпляра бота
bot = Bot(token=os.getenv("TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))


async def main():
    """ Входная точка программы """
    # Создание асинхронного движка для SQLAlchemy
    # engine = create_async_engine(
    #     url=f"postgresql+asyncpg://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}/{os.getenv("DB_NAME")}"
    # )
    # sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    # Созданеи диспетчера
    dp = Dispatcher()

    dp.startup.register(on_startup_callback)
    dp.shutdown.register(on_shutdown_callback)

    dp.update.middleware(DbSessionMiddleware(session_pool=sessionmaker))

    # Автоматическое добавление сессий на все callback-функции
    dp.callback_query.middleware(CallbackAnswerMiddleware())

    # Автоматическое добавление сессий на все callback-функции
    dp.callback_query.middleware(CallbackAnswerMiddleware())

    # Инициализация роутов
    dp.include_routers(
        welcome.router,
        messenger.router,
    )

    # Запуск основного потока
    await dp.start_polling(bot)


if __name__ == "__main__":
    log_path: str = os.path.join(os.path.dirname(__file__), "logs", f'{f"{datetime.now().strftime('%Y-%m-%d')}.logs"}')

    logging.basicConfig(
        level=logging.INFO,
        filename=log_path,
        filemode="a"
    )

    asyncio.run(main())
    
