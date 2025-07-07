import os
import asyncio
import aio_pika

from api.dependencies import get_session
from distributors.llm_model.distributor import send_prompt_to_llm

from sqlalchemy.ext.asyncio import AsyncSession


async def create_task_to_llm():
    """ Получатель сообщения для отправлки их в LLM """
    while True:
        try:
            connection = await aio_pika.connect_robust(host=os.getenv("RABBITMQ_HOST"), port=os.getenv("RABBITMQ_PORT"), timeout=10)
        except:
            await asyncio.sleep(1)
        else:
            break
    
    async with connection:
        # берем канал
        channel = await connection.channel()

        # берем целевую очередь для принятия сообщений
        queue = await channel.declare_queue('llm_generate_answer', auto_delete=True)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                # обработка поступающих сообщений
                async with message.process():
                    # Получаем сессию БД и сообщение от брокера
                    session: AsyncSession = await get_session()
                    # Обрабатываем сообщение от брокера и передаем его в LLM
                    await send_prompt_to_llm(message, session)