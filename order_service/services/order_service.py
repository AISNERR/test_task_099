"""
Сервисный слой для работы с заказами
"""
from order_service.domain.models import CreateOrderRequest, OrderResponse, OrderItem
from order_service.domain.events import OrderCreatedEvent, OrderItemEvent
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
        
        # Публикуем событие order.created в Kafka
        try:
            event = OrderCreatedEvent(
                order_id=order.id,
                customer_id=order.customer_id,
                items=[OrderItemEvent(**item) for item in items_dict],
                total_amount=order.total_amount
            )
            
            await kafka_producer.publish(
                topic=settings.order_created_topic,
                message=event.model_dump()
            )
            logger.info(f"Order created event published for order {order.id}")
        except Exception as e:
            # Логируем ошибку, но не прерываем создание заказа
            # В продакшене можно добавить retry механизм или dead letter queue
            logger.error(f"Failed to publish order.created event: {e}")
        
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
            HTTPException: Если заказ не найден
        """
        try:
            order = await Order.objects.get(id=order_id)
        except Exception:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Преобразуем items из JSON обратно в Pydantic модели
        items = [OrderItem(**item) for item in order.items]
        
        return OrderResponse(
            order_id=order.id,
            customer_id=order.customer_id,
            items=items,
            total_amount=order.total_amount,
            status=order.status
        )

