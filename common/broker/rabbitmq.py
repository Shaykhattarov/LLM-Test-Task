import json
import uuid
import asyncio
import logging
import aio_pika

from aio_pika import ExchangeType, Message, DeliveryMode
from aio_pika.abc import AbstractIncomingMessage


class RabbitMQClient:

    def __init__(self, host: str, port: int, publish_queue: str, consume_queue: str):
        self.host = host
        self.port = port
        self.publish_queue_name = publish_queue
        self.consume_queue_name = consume_queue


    async def connect(self):
        self.connection = await aio_pika.connect_robust(
            host=self.host,
            port=self.port
        )

        self.channel = await self.connection.channel()

        self.publish_queue = await self.channel.declare_queue(
            self.publish_queue_name, durable=True
        )

        self.consume_queue = await self.channel.declare_queue(
            self.consume_queue_name, durable=True
        )

    async def disconnect(self):
        if self.connection:
            await self.connection.close()

    async def publish(self, message: dict|list):
        if not self.channel: await self.connect()

        message = json.dumps(message).encode('utf-8')

        await self.channel.default_exchange.publish(
            message=Message(body=message, delivery_mode=DeliveryMode.PERSISTENT),
            routing_key=self.publish_queue_name
        )

    async def consume(self, callback: callable, prefetch_count=10):
        if not self.consume_queue:
            logging.exception("Соединение не установлено. Вызовите connect()")
            raise RuntimeError("Очередь не объявлена. Вызовите connect()")

        # Ограничиваем количество неподтвержденных сообщений
        await self.channel.set_qos(prefetch_count=prefetch_count)

        # Запускаем бесконечный цикл потребления
        async with self.consume_queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    # Вызываем callback с данными сообщения
                    await callback(message.body)

        


class RabbitMQClient1:

    def __init__(self, host: str, port: int, process_callable, publish_queue_name, consume_queue_name):
        self.host, self.port = host, int(port)
        self.publish_queue_name = publish_queue_name
        self.consume_queue_name = consume_queue_name
        self.process_callable = process_callable
        
        self.connection = None  # Будет установлено асинхронно
        self.channel = None     # Будет установлено асинхронно
        self.publish_queue = None
        self.consume_queue = None

    async def connect(self) -> None:
        """Установка асинхронного соединения для публикации сообщений"""
        self.connection = await aio_pika.connect_robust(
            host=self.host,
            port=self.port,
        )
        self.channel = await self.connection.channel()

        # Объявляем durable очереди для публикации и потребления
        self.publish_queue = await self.channel.declare_queue(
            self.publish_queue_name, durable=True
        )

    async def consume(self, loop: asyncio.AbstractEventLoop) -> aio_pika.connection.Connection:
        """Настройка потребителя сообщений"""
        # Создаем отдельное соединение для потребителя
        connection = await aio_pika.connect_robust(
            host=self.host,
            port=self.port,
            loop=loop
        )
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=5)
    
        queue = await channel.declare_queue(
            self.consume_queue_name, durable=True
        )
        await queue.consume(self.process_incoming_message)
        return connection

    async def process_incoming_message(
        self, message: AbstractIncomingMessage
    ) -> None:
        """Обработка входящего сообщения"""
        async with message.process():
            body = message.body.decode()
            # print(f'Received message: {body}')
            if body:
                await self.process_callable(json.loads(body))

    async def publish(self, message: dict|list) -> None:
        """Асинхронная публикация сообщения"""
        if not self.connection:
            await self.connect()
            
        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(message).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                correlation_id=str(uuid.uuid4()),
                reply_to=self.publish_queue_name,
            ),
            routing_key=self.publish_queue_name,
        )


class RabbitMQClient2:

    def __init__(self, host: str, port: int, queue_name: str):
        self.host = host
        self.port = port
        self.queue_name = queue_name
        self.connection = None
        self.channel = None
        self.queue = None
        self.exchange = None

    async def connect(self):
        """Установка соединения и создание очереди"""
        self.connection = await aio_pika.connect_robust(
            host=self.host,
            port=int(self.port),
            loop=self.loop
        )
        self.channel = await self.connection.channel()
        
        # Объявляем очередь с параметрами
        self.queue = await self.channel.declare_queue(
            self.queue_name,
            durable=True,  # Сохранять сообщения при перезапуске RabbitMQ
            auto_delete=False
        )
        
        # Создаем exchange (если нужна маршрутизация)
        self.exchange = await self.channel.declare_exchange(
            "direct_exchange",
            ExchangeType.DIRECT,
            durable=True
        )

        await self.queue.bind(self.exchange, routing_key=self.queue_name)

    async def disconnect(self):
        """Закрытие соединения"""
        if self.connection:
            await self.connection.close()

    async def publish(self, message: dict):
        """Отправка сообщения в очередь"""
        if not self.channel:
            logging.exception("Соединение не установлено. Вызовите connect()")
            raise RuntimeError("Соединение не установлено. Вызовите connect()")
        
        # Сериализуем сообщение в JSON
        body = json.dumps(message).encode('utf-8')
        
        # Создаем сообщение с настройкой persistent-режима
        message = Message(
            body,
            delivery_mode=DeliveryMode.PERSISTENT  # Гарантирует сохранение при перезагрузке
        )
        
        # Публикуем через exchange с routing_key = имени очереди
        await self.exchange.publish(
            message=message,
            routing_key=self.queue_name
        )

    async def consume(self, callback: callable, prefetch_count: int = 10):
        """Слушаем очередь и обрабатываем сообщения callback-функцией"""
        if not self.queue:
            logging.exception("Соединение не установлено. Вызовите connect()")
            raise RuntimeError("Очередь не объявлена. Вызовите connect()")
        
        # Ограничиваем количество неподтвержденных сообщений
        await self.channel.set_qos(prefetch_count=prefetch_count)
        
        # Запускаем бесконечный цикл потребления
        async with self.queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    # Вызываем callback с данными сообщения
                    await callback(message.body)


    

