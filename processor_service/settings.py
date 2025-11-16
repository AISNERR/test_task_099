from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки Processor сервиса"""
    
    # Database
    database_url: str = "postgresql+asyncpg://processor_user:processor_password@localhost:5433/processor_db"
    
    # Message Broker (RabbitMQ)
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    order_created_exchange: str = "orders"
    order_created_queue: str = "order.created"
    order_processed_exchange: str = "orders"
    order_processed_queue: str = "order.processed"
    
    # Service
    service_name: str = "processor_service"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

