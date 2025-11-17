"""
Сервисный слой для работы с заказами
"""
from order_service.domain.models import CreateOrderRequest, OrderResponse, OrderItem
from order_service.domain.events import OrderCreatedEvent, OrderItemEvent, OrderProcessedEvent
from order_service.infrastructure.models import Order
from order_service.infrastructure.kafka_client import kafka_producer
from order_service.settings import settings
import logging

logger = logging.getLogger(__name__)


class OrderService:
    """Сервис для работы с заказами"""
    
    @staticmethod
    async def create_order(order_data: CreateOrderRequest) -> OrderResponse:
        """
        Создание заказа с сохранением в БД и публикацией события
        
        Args:
            order_data: Данные заказа
            
        Returns:
            OrderResponse с информацией о созданном заказе
        """
        # Преобразуем items в список словарей для сохранения в JSON поле
        items_dict = [item.model_dump() for item in order_data.items]
        
        # Создаем заказ в БД
        order = await Order.objects.create(
            customer_id=order_data.customer_id,
            items=items_dict,
            total_amount=order_data.total_amount,
            status="created"
        )
        
        # Публикуем событие order.created в Kafka с retry
        try:
            event = OrderCreatedEvent(
                order_id=order.id,
                customer_id=order.customer_id,
                items=[OrderItemEvent(**item) for item in items_dict],
                total_amount=order.total_amount
            )
            
            from order_service.infrastructure.retry import retry_async
            await retry_async(
                kafka_producer.publish,
                max_attempts=3,
                delay=1.0,
                backoff=2.0,
                exceptions=(Exception,),
                topic=settings.order_created_topic,
                message=event.model_dump()
            )
            logger.info(f"Order created event published for order {order.id}")
        except Exception as e:
            # Логируем ошибку, но не прерываем создание заказа
            # В продакшене можно добавить dead letter queue
            logger.error(f"Failed to publish order.created event after retries: {e}")
        
        return OrderResponse(
            order_id=order.id,
            customer_id=order.customer_id,
            items=order_data.items,  # Возвращаем оригинальные Pydantic модели
            total_amount=order.total_amount,
            status=order.status
        )
    
    @staticmethod
    async def get_order(order_id: str) -> OrderResponse:
        """
        Получение заказа по ID
        
        Args:
            order_id: ID заказа
            
        Returns:
            OrderResponse с информацией о заказе
            
        Raises:
            OrderNotFoundError: Если заказ не найден
        """
        try:
            order = await Order.objects.get(id=order_id)
        except Exception as e:
            from order_service.api.exceptions import OrderNotFoundError
            logger.debug(f"Order {order_id} not found: {e}")
            raise OrderNotFoundError(order_id)
        
        # Преобразуем items из JSON обратно в Pydantic модели
        items = [OrderItem(**item) for item in order.items]
        
        return OrderResponse(
            order_id=order.id,
            customer_id=order.customer_id,
            items=items,
            total_amount=order.total_amount,
            status=order.status
        )
    
    @staticmethod
    async def update_order_status(event: OrderProcessedEvent):
        """
        Обновление статуса заказа на основе события обработки
        
        Args:
            event: Событие обработки заказа
        """
        try:
            order = await Order.objects.get(id=event.order_id)
            
            # Обновляем статус заказа
            if event.status == "success":
                order.status = "processed"
            elif event.status == "failed":
                order.status = "failed"
            
            await order.update()
            logger.info(f"Order {event.order_id} status updated to {order.status}")
            
        except Exception as e:
            logger.error(f"Failed to update order status for {event.order_id}: {e}")
            # В продакшене можно добавить retry или dead letter queue

