"""
API роуты для Order сервиса
"""
from fastapi import APIRouter, HTTPException
from order_service.domain.models import CreateOrderRequest, OrderResponse
import uuid

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=201)
async def create_order(order_data: CreateOrderRequest):
    """
    Создание нового заказа
    
    Принимает данные заказа и создает его в системе.
    """
    # Временная реализация для прохождения теста
    # Позже будет добавлена работа с БД и брокером сообщений
    order_id = str(uuid.uuid4())
    
    return OrderResponse(
        order_id=order_id,
        customer_id=order_data.customer_id,
        items=order_data.items,
        total_amount=order_data.total_amount,
        status="created"
    )

