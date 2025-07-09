import json
import logging

from typing import Optional, List

from datetime import datetime
from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response, JSONResponse

from sqlalchemy import select, desc, update
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.message import (
    CreateMessageSchema,
    MessageSchema,
    UpdateMessageSchema
)

from core.config import rabbit_broker

from common.database.models.user import UserModel
from common.database.models.message import MessageModel, MessageStatus
from common.database.models.generated_answer import GeneratedAnswerModel
 

class MessageService:

    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger = logging.getLogger('uvicorn.error')


    async def create(self, schema: CreateMessageSchema):
        message: MessageModel = await self.__create(schema)

        # Если сообщение не создана возвращаем ошибку 500
        if message is None:
            return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Подготавливаем к отправке в RabbitMQ
        history: List[dict[str,str]] = await self.__history(chat_id=0, user_id=message.user_id)
        history.append({
            'role': 'user',
            'id': message.id,
            'user_id': message.user_id,
            'content': message.text
        })

        self.logger.info(f"Send History To Model - length:{len(history)}")
        await rabbit_broker.connect()
        await rabbit_broker.publish(
            history,
            "model_messages",
        )
        
        # Возвращаем ответ о создании сообщения в БД
        return Response(
                headers={
                    'Location': f'/message/{message.id}'
                },
                status_code=status.HTTP_201_CREATED
            ) 

    async def get(self, id: int) -> Response | JSONResponse:
        # statement = select(MessageModel).where(MessageModel.id == id)
        message: Optional[MessageModel] = await self._get(id)
        if message is None:
            return Response(
                status_code=status.HTTP_404_NOT_FOUND
            )
        result = MessageSchema(
            id=message.id,
            user_id=message.user_id,
            text=message.text,
            status=message.status,
            created_at=message.created_at,
        )
        return JSONResponse(
            content=jsonable_encoder(result),
            status_code=status.HTTP_200_OK
        )

    async def getlist_status(self, mstatus: str) -> JSONResponse:
        if not isinstance(mstatus, str) and mstatus not in MessageStatus:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST)
        
        messages: List[dict] = await self.__getlist_status(mstatus)

        return JSONResponse(
            content=jsonable_encoder(messages),
            status_code=status.HTTP_200_OK
        )            

    async def history(self, chat_id: int, limit=5) -> JSONResponse:
        conversation = await self.__history(chat_id=chat_id, limit=limit)
        # self.logger.info(conversation)

        return JSONResponse(
            content=jsonable_encoder(conversation), 
            status_code=200
        )
    
    async def update_status(self, id: int, status: MessageStatus) -> bool:
        # self.logger.info(status, type(status))
        is_updated: bool = await self.__update_status(id, status)
        return is_updated

    async def __update_status(self, id: int, status: MessageStatus):
        statement = update(MessageModel) \
            .where(MessageModel.id == id) \
            .values(status=status)
        try:
            await self.session.execute(statement)
            await self.session.commit()
        except Exception as err:
            self.logger.exception(err)
            return False
        
        return True
        
    async def _get(self, id: int) -> Optional[MessageModel]:
        statement = select(MessageModel).where(MessageModel.id == id)
        try:
            result = await self.session.execute(statement)
        except Exception as err:
            self.logger.exception(f"ConversationService:get() - {err}")
            return None
        else:
            return result.scalar_one_or_none()
        
    async def __history(self, chat_id: int, user_id: int=None, limit: int = 5) -> List[dict[str]]:
        """ Получение истории сообщений пользователя по chat_id или user_id (костыльно) """
        if user_id is None:
            statement = select(MessageModel, GeneratedAnswerModel) \
                    .join(GeneratedAnswerModel, GeneratedAnswerModel.message_id == MessageModel.id) \
                    .join(UserModel, UserModel.chat_id == chat_id) \
                    .filter(MessageModel.status == 'send') \
                    .limit(limit) \
                    .order_by(desc(MessageModel.created_at))
                          
        else:
            statement = select(MessageModel, GeneratedAnswerModel) \
                    .join(UserModel, UserModel.id == MessageModel.user_id) \
                    .join(GeneratedAnswerModel, GeneratedAnswerModel.message_id == MessageModel.id) \
                    .filter(MessageModel.status == 'send') \
                    .filter(UserModel.id == user_id) \
                    .order_by(desc(MessageModel.created_at)) \
                    .limit(limit) \
                    .order_by(MessageModel.created_at)
                                        
        
        try:
            response = await self.session.execute(statement)
        except Exception as err:
            self.logger.exception(f"ConversationService:__history() - {err}")
            return []
        
        response = response.fetchall()
        
        conversation: List[dict] = []
        for message, answer in response:
            conversation.extend(
                [
                    {
                        'role': 'user',
                        'content': message.text
                    },
                    {
                        'role': 'assistant',
                        'content': answer.text
                    }
                ]
            )

        return conversation
    
    async def _update(self, updated_message: UpdateMessageSchema) -> Optional[MessageModel]:
        message_model = MessageModel(
            id=updated_message.id,
            user_id=updated_message.user_id,

        )

    async def __create(self, message: CreateMessageSchema) -> Optional[MessageModel]:
        message_model = MessageModel(
            user_id=message.user_id,
            text=message.text,
            status='new'
        )
        try:
            self.session.add(message_model)
            await self.session.commit()
        except Exception as err:
            logging.error(f"MessageService:create() - {err}")
            await self.session.rollback()
            return None
        else:
            await self.session.refresh(message_model)

        return message_model
    
    async def __getlist_status(self, mstatus: str, limit:int=50, order_by:str="asc") -> List[dict[str]]:
        if order_by.lower() == "asc":
            statement = select(MessageModel) \
                .where(MessageModel.status == mstatus) \
                .limit(limit) \
                .order_by(MessageModel.created_at)
        else:
            statement = select(MessageModel) \
                .where(MessageModel.status == mstatus) \
                .limit(limit) \
                .order_by(desc(MessageModel.created_at))
            
        try:
            response = await self.session.execute(statement)
        except Exception as err:
            self.logger.exception("MessageService:get_status() - " + err)
            return []
        else:
            response = response.scalars().all()
            result: List[dict[str]] = []
            for message in response:
                created_at: datetime = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
                result.append(
                    {
                        'id': message.id,
                        'user_id': message.user_id,
                        'text': message.text,
                        'status': message.status,
                        'created_at': created_at,
                    }
                )
            return result
        
    async def _update_status(self, mid: int, mmstatus: MessageStatus) -> True:
        statement = update(MessageModel).where(MessageModel.id == mid) \
            .values(status=mmstatus)
        
        try:
            await self.session.execute(statement)
        except Exception as err:
            self.logger.exception(f"MessageService:_update_status() - {err}")
            return False
        else:
            self.logger.info("MessageService:_update_status() - successfull")

        return True
        
