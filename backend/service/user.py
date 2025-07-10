import logging
from typing import Optional

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response, JSONResponse

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.user import CreateUserSchema
from common.database.models.user import UserModel



class UserService:

    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger = logging.getLogger('uvicorn.error')

    async def registr(self, user: CreateUserSchema) -> Response:
        user_model: UserModel = UserModel(
            chat_id=user.chat_id,
            user_id=user.user_id,
            name=user.name,
            username=user.username
        )

        try:
            self.session.add(user_model)
            await self.session.commit()
        except Exception as err:
            logging.error(err)
            await self.session.rollback()
            return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            await self.session.refresh(user_model)
            return Response(
                headers={
                    "location": f"/user/{user_model.id}"
                },
                status_code=status.HTTP_201_CREATED
            )
        
    async def get(self, id: int) -> JSONResponse:
        user = await self.session.get(UserModel, id)
        if user:
            return JSONResponse(
                content={
                    'chat_id': user.chat_id,
                    'user_id': user.user_id,
                    'name': user.name,
                    'username': user.username,
                },
                status_code=status.HTTP_200_OK
            )
        else:
            return Response(status_code=status.HTTP_404_NOT_FOUND)

    async def get_users_list(self, limit: int) -> JSONResponse|Response:
        statement = select(UserModel).limit(limit)
        
        try:
            response = await self.session.execute(statement)
        except Exception as err:
            self.logger.exception(err)
            return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        response = response.scalars().all()
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(response)
        )