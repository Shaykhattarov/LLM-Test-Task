from typing import Annotated, List

from fastapi import (
    APIRouter, 
    Depends, 
    status
)
from starlette.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.user import CreateUserSchema
from service.user import UserService
from api.dependencies import get_session


user_router = APIRouter(prefix="/user", tags=["User"])


@user_router.post("/register")
async def registr_user(user: CreateUserSchema, session: Annotated[AsyncSession, Depends(get_session)]):
    service = UserService(session)
    return await service.registr(user) 


@user_router.get("/{id}")   
async def get_user(id: int, session: Annotated[AsyncSession, Depends(get_session)]):
    service = UserService(session)
    return await service.get(id)