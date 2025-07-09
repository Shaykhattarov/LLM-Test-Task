import os

from faststream.rabbit import RabbitBroker


async def on_startup_callback():
    await rabbit_broker.start()

async def on_shutdown_callback():
    await rabbit_broker.stop()

rabbit_broker = RabbitBroker(
    host=os.getenv("RABBITMQ_HOST"),
    port=int(os.getenv("RABBITMQ_PORT")),
)