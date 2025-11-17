"""
API роуты для Order сервиса
"""
from fastapi import APIRouter
from order_service.domain.models import CreateOrderRequest, OrderResponse
from order_service.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=201)
async def create_order(order_data: CreateOrderRequest):
    """
    Создание нового заказа
    
    Принимает данные заказа и создает его в системе.
    Сохраняет заказ в БД и публикует событие order.created в Kafka.
    """
    return await OrderService.create_order(order_data)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_status(order_id: str):
    """
    Получение статуса заказа по ID
    
    Возвращает информацию о заказе, включая его текущий статус.
    """
    return await OrderService.get_order(order_id)

