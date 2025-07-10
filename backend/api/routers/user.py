import logging
from typing import Annotated, Optional

from fastapi import (
    APIRouter, 
    Depends
)
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.user import CreateUserSchema
from service.user import UserService
from api.dependencies import get_session


user_router = APIRouter(prefix="/user", tags=["User"])
logger = logging.getLogger('uvicorn.error')


@user_router.post("/register/")
async def registr_user(user: CreateUserSchema, session: Annotated[AsyncSession, Depends(get_session)]):
    service = UserService(session)
    return await service.registr(user) 


@user_router.get("/{id}")   
async def get_user(id: int, session: Annotated[AsyncSession, Depends(get_session)]):
    service = UserService(session)
    return await service.get(id)

@user_router.get("/list/")
async def get_users_list(session: Annotated[AsyncSession, Depends(get_session)], limit: int = 10):
    service = UserService(session)
    return await service.get_users_list(limit)