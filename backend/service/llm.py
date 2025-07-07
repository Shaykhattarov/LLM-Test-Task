
from database.models.generated_answer import GeneratedAnswerModel

from sqlalchemy.ext.asyncio import AsyncSession

class LLMService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_answer(self, answer: str):
        answer_model = GeneratedAnswerModel(
            message_id=1,
            text=answer
        )
        self.session.add(answer_model)
        await self.session.commit()