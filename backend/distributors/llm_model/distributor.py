import os
import asyncio
import aiohttp

from ollama import AsyncClient

from service.message import MessageService
from service.conversation import ConversationService

from database.models.user import UserModel
from database.models.message import MessageModel
from database.models.generated_answer import GeneratedAnswerModel

from sqlalchemy.ext.asyncio import AsyncSession


async def send_prompt_to_llm(message: bytes, session: AsyncSession):
    
    client = AsyncClient(
        host=os.getenv("OLLAMA_ENDPOINT"),
        headers={
            'content-type': 'application/json',
            'accept': '*'
        }
    )

    response = await client.chat(
        model="llama3.2",
        messages=[
            {
                'role': 'assistant',
                'content': "Почем небо синее? Чему равно '2 + 2'?"
            }
        ],
        stream=False
    )

    session.add(GeneratedAnswerModel(message_id=1, text=response.message))
    await session.commit() 
    

    



