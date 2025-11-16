import pytest
from httpx import AsyncClient
from order_service.main import app


@pytest.fixture
async def client():
    """Фикстура для тестового клиента"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

