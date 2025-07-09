import logging
from typing import Annotated

from fastapi import (
    APIRouter, 
    Depends,
    status
)

from fastapi.responses import Response

from sqlalchemy.ext.asyncio import AsyncSession

from schemas.message import CreateMessageSchema, EditModelAnswerSchema
from service.message import MessageService
from service.answer import GeneratedAnswerService
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
async def get_messages_history(chat_id: int, session: Annotated[AsyncSession, Depends(get_session)]):
    logging.info(f"Router:/message/history - {chat_id}")
    service = MessageService(session)
    return await service.history(chat_id)

@message_router.get("/status/{status}")
async def get_messages_by_status(status: str, session: Annotated[AsyncSession, Depends(get_session)]):
    logging.info(f"Router:/message/status/ - {status}")
    service = MessageService(session)
    return await service.getlist_status(status)


@message_router.post("/answer/approve/{answer_id}")
async def approve_model_answer(answer_id: int, session: Annotated[AsyncSession, Depends(get_session)]):
    service = GeneratedAnswerService(session)
    response = await service.approve(answer_id)
    if not response:
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )

@message_router.post("/answer/edit")
async def edit_model_answer(answer: EditModelAnswerSchema, session: Annotated[AsyncSession, Depends(get_session)]):
    service = GeneratedAnswerService(session)
    return await service.edit(answer)

@message_router.post("/answer/deny/{answer_id}")
async def deny_model_answer(answer_id: int, session: Annotated[AsyncSession, Depends(get_session)]):
    service = GeneratedAnswerService(session)
    return await service.deny(answer_id)