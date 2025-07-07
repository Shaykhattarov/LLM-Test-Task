import logging

from typing import List

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.user import UserModel
from database.models.message import MessageModel
from database.models.generated_answer import GeneratedAnswerModel


class ConversationService:

    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger = logging.getLogger('uvicorn.error')

    async def get(self, chat_id: int) -> List | JSONResponse:
        statement = select(MessageModel) \
                    .join(UserModel, UserModel.id == MessageModel.user_id) \
                    .outerjoin_from(MessageModel, GeneratedAnswerModel, GeneratedAnswerModel.message_id == MessageModel.id) \
                    .filter(UserModel.chat_id == chat_id)
        
        try:
            response = await self.session.execute(statement)
        except Exception as err:
            self.logger.exception(f"ConversationService:get() - {err}")
            return []
        
        response = response.scalars().all()

        return JSONResponse(
            content=jsonable_encoder(response),
            status_code=200
        )

  
