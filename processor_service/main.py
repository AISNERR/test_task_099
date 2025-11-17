"""
Processor Service - главный файл приложения
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from processor_service.infrastructure.database import init_db, close_db
from processor_service.infrastructure.kafka_client import kafka_producer
from processor_service.consumers.order_consumer import order_created_consumer


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Инициализация при старте
    await init_db()
    await kafka_producer.start()
    await order_created_consumer.start()
    yield
    # Очистка при остановке
    await order_created_consumer.stop()
    await kafka_producer.stop()
    await close_db()


app = FastAPI(
    title="Processor Service",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "processor_service"}

