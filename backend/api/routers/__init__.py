from fastapi import APIRouter

from api.routers.user import user_router
from api.routers.message import message_router
from api.routers.broker import rabbit_router


global_router = APIRouter()

global_router.include_router(user_router)
global_router.include_router(message_router)
global_router.include_router(rabbit_router)