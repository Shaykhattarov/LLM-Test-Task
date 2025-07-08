import json
import logging
import aio_pika

from abc import ABC
from aio_pika import ExchangeType, Message, DeliveryMode



class AbstractRabbitMQClient(ABC):

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
            port=int(self.port)
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


    

