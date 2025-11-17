"""
Клиент для работы с Kafka
"""
import json
import logging
from datetime import datetime
from typing import Optional
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from processor_service.settings import settings

logger = logging.getLogger(__name__)


class KafkaProducer:
    """Producer для публикации сообщений в Kafka"""
    
    def __init__(self):
        self._producer: Optional[AIOKafkaProducer] = None
    
    async def start(self):
        """Запуск producer"""
        self._producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        await self._producer.start()
        logger.info("Kafka producer started")
    
    async def stop(self):
        """Остановка producer"""
        if self._producer:
            await self._producer.stop()
            logger.info("Kafka producer stopped")
    
    async def publish(self, topic: str, message: dict):
        """
        Публикация сообщения в топик
        
        Args:
            topic: Название топика
            message: Словарь с данными сообщения
        """
        if not self._producer:
            raise RuntimeError("Producer not started")
        
        try:
            await self._producer.send_and_wait(topic, message)
            logger.info(f"Message published to topic {topic}: {message}")
        except Exception as e:
            logger.error(f"Failed to publish message to {topic}: {e}")
            raise

    async def publish_to_dlq(
        self,
        topic: str,
        original_topic: str,
        message: dict,
        error: str,
    ):
        """Публикация сообщения в DLQ"""
        payload = {
            "original_topic": original_topic,
            "error": error,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
        }
        if not self._producer:
            raise RuntimeError("Producer not started")
        try:
            await self._producer.send_and_wait(topic, payload)
            logger.warning(
                "Message routed to DLQ %s due to error: %s", topic, error
            )
        except Exception as dlq_error:
            logger.error(
                "Failed to publish message to DLQ %s: %s", topic, dlq_error
            )


class KafkaConsumer:
    """Consumer для подписки на сообщения из Kafka"""
    
    def __init__(self, topic: str, group_id: str):
        self.topic = topic
        self.group_id = group_id
        self._consumer: Optional[AIOKafkaConsumer] = None
    
    async def start(self):
        """Запуск consumer"""
        self._consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=settings.kafka_bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=True
        )
        await self._consumer.start()
        logger.info(f"Kafka consumer started for topic {self.topic}")
    
    async def stop(self):
        """Остановка consumer"""
        if self._consumer:
            await self._consumer.stop()
            logger.info(f"Kafka consumer stopped for topic {self.topic}")
    
    async def consume(self):
        """Генератор для получения сообщений"""
        if not self._consumer:
            raise RuntimeError("Consumer not started")
        
        async for message in self._consumer:
            yield message.value


# Глобальные экземпляры
kafka_producer = KafkaProducer()

