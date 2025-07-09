import os

from redis.asyncio import Redis    
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)


engine = create_async_engine(
    url=f"postgresql+asyncpg://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}/{os.getenv("DB_NAME")}"
)
sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

redis = Redis(
    host=os.getenv("REDIS_HOST"),
    port=os.getenv("REDIS_PORT"),
    db=0,
    decode_responses=True
)