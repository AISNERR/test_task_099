"""
Processor Service - главный файл приложения
"""
from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from processor_service.infrastructure.database import init_db, close_db
from processor_service.infrastructure.kafka_client import kafka_producer
from processor_service.consumers.order_consumer import order_created_consumer

# Настройка логирования
from processor_service.infrastructure.logging_config import setup_logging
from processor_service.settings import settings

setup_logging(level="DEBUG" if settings.debug else "INFO", structured=False)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Инициализация при старте
    logger.info("Starting Processor Service...")
    try:
        await init_db()
        logger.info("Database initialized")
        
        await kafka_producer.start()
        logger.info("Kafka producer started")
        
        await order_created_consumer.start()
        logger.info("Kafka consumer started")
        
        logger.info("Processor Service started successfully")
    except Exception as e:
        logger.error(f"Failed to start Processor Service: {e}", exc_info=True)
        raise
    
    yield
    
    # Очистка при остановке
    logger.info("Shutting down Processor Service...")
    try:
        await order_created_consumer.stop()
        await kafka_producer.stop()
        await close_db()
        logger.info("Processor Service stopped successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}", exc_info=True)


app = FastAPI(
    title="Processor Service",
    version="1.0.0",
    description="Микросервис для обработки заказов",
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


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "processor_service",
        "version": "1.0.0"
    }

