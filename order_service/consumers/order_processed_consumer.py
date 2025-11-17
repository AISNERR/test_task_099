"""
Consumer для обработки событий order.processed из Kafka
"""
import asyncio
import logging
from order_service.infrastructure.kafka_client import KafkaConsumer
from order_service.domain.events import OrderProcessedEvent
from order_service.services.order_service import OrderService
from order_service.settings import settings

logger = logging.getLogger(__name__)


class OrderProcessedConsumer:
    """Consumer для обработки событий обработки заказов"""
    
    def __init__(self):
        self.consumer = KafkaConsumer(
            topic=settings.order_processed_topic,
            group_id="order_service_group"
        )
        self._running = False
    
    async def start(self):
        """Запуск consumer"""
        await self.consumer.start()
        self._running = True
        logger.info("Order processed consumer started")
        
        # Запускаем обработку в фоновой задаче
        asyncio.create_task(self._consume_loop())
    
    async def stop(self):
        """Остановка consumer"""
        self._running = False
        await self.consumer.stop()
        logger.info("Order processed consumer stopped")
    
    async def _consume_loop(self):
        """Основной цикл обработки сообщений"""
        try:
            async for message in self.consumer.consume():
                if not self._running:
                    break
                
                try:
                    # Парсим событие
                    event = OrderProcessedEvent(**message)
                    logger.info(f"Received order.processed event for order {event.order_id}")
                    
                    # Обновляем статус заказа с retry
                    from order_service.infrastructure.retry import retry_async
                    await retry_async(
                        OrderService.update_order_status,
                        max_attempts=3,
                        delay=1.0,
                        backoff=2.0,
                        exceptions=(Exception,),
                        event=event
                    )
                    
                except Exception as e:
                    logger.error(f"Error processing order.processed event after retries: {e}", exc_info=True)
                    # В продакшене здесь можно добавить dead letter queue
                    
        except Exception as e:
            logger.error(f"Error in consume loop: {e}", exc_info=True)


# Глобальный экземпляр
order_processed_consumer = OrderProcessedConsumer()

