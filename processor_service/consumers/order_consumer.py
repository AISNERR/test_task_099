"""
Consumer для обработки событий order.created из Kafka
"""
import asyncio
import logging
from processor_service.infrastructure.kafka_client import KafkaConsumer
from processor_service.domain.events import OrderCreatedEvent
from processor_service.services.processor_service import ProcessorService
from processor_service.settings import settings

logger = logging.getLogger(__name__)


class OrderCreatedConsumer:
    """Consumer для обработки событий создания заказов"""
    
    def __init__(self):
        self.consumer = KafkaConsumer(
            topic=settings.order_created_topic,
            group_id="processor_service_group"
        )
        self._running = False
    
    async def start(self):
        """Запуск consumer"""
        await self.consumer.start()
        self._running = True
        logger.info("Order created consumer started")
        
        # Запускаем обработку в фоновой задаче
        asyncio.create_task(self._consume_loop())
    
    async def stop(self):
        """Остановка consumer"""
        self._running = False
        await self.consumer.stop()
        logger.info("Order created consumer stopped")
    
    async def _consume_loop(self):
        """Основной цикл обработки сообщений"""
        try:
            async for message in self.consumer.consume():
                if not self._running:
                    break
                
                try:
                    # Парсим событие
                    event = OrderCreatedEvent(**message)
                    logger.info(f"Received order.created event for order {event.order_id}")
                    
                    # Обрабатываем заказ с retry
                    from processor_service.infrastructure.retry import retry_async
                    await retry_async(
                        ProcessorService.process_order,
                        max_attempts=3,
                        delay=1.0,
                        backoff=2.0,
                        exceptions=(Exception,),
                        event=event
                    )
                    
                except Exception as e:
                    logger.error(f"Error processing order.created event after retries: {e}", exc_info=True)
                    # В продакшене здесь можно добавить dead letter queue
                    
        except Exception as e:
            logger.error(f"Error in consume loop: {e}", exc_info=True)


# Глобальный экземпляр
order_created_consumer = OrderCreatedConsumer()

