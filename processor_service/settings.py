from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки Processor сервиса"""
    
    # Database
    database_url: str = "postgresql+asyncpg://processor_user:processor_password@localhost:5433/processor_db"
    
    # Message Broker (Kafka)
    kafka_bootstrap_servers: str = "localhost:9092"
    order_created_topic: str = "order.created"
    order_processed_topic: str = "order.processed"
    
    # Service
    service_name: str = "processor_service"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        # Позволяем переопределять через переменные окружения
        env_prefix = ""


settings = Settings()

