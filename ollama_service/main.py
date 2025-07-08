import os
import json
import aio_pika

import logging
import asyncio

from aio_pika import DeliveryMode
from aio_pika.message import Message
from aio_pika.exchange import ExchangeType

from consumer import create_task_to_llm

        

if __name__ == "__main__":
    print("Start")
    logging.basicConfig(
        level=logging.INFO,
        filename="logs.logs",
        filemode='a'
    )
    asyncio.run(create_task_to_llm())