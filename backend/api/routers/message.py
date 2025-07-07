from typing import Annotated

from fastapi import (
    APIRouter, 
    Depends
)
from starlette.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.message import CreateMessageSchema
from service.message import MessageService
from api.dependencies import get_session


message_router = APIRouter("/message", tags=["Message"])


@message_router("/create")
async def create_message(message: CreateMessageSchema, session: Annotated[AsyncSession, Depends(get_session)]):
    service = MessageService(session)
    return await service.create(message)


@message_router("/{id}")
async def get_message(id: int, session: Annotated[AsyncSession, Depends(get_session)]):
    service = MessageService(session)
    return await service.get(id)
