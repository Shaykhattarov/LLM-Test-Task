from typing import Optional
from database.models.message import MessageModel
from schemas.message import CreateMessageSchema

from sqlalchemy.ext.asyncio import AsyncSession



class MessengerService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, schema: CreateMessageSchema) -> Optional[int]:
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
            return None
    
        await self.session.refresh(message_model)
        return message_model.id
        