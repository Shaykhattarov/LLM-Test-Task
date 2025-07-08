import os
import logging
import asyncio
import aio_pika

# from api.dependencies import get_session
from distributor import send_prompt_to_llm

# from sqlalchemy.ext.asyncio import AsyncSession


async def create_task_to_llm():
    """ Получатель сообщения для отправлки их в LLM """
    while True:
        try:
            connection = await aio_pika.connect_robust(host=os.getenv("RABBITMQ_HOST"), port=int(os.getenv("RABBITMQ_PORT")), timeout=10)
        except:
            await asyncio.sleep(1)
        else:
            break
    logging.info("Connection is create")
    async with connection:
        # берем канал
        channel = await connection.channel()

        # берем целевую очередь для принятия сообщений
        queue = await channel.declare_queue('llm_generate_answer', auto_delete=False)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                # обработка поступающих сообщений
                async with message.process():
                    response: dict = await send_prompt_to_llm(message.body.decode('utf-8'))
                    logging.info("Ответ: " + response['message']['content'])
    