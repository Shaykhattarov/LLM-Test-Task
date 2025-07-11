from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs



class BaseModel(AsyncAttrs, DeclarativeBase):
    __abstract__ = True
