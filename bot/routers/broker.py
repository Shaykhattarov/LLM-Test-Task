from core.config import rabbit_broker
from main import bot


@rabbit_broker.subscriber("tgfrontend_messages")
async def receive_backend_messages(message: dict):
    print(message)
    await bot.send_message(
        chat_id=message['chat_id'],
        text=message['content']
    )