"""
Доменные события для Processor сервиса
"""
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class OrderItemEvent(BaseModel):
    """Элемент заказа в событии"""
    product_id: str
    quantity: int


class OrderCreatedEvent(BaseModel):
    """Событие создания заказа (входящее)"""
    order_id: str = Field(..., description="ID заказа")
    customer_id: str = Field(..., description="ID клиента")
    items: List[OrderItemEvent] = Field(..., description="Список товаров")
    total_amount: float = Field(..., description="Общая сумма заказа")
    created_at: datetime = Field(..., description="Время создания")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class OrderProcessedEvent(BaseModel):
    """Событие обработки заказа (исходящее)"""
    order_id: str = Field(..., description="ID заказа")
    status: str = Field(..., description="Статус обработки (success/failed)")
    error_message: str = Field(default="", description="Сообщение об ошибке, если есть")
    processed_at: datetime = Field(default_factory=datetime.utcnow, description="Время обработки")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

