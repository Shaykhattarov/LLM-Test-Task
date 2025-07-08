import os
import json
import logging

from ollama import AsyncClient

# from database.models.generated_answer import GeneratedAnswerModel

# from sqlalchemy.ext.asyncio import AsyncSession



async def send_prompt_to_llm(message: str) -> dict:
    message = json.loads(message)

    client = AsyncClient(
        host=os.getenv("OLLAMA_ENDPOINT")
    )

    response = await client.chat(
        model="llama3.2",
        messages=message,
        stream=False
    )

    return response
        
    

    



