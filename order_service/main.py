"""
Order Service - главный файл приложения
"""
from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from order_service.api.routes import router
from order_service.infrastructure.database import init_db, close_db
from order_service.infrastructure.kafka_client import kafka_producer
from order_service.consumers.order_processed_consumer import order_processed_consumer

# Настройка логирования
from order_service.infrastructure.logging_config import setup_logging
from order_service.settings import settings

setup_logging(level="DEBUG" if settings.debug else "INFO", structured=False)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Инициализация при старте
    logger.info("Starting Order Service...")
    try:
        await init_db()
        logger.info("Database initialized")
        
        await kafka_producer.start()
        logger.info("Kafka producer started")
        
        await order_processed_consumer.start()
        logger.info("Kafka consumer started")
        
        logger.info("Order Service started successfully")
    except Exception as e:
        logger.error(f"Failed to start Order Service: {e}", exc_info=True)
        raise
    
    yield
    
    # Очистка при остановке
    logger.info("Shutting down Order Service...")
    try:
        await order_processed_consumer.stop()
        await kafka_producer.stop()
        await close_db()
        logger.info("Order Service stopped successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}", exc_info=True)


app = FastAPI(
    title="Order Service",
    version="1.0.0",
    description="Микросервис для управления заказами",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "order_service",
        "version": "1.0.0"
    }
