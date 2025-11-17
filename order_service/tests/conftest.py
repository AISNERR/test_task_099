import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
from order_service.main import app
from order_service.infrastructure.database import init_db, close_db, metadata
from sqlalchemy.ext.asyncio import create_async_engine
from order_service.settings import settings


@pytest.fixture(scope="function")
async def test_db():
    """Фикстура для тестовой БД - создает и удаляет таблицы для каждого теста"""
    # Используем тестовую БД
    test_db_url = settings.database_url.replace("/order_db", "/test_order_db")
    engine = create_async_engine(test_db_url)
    
    # Создаем таблицы
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    
    yield
    
    # Удаляем таблицы после теста
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
def mock_kafka_producer():
    """Фикстура для мокирования Kafka producer"""
    with patch('order_service.infrastructure.kafka_client.kafka_producer') as mock:
        mock.start = AsyncMock()
        mock.stop = AsyncMock()
        mock.publish = AsyncMock()
        yield mock


@pytest.fixture
async def client(test_db, mock_kafka_producer):
    """Фикстура для тестового клиента"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

