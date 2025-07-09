import os
import logging

from typing import Optional

from fastapi import status
from fastapi.responses import Response, JSONResponse

from service.user import UserService
from service.message import MessageService

from common.broker.rabbitmq import RabbitMQClient
from common.database.models.user import UserModel
from common.database.models.message import MessageModel
from common.database.models.to_send import ToSendModel
from common.database.models.generated_answer import GeneratedAnswerModel 

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession



class GeneratedAnswerService:

    def __init__(self, session: AsyncSession):
        self.session = session
        self.message_service = MessageService(self.session)
        self.logger = logging.getLogger('uvicorn.error')

    async def get(self, id: int):
        ...

    async def create(self, message: dict):
        answer = await self.__create(message)
        
        if answer is None:
            self.logger.info("GeneratedAnswerService:create() -> failed")
            raise Exception("Не удалось создать ответа от модели")
        
        self.logger.info(f"GeneratedAnswerService:create() -> successfull({answer.id})")

    async def approve(self, id: int):
        to_send: Optional[ToSendModel] = self.__approve(id)
        
        if to_send is None:
            return Response(
                status_code=status.HTTP_404_NOT_FOUND
            )

        # Получение текста ответа пользователю
        answer: Optional[GeneratedAnswerModel] = self.__get(to_send.answer_id)       
        user: Optional[UserModel] = self.__get_receiver(answer.id)
        formatted_answer = {
            'chat_id': '',
        }

    async def edit(self):
        ...

    async def deny(self, ):
        ...
    
    async def __create(self, message: dict) -> Optional[GeneratedAnswerModel]:
        answer_model = GeneratedAnswerModel(
            message_id=message['id'],
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


    async def __approve(self, id: int) -> Optional[ToSendModel]:
        answer: Optional[GeneratedAnswerModel] = await self.__get(id)
        message: Optional[MessageModel] = await self.message_service._get(answer.message_id)

        if answer is None:
            self.logger.exception("GeneratedAnswerService:__approve() - answer is None")
            return None
        
        to_send = ToSendModel(
            answer_id=answer.id
        )
        try:
            self.session.add(to_send)
            await self.session.commit()
        except Exception as err:
            self.logger.exception("GeneratedAnswerService:__approve() - " + err)
            await self.session.rollback()
            return None
        else:
            await self.session.refresh(to_send)
            return to_send
        
    async def __get_receiver(self, answer_id: int) -> Optional[UserModel]:
        statement = select(UserModel) \
            .join(GeneratedAnswerModel, GeneratedAnswerModel == answer_id) \
            .join(MessageModel, MessageModel.id == GeneratedAnswerModel.message_id) \
            .where(UserModel.id == MessageModel.user_id)
        
        try:
            response = await self.session.execute(statement)
        except Exception as err:
            self.logger.exception("GeneratedAnswerService:__get_receiver() - " + err)
            return None
        return response.scalar_one_or_none()
        

