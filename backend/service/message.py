import logging

from typing import Optional, List

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.message import CreateMessageSchema
from database.models.message import MessageModel
from database.models.user import UserModel

from sqlalchemy import select


class MessageService:

    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger = logging.getLogger('uvicorn.error')

    async def create(self, schema: CreateMessageSchema):
        message_model = MessageModel(
            user_id=schema.user_id,
            text=schema.text,
            status='new'
        )
        try:
            self.session.add(message_model)
            await self.session.commit()
        except Exception as err:
            logging.error(f"MessageService:create() - {err}")
            print(err)
            await self.session.rollback()
            return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            await self.session.refresh(message_model)
            return Response(
                headers={
                    'Location': f'/message/{message_model.id}'
                },
                status_code=status.HTTP_201_CREATED
            )
    
    async def get(self, id: int) -> Optional[int]:
        statement = select(MessageModel).where(MessageModel.id == id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()
    
    async def get_conversation(self, chat_id: int) -> List:
        statement = select(MessageModel) \
                    .join(UserModel, MessageModel.user_id == UserModel.id) \
                    .filter(UserModel.chat_id == chat_id) \
                    .order_by(MessageModel.created_at)
        try:
            response = await self.session.execute(statement)
        except Exception as err:
            self.logger.exception(f"MessageService:get_conversation() - {err}")
            return []
        
        response = response.scalars().all()
        print(response)
        return JSONResponse(content=jsonable_encoder(response), status_code=200)
        
        
