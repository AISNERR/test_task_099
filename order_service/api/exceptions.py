"""
Кастомные исключения для Order Service
"""
from fastapi import HTTPException, status


class OrderNotFoundError(HTTPException):
    """Исключение для случая, когда заказ не найден"""
    
    def __init__(self, order_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} not found"
        )
        self.order_id = order_id


class OrderValidationError(HTTPException):
    """Исключение для ошибок валидации заказа"""
    
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order validation failed: {message}"
        )


class KafkaPublishError(Exception):
    """Исключение для ошибок публикации в Kafka"""
    
    def __init__(self, topic: str, message: str = ""):
        self.topic = topic
        self.message = message
        super().__init__(f"Failed to publish message to topic {topic}: {message}")
