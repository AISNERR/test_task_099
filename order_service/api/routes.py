"""
API роуты для Order сервиса
"""
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from order_service.domain.models import CreateOrderRequest, OrderResponse
from order_service.services.order_service import OrderService
from order_service.api.exceptions import OrderNotFoundError, OrderValidationError
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=201)
async def create_order(order_data: CreateOrderRequest):
    """
    Создание нового заказа
    
    Принимает данные заказа и создает его в системе.
    Сохраняет заказ в БД и публикует событие order.created в Kafka.
    """
    try:
        # Валидация данных
        if not order_data.items:
            raise OrderValidationError("Order must contain at least one item")
        
        if order_data.total_amount <= 0:
            raise OrderValidationError("Total amount must be greater than 0")
        
        return await OrderService.create_order(order_data)
    
    except OrderValidationError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating order: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while creating order"
        )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_status(order_id: str):
    """
    Получение статуса заказа по ID
    
    Возвращает информацию о заказе, включая его текущий статус.
    """
    try:
        return await OrderService.get_order(order_id)
    except OrderNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting order {order_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving order"
        )


