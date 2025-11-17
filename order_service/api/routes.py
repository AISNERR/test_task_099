"""
API роуты для Order сервиса
"""
from fastapi import APIRouter, HTTPException
from order_service.domain.models import CreateOrderRequest, OrderResponse, OrderItem
from order_service.infrastructure.models import Order

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=201)
async def create_order(order_data: CreateOrderRequest):
    """
    Создание нового заказа
    
    Принимает данные заказа и создает его в системе.
    Сохраняет заказ в БД.
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
    
    return OrderResponse(
        order_id=order.id,
        customer_id=order.customer_id,
        items=order_data.items,  # Возвращаем оригинальные Pydantic модели
        total_amount=order.total_amount,
        status=order.status
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_status(order_id: str):
    """
    Получение статуса заказа по ID
    
    Возвращает информацию о заказе, включая его текущий статус.
    """
    try:
        order = await Order.objects.get(id=order_id)
    except Exception:
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

