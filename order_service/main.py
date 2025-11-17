"""
Order Service - главный файл приложения
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from order_service.api.routes import router
from order_service.infrastructure.database import init_db, close_db
from order_service.infrastructure.kafka_client import kafka_producer
from order_service.consumers.order_processed_consumer import order_processed_consumer


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Инициализация при старте
    await init_db()
    await kafka_producer.start()
    await order_processed_consumer.start()
    yield
    # Очистка при остановке
    await order_processed_consumer.stop()
    await kafka_producer.stop()
    await close_db()


app = FastAPI(
    title="Order Service",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "order_service"}

