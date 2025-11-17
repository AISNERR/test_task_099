"""
Доменные модели для Order сервиса
"""
from typing import List
from pydantic import BaseModel, Field, conlist


class OrderItem(BaseModel):
    """Элемент заказа"""
    product_id: str = Field(..., description="ID товара")
    quantity: int = Field(..., gt=0, description="Количество")


class CreateOrderRequest(BaseModel):
    """Запрос на создание заказа"""
    customer_id: str = Field(..., description="ID клиента")
    items: conlist(OrderItem, min_items=1) = Field(..., description="Список товаров")
    total_amount: float = Field(..., gt=0, description="Общая сумма заказа")


class OrderResponse(BaseModel):
    """Ответ с информацией о заказе"""
    order_id: str = Field(..., description="ID заказа")
    customer_id: str = Field(..., description="ID клиента")
    items: List[OrderItem] = Field(..., description="Список товаров")
    total_amount: float = Field(..., description="Общая сумма")
    status: str = Field(..., description="Статус заказа")

