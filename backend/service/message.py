import json
import logging

from typing import Optional, List

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response, JSONResponse

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.message import CreateMessageSchema

from common.database.models.user import UserModel
from common.database.models.message import MessageModel
from common.database.models.generated_answer import GeneratedAnswerModel
 
from service.rabbit_client import RabbitClient




class MessageService:

    def __init__(self, session: AsyncSession):
        self.session = session
        self.rabbitmq = RabbitClient("llm_generate_answer")
        self.logger = logging.getLogger('uvicorn.error')


    async def create(self, schema: CreateMessageSchema):
        message: MessageModel = await self.__create(schema)

        # Если сообщение не создана возвращаем ошибку 500
        if message is None:
            return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Подготавливаем к отправке в RabbitMQ
        history: List[dict[str,str]] = await self.__history(chat_id=0, user_id=message.user_id)
        history.append({
            'id': message.id,
            'role': 'user',
            'content': message.text
        })
        rabbit_message: bytes = json.dumps(history).encode('utf-8') # Получаем массив bytes 
        await self.rabbitmq.publish_messages(rabbit_message) # Публикуем сообщение в rabbit

        # Возвращаем ответ о создании сообщения в БД
        return Response(
                headers={
                    'Location': f'/message/{message.id}'
                },
                status_code=status.HTTP_201_CREATED
            ) 

    async def get(self, id: int) -> Optional[int]:
        statement = select(MessageModel).where(MessageModel.id == id)
        result = await self.session.execute(statement)
        if result is None:
            return Response(
                status_code=status.HTTP_404_NOT_FOUND
            )
        return JSONResponse(
            content=jsonable_encoder(result),
            status_code=status.HTTP_200_OK
        )
    
    async def history(self, chat_id: int) -> JSONResponse:
        conversation = await self.__history(chat_id)
        
        return JSONResponse(
            content=jsonable_encoder(conversation), 
            status_code=200
        )
    
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
            self.logger.exception(f"ConversationService:get() - {err}")
            return []
        
        response = response.fetchall()
        
        conversation: List[dict] = []
        for message, answer in response:
            conversation.extend(
                [
                    {
                        'id': message.id,
                        'role': 'user',
                        'content': message.text
                    },
                    {
                        'id': message.id,
                        'role': 'assistant',
                        'content': answer.text
                    }
                ]
            )

        return conversation
    
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