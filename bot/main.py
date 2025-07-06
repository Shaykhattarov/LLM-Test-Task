import os
from aiogram import Bot, Dispatcher

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)


async def main():
    engine = create_async_engine(
        url=f"postgresql+asyncpg://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}/{os.getenv("DB_NAME")}"
    )
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)


if __name__ == "__main__":
    main()
