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
        
        # await self.rabbitmq.connect() # Создаем соединение с rabbitmq
        # await self.rabbitmq.publish(history) # Публикуем сообщение

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
            content=result.model_dump_json(),
            status_code=status.HTTP_200_OK
        )

    async def getlist_status(self, mstatus: MessageStatus) -> JSONResponse:
        if not isinstance(mstatus, str) or not isinstance(mstatus, MessageStatus):
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST)
        
        messages: List[dict] = await self.__getlist_status(mstatus)

        return JSONResponse(
            content=jsonable_encoder(messages),
            status_code=status.HTTP_200_OK
        )            

    async def history(self, chat_id: int) -> JSONResponse:
        conversation = await self.__history(chat_id)
        
        return JSONResponse(
            content=jsonable_encoder(conversation), 
            status_code=200
        )
    
    async def update(self, updated_message: UpdateMessageSchema) -> Response:
        ...



    async def _get(self, id: int) -> Optional[MessageModel]:
        statement = select(MessageModel).where(MessageModel.id == id)
        try:
            result = await self.session.execute(statement)
        except Exception as err:
            self.logger.exception(f"ConversationService:get() - {err}")
            return None
        else:
            return result.scalar_one_or_none()
        
    async def __history(self, chat_id: int, user_id: int=None, limit: int = 10) -> List[dict[str]]:
        """ Получение истории сообщений пользователя по chat_id или user_id (костыльно) """
        if user_id is None:
            statement = select(MessageModel, GeneratedAnswerModel) \
                    .join(UserModel, UserModel.id == MessageModel.user_id) \
                    .join(GeneratedAnswerModel, GeneratedAnswerModel.message_id == MessageModel.id) \
                    .filter(UserModel.chat_id == chat_id) \
                    .filter(MessageModel.status != 'new') \
                    .order_by(desc(MessageModel.created_at)) \
                    .limit(limit) \
                    .order_by(MessageModel.created_at)
        else:
            statement = select(MessageModel, GeneratedAnswerModel) \
                    .join(UserModel, UserModel.id == MessageModel.user_id) \
                    .join(GeneratedAnswerModel, GeneratedAnswerModel.message_id == MessageModel.id) \
                    .filter(UserModel.id == user_id) \
                    .filter(MessageModel.status != 'new') \
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
    
    async def __getlist_status(self, mstatus: MessageStatus, limit:int=50, order_by:str="asc") -> List[dict[str]]:
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
        
