"""
Тесты для API создания заказов (TDD - первый тест)
"""
import pytest
from httpx import AsyncClient
from order_service.infrastructure.models import Order


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


@pytest.mark.asyncio
async def test_create_order_saved_to_database(client: AsyncClient):
    """
    Тест: Заказ сохраняется в базу данных
    Ожидаемое поведение:
    - После создания заказа через API, он должен быть в БД
    - Все поля должны совпадать
    """
    order_data = {
        "customer_id": "customer_456",
        "items": [
            {"product_id": "prod_3", "quantity": 5}
        ],
        "total_amount": 2500.00
    }
    
    response = await client.post("/orders", json=order_data)
    assert response.status_code == 201
    
    order_id = response.json()["order_id"]
    
    # Проверяем, что заказ есть в БД
    order_from_db = await Order.objects.get(id=order_id)
    
    assert order_from_db.customer_id == "customer_456"
    assert order_from_db.total_amount == 2500.00
    assert order_from_db.status == "created"
    assert len(order_from_db.items) == 1
    assert order_from_db.items[0]["product_id"] == "prod_3"
    assert order_from_db.items[0]["quantity"] == 5


@pytest.mark.asyncio
async def test_get_order_status(client: AsyncClient):
    """
    Тест: Получение статуса заказа через GET endpoint
    Ожидаемое поведение:
    - GET /orders/{order_id} возвращает информацию о заказе
    - Все поля корректны
    """
    # Сначала создаем заказ
    order_data = {
        "customer_id": "customer_789",
        "items": [
            {"product_id": "prod_4", "quantity": 3}
        ],
        "total_amount": 3000.00
    }
    
    create_response = await client.post("/orders", json=order_data)
    assert create_response.status_code == 201
    order_id = create_response.json()["order_id"]
    
    # Получаем статус заказа
    get_response = await client.get(f"/orders/{order_id}")
    assert get_response.status_code == 200
    
    data = get_response.json()
    assert data["order_id"] == order_id
    assert data["customer_id"] == "customer_789"
    assert data["status"] == "created"
    assert data["total_amount"] == 3000.00
    assert len(data["items"]) == 1
    assert data["items"][0]["product_id"] == "prod_4"
    assert data["items"][0]["quantity"] == 3


@pytest.mark.asyncio
async def test_get_order_status_not_found(client: AsyncClient):
    """
    Тест: Получение статуса несуществующего заказа
    Ожидаемое поведение:
    - GET /orders/{non_existent_id} возвращает 404
    """
    response = await client.get("/orders/non-existent-id")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

