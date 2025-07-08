import os
import aio_pika

from typing import Any

from fastapi.encoders import jsonable_encoder


class RabbitClient:
        
        def __init__(self, queue_name: str):
            self.queue_name = queue_name
            
        async def publish_messages(self, message: bytes):
            connection = await aio_pika.connect_robust(
                host=os.getenv("RABBITMQ_HOST"), port=int(os.getenv("RABBITMQ_PORT")), timeout=10
            )
            async with connection:         
                channel = await connection.channel()
                queue = await channel.declare_queue(self.queue_name)
                await channel.default_exchange.publish(
                    message=aio_pika.Message(
                        body=message
                    ),
                    routing_key=queue.name,
                )

