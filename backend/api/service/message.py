import logging

from fastapi import status
from fastapi.responses import Response, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas.message import CreateMessageSchema
from database.models.message import MessageModel



class MessageService:

    def __init__(self, session: AsyncSession):
        self.session = session

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
    
    async def get(self, id: int):
        ...