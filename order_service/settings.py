from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки Order сервиса"""
    
    # Database
    database_url: str = "postgresql+asyncpg://order_user:order_password@localhost:5432/order_db"
    
    # Message Broker (RabbitMQ)
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    order_created_exchange: str = "orders"
    order_created_queue: str = "order.created"
    order_processed_exchange: str = "orders"
    order_processed_queue: str = "order.processed"
    
    # Service
    service_name: str = "order_service"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

