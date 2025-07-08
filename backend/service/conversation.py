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
        statement = select(MessageModel, GeneratedAnswerModel) \
                    .join(UserModel, UserModel.id == MessageModel.user_id) \
                    .join(GeneratedAnswerModel, GeneratedAnswerModel.message_id == MessageModel.id) \
                    .filter(UserModel.chat_id == chat_id) \
                    .filter(MessageModel.status == 'pending') \
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
                        'role': 'user',
                        'content': message
                    },
                    {
                        'role': 'assistant',
                        'content': answer
                    }
                ]
            )
        
        return JSONResponse(
            content=jsonable_encoder(conversation),
            status_code=200
        )
    
    

  
