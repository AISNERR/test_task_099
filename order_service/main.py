"""
Order Service - главный файл приложения
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from order_service.api.routes import router
from order_service.infrastructure.database import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Инициализация при старте
    await init_db()
    yield
    # Очистка при остановке
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

