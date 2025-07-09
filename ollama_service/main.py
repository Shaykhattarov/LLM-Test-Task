import os
import json
import logging

from typing import Optional, List
from ollama import AsyncClient
from aiohttp import web

from pydantic import BaseModel
from faststream import Context
from faststream.rabbit import RabbitBroker



broker = RabbitBroker(
    host=os.getenv("RABBITMQ_HOST"),
    port=int(os.getenv("RABBITMQ_PORT")),
)

async def service_incoming_messages(messages: list):
    
    # messages = json.loads(messages)
    new_message = messages[len(messages) - 1]
    logging.info(messages)
    model_messages = []
    for message in messages:
        logging.info(f"role: {message['role']}\ncontent: {message['content']}")
        model_messages.append(
            {
                'role': message['role'],
                'content': message['content']
            }
        )

    ollama_client = AsyncClient(
        host=os.getenv("OLLAMA_ENDPOINT")
    )
    
    try:

        response = await ollama_client.chat(
            model="llama3.2",
            messages=model_messages,
            stream=False
        )
    except Exception as err:
        logging.exception(err)
        response = {
            'status': '500',
            'message_id': new_message['id'],
            'content': '',
        }
        await broker.publish(response, "backend_messages")
    else:
        response = {
            'status': '200',
            'message_id': new_message['id'],
            'content': response['message']['content'],
        }
        logging.info(f"status: {response['status']}\ncontent: {response['message_id']}\ncontent: {response['content']}")
    # await broker.connect()
    # logging.info("[INFO] Response: " + response)
        await broker.publish(response, "backend_messages")
    


@broker.subscriber("model_messages")
async def incoming_messages(messages: list):
    # logging.info(messages)
    await service_incoming_messages(messages)

async def start_broker(app):
    await broker.start()

async def stop_broker(app):
    await broker.stop()


app = web.Application()
app.add_routes([

])

app.on_startup.append(start_broker)
app.on_cleanup.append(stop_broker)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,filename="logs.logs",filemode='a')
    web.run_app(app)
