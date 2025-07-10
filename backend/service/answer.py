
import os
import logging

from typing import Any, List, Optional, Union

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response, JSONResponse

from core.config import rabbit_broker
from service.message import MessageService
from schemas.message import EditModelAnswerSchema
from schemas.answer import AnswerSchema

from common.database.models.user import UserModel
from common.database.models.message import MessageModel, MessageStatus
from common.database.models.to_send import ToSendModel
from common.database.models.generated_answer import GeneratedAnswerModel 

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession



class GeneratedAnswerService:

    def __init__(self, session: AsyncSession):
        self.session = session
        self.message_service = MessageService(self.session)
        self.logger = logging.getLogger('uvicorn.error')

    async def get(self, id: int) -> Optional[GeneratedAnswerModel]:
        answer: Optional[GeneratedAnswerModel] = await self.__get(id)
        return answer

    async def get_by_message_id(self, message_id: int):
        statement = select(GeneratedAnswerModel) \
                    .where(GeneratedAnswerModel.message_id == message_id)
        
        try:
            response = await self.session.execute(statement)
        except Exception as err:
            self.logger.exception(err)
            return Response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        response = response.scalar_one_or_none()

        if response is None:
            return Response(
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        answer_schema = AnswerSchema(
            id=response.id,
            message_id=response.message_id,
            text=response.text,
            created_at=response.created_at
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(answer_schema)
        )

    async def create(self, message: dict) -> Optional[GeneratedAnswerModel]:
        answer: Optional[GeneratedAnswerModel] = await self.__create(message)
        self.logger.info("Создаем ответ")
        if answer is None:
            self.logger.info("GeneratedAnswerService:create() -> failed")
            raise Exception("Не удалось создать ответа от модели")
        self.logger.info(f"Answer({answer.id}, {answer.message_id})")
        await self.message_service.update_status(answer.message_id, 'pending')
        self.logger.info(f"GeneratedAnswerService:create() -> successfull({answer.id})")
        return answer

    async def approve(self, id: int) -> bool:
        approve_info: Optional[List] = await self.__select_approve_info(id)

        if approve_info is None:
            return False

        answer_model: GeneratedAnswerModel = approve_info[0] 
        message_model: MessageModel = approve_info[1]
        user_model: UserModel = approve_info[2]

        request_data: dict = {
            'chat_id': user_model.chat_id,
            'content': answer_model.text,
        }

        # Изменяем статус сообщения на send
        await self.message_service.update_status(answer_model.message_id, 'send')
        
        # Отправка сообщения через rabbit
        await rabbit_broker.connect()
        await rabbit_broker.publish(request_data, 'tgfrontend_messages')

        return True


    async def edit(self, answer: EditModelAnswerSchema) -> Optional[GeneratedAnswerModel]:
        statement = update(GeneratedAnswerModel) \
                    .where(GeneratedAnswerModel.id == answer.id) \
                    .values(text=answer.text)

        try:
            await self.session.execute(statement)
            await self.session.commit()
        except Exception as err:
            self.logger.exception(err)
            return None
        else:
            response = await self.__get(answer.id)
            return response

    async def deny(self, id: int):
        approve_info: Optional[GeneratedAnswerModel] = await self.__select_approve_info(id)
        
        if approve_info is None:
            return False
        
        answer: GeneratedAnswerModel = approve_info[0]
        message: MessageModel = approve_info[1]

        self.logger.info(f"Message status: {message.status}")
        if message.status == 'send':
            return False
        
        request_data = {
            'id': message.id,
            'user_id': message.user_id,
            'role': 'user',
            'content': message.text
        }
        
        await self.message_service.update_status(answer.message_id, 'new')

        request_data = [{
            'id': message.id,
            'user_id': message.user_id,
            'role': 'user',
            'content': message.text
        }]

        # await rabbit_broker.connect()
        await rabbit_broker.publish(request_data, 'model_messages')

        statement = delete(GeneratedAnswerModel).where(GeneratedAnswerModel.id == answer.id)
        try:
            await self.session.execute(statement)
            await self.session.commit()
        except Exception as err:
            logging.error(f"AnswerService:__deny() - {err}")
            await self.session.rollback()
            return False
        
        return True
    

    async def __create(self, message: dict) -> Optional[GeneratedAnswerModel]:
        answer_model = GeneratedAnswerModel(
            message_id=message['message_id'],
            text=message['content']
        )
        try:
            self.session.add(answer_model)
            await self.session.commit()
        except Exception as err:
            logging.error(f"AnswerService:__create() - {err}")
            await self.session.rollback()
            return None
        else:
            await self.session.refresh(answer_model)
            # Обновляем статус сообщения
            await self.message_service._update_status(answer_model.message_id, 'pending')

        return answer_model

    async def __get(self, id: int) -> Optional[GeneratedAnswerModel]:
        """ Получение из БД ответа LLM по его ID """
        statement = select(GeneratedAnswerModel).where(GeneratedAnswerModel.id == id)
        try:
            response = await self.session.execute(statement)
        except Exception as err:
            self.logger.exception("GeneratedAnswerService:__get() - " + err)
            return None
        return response.scalar_one_or_none()
        
    async def __select_approve_info(self, id: int) -> Optional[List]:
        statement = select(GeneratedAnswerModel, MessageModel, UserModel) \
                    .join(MessageModel, GeneratedAnswerModel.message_id == MessageModel.id) \
                    .join(UserModel, UserModel.id == MessageModel.user_id) \
                    .filter(GeneratedAnswerModel.id == id)

        try:
            response = await self.session.execute(statement)
        except Exception as err:
            self.logger.exception(err)
            return None
        else:
            response = response.fetchall()
            if len(response) == 0:
                return None
            print(response)
            return response[0]
