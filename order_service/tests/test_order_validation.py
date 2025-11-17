"""
Тесты валидации данных для Order API
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_order_validation_missing_fields(client: AsyncClient):
    """
    Тест: Валидация - отсутствие обязательных полей
    """
    # Отсутствует customer_id
    order_data = {
        "items": [{"product_id": "prod_1", "quantity": 1}],
        "total_amount": 100.0
    }
    response = await client.post("/orders", json=order_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_order_validation_empty_items(client: AsyncClient):
    """
    Тест: Валидация - пустой список товаров
    """
    order_data = {
        "customer_id": "customer_123",
        "items": [],
        "total_amount": 100.0
    }
    response = await client.post("/orders", json=order_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_order_validation_negative_quantity(client: AsyncClient):
    """
    Тест: Валидация - отрицательное количество товара
    """
    order_data = {
        "customer_id": "customer_123",
        "items": [{"product_id": "prod_1", "quantity": -1}],
        "total_amount": 100.0
    }
    response = await client.post("/orders", json=order_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_order_validation_zero_total_amount(client: AsyncClient):
    """
    Тест: Валидация - нулевая или отрицательная сумма
    """
    order_data = {
        "customer_id": "customer_123",
        "items": [{"product_id": "prod_1", "quantity": 1}],
        "total_amount": 0
    }
    response = await client.post("/orders", json=order_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_order_validation_missing_product_id(client: AsyncClient):
    """
    Тест: Валидация - отсутствие product_id в элементе заказа
    """
    order_data = {
        "customer_id": "customer_123",
        "items": [{"quantity": 1}],
        "total_amount": 100.0
    }
    response = await client.post("/orders", json=order_data)
    assert response.status_code == 422

