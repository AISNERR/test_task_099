import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
from order_service.main import app
from order_service.infrastructure.database import metadata
from sqlalchemy.ext.asyncio import create_async_engine
from order_service.settings import settings


@pytest_asyncio.fixture(scope="function")
async def test_db():
    """Фикстура для тестовой БД - создает и удаляет таблицы для каждого теста"""
    # Используем тестовую БД
    if "test_order_db" in settings.database_url:
        test_db_url = settings.database_url
    else:
        test_db_url = settings.database_url.replace("/order_db", "/test_order_db")
    engine = create_async_engine(test_db_url)
    
    # Создаем таблицы
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    # Подключаем базу через databases, если она не подключена
    from order_service.infrastructure.database import database
    if not database.is_connected:
        await database.connect()
    
    yield
    
    # Удаляем таблицы после теста
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
    
    await engine.dispose()
    if database.is_connected:
        await database.disconnect()


@pytest.fixture
def mock_kafka_producer():
    """Фикстура для мокирования Kafka producer"""
    with patch('order_service.infrastructure.kafka_client.kafka_producer') as mock:
        mock.start = AsyncMock(return_value=None)
        mock.stop = AsyncMock(return_value=None)
        mock.publish = AsyncMock(return_value=None)
        mock.publish_to_dlq = AsyncMock(return_value=None)
        mock._producer = object()
        yield mock


@pytest_asyncio.fixture
async def client(test_db, mock_kafka_producer):
    """Фикстура для тестового клиента"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

