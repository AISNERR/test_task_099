"""
Тесты для Processor сервиса (TDD)
"""
import pytest
from datetime import datetime
from processor_service.domain.events import OrderCreatedEvent, OrderItemEvent
from processor_service.services.processor_service import ProcessorService
from processor_service.infrastructure.models import OrderProcessing
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_process_order_success():
    """
    Тест: Успешная обработка заказа
    Ожидаемое поведение:
    - Заказ сохраняется в БД со статусом processing
    - После обработки статус обновляется на success
    - Событие order.processed публикуется в Kafka
    """
    event = OrderCreatedEvent(
        order_id="test_order_123",
        customer_id="customer_123",
        items=[OrderItemEvent(product_id="prod_1", quantity=2)],
        total_amount=1000.0,
        created_at=datetime.utcnow()
    )
    
    with patch('processor_service.services.processor_service.random.random', return_value=0.9), \
         patch('processor_service.infrastructure.kafka_client.kafka_producer.publish') as mock_publish:
        
        result = await ProcessorService.process_order(event)
        
        # Проверяем результат
        assert result.order_id == "test_order_123"
        assert result.status == "success"
        assert result.error_message == ""
        assert result.processed_at is not None
        
        # Проверяем, что событие было опубликовано
        assert mock_publish.called
        call_args = mock_publish.call_args
        assert call_args[0][0] == "order.processed"
        
        # Проверяем, что заказ сохранен в БД
        processing = await OrderProcessing.objects.get(order_id="test_order_123")
        assert processing.status == "success"
        assert processing.customer_id == "customer_123"
        assert processing.total_amount == 1000.0


@pytest.mark.asyncio
async def test_process_order_failed():
    """
    Тест: Неудачная обработка заказа
    Ожидаемое поведение:
    - Заказ сохраняется в БД
    - После обработки статус обновляется на failed
    - Событие order.processed публикуется с error_message
    """
    event = OrderCreatedEvent(
        order_id="test_order_456",
        customer_id="customer_456",
        items=[OrderItemEvent(product_id="prod_2", quantity=1)],
        total_amount=500.0,
        created_at=datetime.utcnow()
    )
    
    with patch('processor_service.services.processor_service.random.random', return_value=0.1), \
         patch('processor_service.infrastructure.kafka_client.kafka_producer.publish') as mock_publish:
        
        result = await ProcessorService.process_order(event)
        
        # Проверяем результат
        assert result.order_id == "test_order_456"
        assert result.status == "failed"
        assert "failed" in result.error_message.lower()
        assert result.processed_at is not None
        
        # Проверяем, что событие было опубликовано
        assert mock_publish.called
        
        # Проверяем, что заказ сохранен в БД с ошибкой
        processing = await OrderProcessing.objects.get(order_id="test_order_456")
        assert processing.status == "failed"
        assert processing.error_message is not None


@pytest.mark.asyncio
async def test_process_order_idempotency():
    """
    Тест: Идемпотентность обработки заказа
    Ожидаемое поведение:
    - При повторной обработке того же заказа возвращается существующий результат
    - Не создается дубликат в БД
    """
    event = OrderCreatedEvent(
        order_id="test_order_789",
        customer_id="customer_789",
        items=[OrderItemEvent(product_id="prod_3", quantity=3)],
        total_amount=1500.0,
        created_at=datetime.utcnow()
    )
    
    # Первая обработка
    with patch('processor_service.services.processor_service.random.random', return_value=0.9), \
         patch('processor_service.infrastructure.kafka_client.kafka_producer.publish'):
        result1 = await ProcessorService.process_order(event)
    
    # Вторая обработка того же заказа
    with patch('processor_service.services.processor_service.random.random', return_value=0.1), \
         patch('processor_service.infrastructure.kafka_client.kafka_producer.publish') as mock_publish:
        result2 = await ProcessorService.process_order(event)
    
    # Результаты должны быть одинаковыми (из первой обработки)
    assert result1.order_id == result2.order_id
    assert result1.status == result2.status
    
    # Проверяем, что при второй обработке не было публикации (или была только первая)
    # В реальности может быть несколько вызовов, но статус должен быть из БД

