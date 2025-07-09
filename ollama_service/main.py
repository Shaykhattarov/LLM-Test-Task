import os
import json
import logging

from typing import Optional, List
from ollama import AsyncClient
from aiohttp import web

from pydantic import BaseModel
from faststream.rabbit import RabbitBroker



broker = RabbitBroker(
    host=os.getenv("RABBITMQ_HOST"),
    port=int(os.getenv("RABBITMQ_PORT")),
)

async def service_incoming_messages(messages: bytes):
    
    # messages = json.loads(messages)
    new_message = messages[len(messages) - 1]

    ollama_client = AsyncClient(
        host=os.getenv("OLLAMA_ENDPOINT")
    )

    response = await ollama_client.chat(
        model="llama3.2",
        messages=messages,
        stream=False
    )

    response = {
        'message_id': new_message['id'],
        'content': response['message']['content'],
    }
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
