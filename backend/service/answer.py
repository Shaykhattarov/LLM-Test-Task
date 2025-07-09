
import os
import logging

from typing import Any, Optional, Union

from fastapi import status
from fastapi.responses import Response

from core.config import rabbit_broker
from service.message import MessageService

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

    async def create(self, message: dict) -> Optional[GeneratedAnswerModel]:
        answer: Optional[GeneratedAnswerModel] = await self.__create(message)
        
        if answer is None:
            self.logger.info("GeneratedAnswerService:create() -> failed")
            raise Exception("Не удалось создать ответа от модели")
        
        self.logger.info(f"GeneratedAnswerService:create() -> successfull({answer.id})")

        return answer

    async def approve(self, id: int) -> bool:
        approve_info: Optional[GeneratedAnswerModel] = await self.__select_approve_info(id)

        if approve_info is None:
            return False

        request_data: dict = {
            'chat_id': approve_info.chat_id,
            'content': approve_info.text
        }

        # Отправка сообщения через rabbit
        await rabbit_broker.connect()
        await rabbit_broker.publish(request_data, 'tgfrontend_messages')

        return True

    async def __select_approve_info(self, id: int) -> Optional[GeneratedAnswerModel]:
        statement = select(GeneratedAnswerModel) \
                    .join(MessageModel.user_id, GeneratedAnswerModel.message_id == MessageModel.id) \
                    .join(UserModel.chat_id, UserModel.id == MessageModel.user_id) \
                    .where(GeneratedAnswerModel.id == id)

        try:
            response = await self.session.execute(statement)
        except Exception as err:
            self.logger.exception("GeneratedAnswerService:__approve() - " + err)
            return False
        else:
            response = response.scalar_one_or_none()
            return response

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
        

