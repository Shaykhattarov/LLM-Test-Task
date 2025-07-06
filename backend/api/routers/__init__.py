from fastapi import APIRouter

from routers import user



global_router = APIRouter()

global_router.include_router(user.router)