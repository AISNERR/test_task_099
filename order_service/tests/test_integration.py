"""
Интеграционные тесты для Order Service
"""
import pytest
from httpx import AsyncClient
from order_service.infrastructure.models import Order
from unittest.mock import patch


@pytest.mark.asyncio
async def test_full_order_flow(client: AsyncClient):
    """
    Тест: Полный цикл работы с заказом
    - Создание заказа
    - Публикация события в Kafka
    - Получение статуса заказа
    """
    order_data = {
        "customer_id": "customer_integration_123",
        "items": [
            {"product_id": "prod_integration_1", "quantity": 2},
            {"product_id": "prod_integration_2", "quantity": 1}
        ],
        "total_amount": 2000.00
    }
    
    from order_service.services import order_service as service_module
    with patch('order_service.services.order_service.kafka_producer.publish', return_value=None) as mock_publish:
        service_module.kafka_producer._producer = object()
        # Создаем заказ
        create_response = await client.post("/orders", json=order_data)
        assert create_response.status_code == 201
        
        order_id = create_response.json()["order_id"]
        
        # Проверяем публикацию события
        assert mock_publish.called
        call_args = mock_publish.call_args
        assert call_args.kwargs["topic"] == "order.created"
        event_data = call_args.kwargs["message"]
        assert event_data["order_id"] == order_id
        
        # Получаем статус заказа
        get_response = await client.get(f"/orders/{order_id}")
        assert get_response.status_code == 200
        
        data = get_response.json()
        assert data["order_id"] == order_id
        assert data["status"] == "created"
        assert data["customer_id"] == "customer_integration_123"
        service_module.kafka_producer._producer = None


@pytest.mark.asyncio
async def test_order_status_after_processing(client: AsyncClient):
    """
    Тест: Обновление статуса заказа после обработки
    Симулируем получение события order.processed
    """
    # Создаем заказ
    order_data = {
        "customer_id": "customer_status_test",
        "items": [{"product_id": "prod_status", "quantity": 1}],
        "total_amount": 500.00
    }
    
    create_response = await client.post("/orders", json=order_data)
    assert create_response.status_code == 201
    order_id = create_response.json()["order_id"]
    
    # Симулируем обновление статуса через событие
    from order_service.domain.events import OrderProcessedEvent
    from order_service.services.order_service import OrderService
    
    processed_event = OrderProcessedEvent(
        order_id=order_id,
        status="success",
        error_message="",
    )
    
    await OrderService.update_order_status(processed_event)
    
    # Проверяем обновленный статус
    get_response = await client.get(f"/orders/{order_id}")
    assert get_response.status_code == 200
    assert get_response.json()["status"] == "processed"

