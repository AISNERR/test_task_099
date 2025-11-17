"""
Тесты для интеграции с Kafka (TDD)
"""
import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
from order_service.domain.events import OrderCreatedEvent


@pytest.mark.asyncio
async def test_create_order_publishes_kafka_event(client: AsyncClient):
    """
    Тест: При создании заказа публикуется событие order.created в Kafka
    Ожидаемое поведение:
    - После создания заказа через API, событие публикуется в Kafka
    - Событие содержит все необходимые данные заказа
    """
    order_data = {
        "customer_id": "customer_kafka_123",
        "items": [
            {"product_id": "prod_kafka_1", "quantity": 2}
        ],
        "total_amount": 1000.00
    }
    
    with patch('order_service.infrastructure.kafka_client.kafka_producer.publish') as mock_publish:
        response = await client.post("/orders", json=order_data)
        
        assert response.status_code == 201
        order_id = response.json()["order_id"]
        
        # Проверяем, что событие было опубликовано
        assert mock_publish.called
        call_args = mock_publish.call_args
        
        # Проверяем топик
        assert call_args[0][0] == "order.created"
        
        # Проверяем содержимое события
        event_data = call_args[0][1]
        assert event_data["order_id"] == order_id
        assert event_data["customer_id"] == "customer_kafka_123"
        assert event_data["total_amount"] == 1000.00
        assert len(event_data["items"]) == 1
        assert event_data["items"][0]["product_id"] == "prod_kafka_1"
        assert event_data["items"][0]["quantity"] == 2
        assert "created_at" in event_data

