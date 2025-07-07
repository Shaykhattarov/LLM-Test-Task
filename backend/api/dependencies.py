from sqlalchemy.ext.asyncio import AsyncSession
from database.engine import sessionmaker



async def get_session() -> AsyncSession:
    async with sessionmaker() as session:
        yield session