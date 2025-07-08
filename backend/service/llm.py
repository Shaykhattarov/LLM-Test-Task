import aio_pika

from abc import ABC

from database.models.generated_answer import GeneratedAnswerModel

from sqlalchemy.ext.asyncio import AsyncSession



class LLMService:

    def __init__(self):
        pass

    async def publish_message(self, conversation: list, new_message: str):
        ...
    
