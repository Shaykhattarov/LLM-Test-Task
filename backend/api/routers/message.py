import logging
from typing import Annotated

from fastapi import (
    APIRouter, 
    Depends,
    Request
)
from starlette.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.message import CreateMessageSchema
from service.message import MessageService
from service.conversation import ConversationService
from api.dependencies import get_session


message_router = APIRouter(prefix="/message", tags=["Message"])
logger = logging.getLogger('uvicorn.error')


@message_router.post("/create")
async def create_message(message: CreateMessageSchema, session: Annotated[AsyncSession, Depends(get_session)]):
    logging.info(f"Router:/message/create - {message.user_id}, {message.text}")
    service = MessageService(session)
    return await service.create(message)


@message_router.get("/{id}")
async def get_message(id: int, session: Annotated[AsyncSession, Depends(get_session)]):
    service = MessageService(session)
    return await service.get(id)


@message_router.get("/history/{chat_id}")
async def get_message_chat(chat_id: int, session: Annotated[AsyncSession, Depends(get_session)]):
    logging.info(f"Router:/message/history - {chat_id}")
    service = MessageService(session)
    return await service.history(chat_id)
