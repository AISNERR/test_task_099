"""
Сервисный слой для обработки заказов
"""
import random
import logging
from datetime import datetime
from processor_service.domain.events import OrderCreatedEvent, OrderProcessedEvent
from processor_service.infrastructure.models import OrderProcessing
from processor_service.infrastructure.kafka_client import kafka_producer
from processor_service.settings import settings

logger = logging.getLogger(__name__)


class ProcessorService:
    """Сервис для обработки заказов"""
    
    @staticmethod
    async def process_order(event: OrderCreatedEvent) -> OrderProcessedEvent:
        """
        Обработка заказа
        
        Args:
            event: Событие создания заказа
            
        Returns:
            OrderProcessedEvent с результатом обработки
        """
        # Сохраняем заказ в БД для отслеживания состояния
        items_dict = [item.model_dump() for item in event.items]
        
        # Проверяем, не обрабатывался ли уже этот заказ (идемпотентность)
        try:
            existing = await OrderProcessing.objects.get(order_id=event.order_id)
            logger.info(f"Order {event.order_id} already processed, returning existing result")
            return OrderProcessedEvent(
                order_id=existing.order_id,
                status=existing.status,
                error_message=existing.error_message or "",
                processed_at=existing.processed_at or datetime.utcnow()
            )
        except Exception:
            # Заказ не найден, продолжаем обработку
            pass
        
        # Создаем запись о начале обработки
        processing = await OrderProcessing.objects.create(
            order_id=event.order_id,
            customer_id=event.customer_id,
            items=items_dict,
            total_amount=event.total_amount,
            status="processing"
        )
        
        # Симуляция обработки (может быть успешной или неудачной)
        # В реальной системе здесь была бы бизнес-логика валидации
        success = random.random() > 0.2  # 80% успешных обработок
        
        if success:
            status = "success"
            error_message = ""
            logger.info(f"Order {event.order_id} processed successfully")
        else:
            status = "failed"
            error_message = "Order validation failed"
            logger.warning(f"Order {event.order_id} processing failed: {error_message}")
        
        # Обновляем статус в БД
        processing.status = status
        processing.error_message = error_message if not success else None
        processing.processed_at = datetime.utcnow()
        await processing.update()
        
        # Создаем событие обработки
        processed_event = OrderProcessedEvent(
            order_id=event.order_id,
            status=status,
            error_message=error_message,
            processed_at=datetime.utcnow()
        )
        
        # Публикуем событие order.processed в Kafka
        try:
            await kafka_producer.publish(
                topic=settings.order_processed_topic,
                message=processed_event.model_dump()
            )
            logger.info(f"Order processed event published for order {event.order_id}")
        except Exception as e:
            logger.error(f"Failed to publish order.processed event: {e}")
            # В продакшене можно добавить retry механизм
        
        return processed_event

