"""
Настройка подключения к базе данных
"""
from sqlalchemy import MetaData
from processor_service.settings import settings

# Создаем metadata для ormar
metadata = MetaData()

# Базовый Meta для ormar моделей
class BaseMeta:
    """Базовый Meta класс для всех моделей"""
    database = settings.database_url
    metadata = metadata


async def init_db():
    """Инициализация БД - создание таблиц"""
    from processor_service.infrastructure.models import OrderProcessing
    from sqlalchemy.ext.asyncio import create_async_engine
    
    engine = create_async_engine(settings.database_url)
    
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    
    await engine.dispose()


async def close_db():
    """Закрытие соединений с БД"""
    # Ormar управляет соединениями автоматически
    pass

