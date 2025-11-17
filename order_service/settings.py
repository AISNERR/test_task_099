from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки Order сервиса"""
    
    # Database
    database_url: str = "postgresql+asyncpg://order_user:order_password@localhost:5432/order_db"
    
    # Message Broker (Kafka)
    kafka_bootstrap_servers: str = "localhost:9092"
    order_created_topic: str = "order.created"
    order_processed_topic: str = "order.processed"
    
    # Service
    service_name: str = "order_service"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

