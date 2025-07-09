from sqlalchemy.ext.asyncio import AsyncSession
from common.database.engine import sessionmaker


async def get_session() -> AsyncSession:
    async with sessionmaker() as session:
        yield session