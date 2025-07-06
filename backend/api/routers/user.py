from typing import Annotated, List

from fastapi import APIRouter, Depends, status
from starlette.responses import Response


router = APIRouter(prefix="/user", tags=["User"])


@router.get("/")
async def get_user():
    ...