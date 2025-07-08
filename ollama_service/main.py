import os
import json
import logging
import asyncio

from ollama import AsyncClient

from common.broker.rabbitmq import RabbitMQClient
from common.database.engine import engine, sessionmaker
from common.database.models.generated_answer import GeneratedAnswerModel    


async def send_message_to_llm(body: bytes):
    
    messages: list = json.loads(body.decode('utf-8'))
    client = AsyncClient(
        host=os.getenv("OLLAMA_ENDPOINT")
    )
    response = client.chat(
        model='llama3.2',
        messages=messages,
        stream=False,
    )
    answer = GeneratedAnswerModel(
        message_id=messages[len(messages) - 1]['message_id'],
        text=response['message']['content'],
    )

    async with sessionmaker() as session:
        try:
            session.add(answer)
            await session.commit()
        except Exception as err:
            logging.exception(f"Ошибка с сохранением ответа от LLM: {err}")
            await session.rollback()
        else:
            await session.refresh(answer)
            logging.info(
                f"Ответ на Message(id={messages[len(messages) - 1]['message_id']}) " + \
                f"успешно сохранен в БД GeneratedAnswer(id={answer.id})"
            )


async def main():
    rabbit = RabbitMQClient(
        host=os.getenv("RABBITMQ_HOST"),
        port=os.getenv('RABBITMQ_PORT'),
        queue_name="llm_generate_answer",
    )

    await rabbit.connect() # Создаем соединение с RabbitMQ
    await rabbit.consume(send_message_to_llm) # Начинаем слушать очередь
    


if __name__ == "__main__":
    print("Start")
    logging.basicConfig(
        level=logging.INFO,
        filename="logs.logs",
        filemode='a'
    )
    asyncio.run(main())