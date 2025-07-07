import logging

from database.models.user import UserModel
from schemas.user import CreateUserSchema

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession



class UserService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, schema: CreateUserSchema) -> bool:
        user_model = UserModel(
            chat_id=schema.chat_id,
            user_id=schema.user_id,
            name=schema.name,
            username=schema.username
        )

        try:
            self.session.add(user_model)
            await self.session.commit()
        except Exception as err:
            await self.session.rollback()
            logging.error("Ошибка при создании пользователя: ", err)
            return False
        else:
            await self.session.refresh(user_model)
            return True

    async def get_by_chatid(self, chat_id: str) -> Optional[UserModel]: 
        statement = select(UserModel).where(UserModel.chat_id == chat_id)
        try:
            result = await self.session.execute(statement)
        except Exception as err:
            logging.error("Ошибка при получении данных пользователя: ", err)
            return None
        user: Optional[UserModel] = result.scalars().one_or_none()
        return user
