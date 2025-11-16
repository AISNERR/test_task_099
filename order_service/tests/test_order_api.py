"""
Тесты для API создания заказов (TDD - первый тест)
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_order_success(client: AsyncClient):
    """
    Тест: Создание заказа через HTTP API
    Ожидаемое поведение:
    - POST /orders возвращает 201
    - В ответе есть order_id
    - Статус заказа = "created"
    """
    order_data = {
        "customer_id": "customer_123",
        "items": [
            {"product_id": "prod_1", "quantity": 2},
            {"product_id": "prod_2", "quantity": 1}
        ],
        "total_amount": 1500.50
    }
    
    response = await client.post("/orders", json=order_data)
    
    assert response.status_code == 201
    data = response.json()
    assert "order_id" in data
    assert data["status"] == "created"
    assert data["customer_id"] == "customer_123"
    assert len(data["items"]) == 2

