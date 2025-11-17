"""
Настройка подключения к базе данных
"""
from databases import Database
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine
from ormar import ModelMeta
from order_service.settings import settings

metadata = MetaData()
database = Database(settings.database_url)


class BaseMeta(ModelMeta):
    """Базовый Meta класс для всех моделей"""
    database = database
    metadata = metadata


async def init_db():
    """Инициализация БД и подключение"""
    engine = create_async_engine(settings.database_url)
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    await engine.dispose()

    if not database.is_connected:
        await database.connect()


async def close_db():
    """Закрытие соединения с БД"""
    if database.is_connected:
        await database.disconnect()

