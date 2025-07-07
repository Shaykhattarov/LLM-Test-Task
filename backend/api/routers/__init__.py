from fastapi import APIRouter

from api.routers.user import user_router



global_router = APIRouter()

global_router.include_router(user_router)