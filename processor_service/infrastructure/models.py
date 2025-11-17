"""
ORM модели для работы с БД (ormar)
"""
import uuid
from typing import Optional, List
from datetime import datetime
from ormar import Model, Integer, String, Float, DateTime, JSON
from processor_service.infrastructure.database import BaseMeta


class OrderProcessing(Model):
    """Модель обработки заказа в БД"""
    
    class Meta(BaseMeta):
        tablename = "order_processing"
    
    id: str = String(primary_key=True, max_length=36, default=lambda: str(uuid.uuid4()))
    order_id: str = String(max_length=36, nullable=False, unique=True, index=True)
    customer_id: str = String(max_length=255, nullable=False)
    items: List[dict] = JSON(nullable=False)  # Список товаров в формате JSON
    total_amount: float = Float(nullable=False)
    status: str = String(max_length=50, nullable=False, default="processing")
    error_message: str = String(max_length=1000, nullable=True)
    processed_at: Optional[datetime] = DateTime(nullable=True)
    created_at: Optional[datetime] = DateTime(default=datetime.utcnow)
    updated_at: Optional[datetime] = DateTime(default=datetime.utcnow, onupdate=datetime.utcnow)

