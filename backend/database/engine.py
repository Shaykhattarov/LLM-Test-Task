from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)
from core.config import settings


engine = create_async_engine(settings.DATABASE_URL)
sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
