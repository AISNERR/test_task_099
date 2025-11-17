import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Настройки Processor сервиса"""

    def __init__(self):
        # Database
        self.pg_host = os.getenv("PG_HOST", "localhost")
        self.pg_port = int(os.getenv("PG_PORT", 5433))
        self.pg_user = os.getenv("PG_USER", "processor_user")
        self.pg_password = os.getenv("PG_PASSWORD", "processor_password")
        self.pg_db = os.getenv("PG_DB", "processor_db")
        default_db_url = (
            f"postgresql+asyncpg://{self.pg_user}:{self.pg_password}"
            f"@{self.pg_host}:{self.pg_port}/{self.pg_db}"
        )
        self.database_url = os.getenv("DATABASE_URL", default_db_url)

        # Message Broker (Kafka)
        self.kafka_bootstrap_servers = os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"
        )
        self.order_created_topic = os.getenv("ORDER_CREATED_TOPIC", "order.created")
        self.order_processed_topic = os.getenv(
            "ORDER_PROCESSED_TOPIC", "order.processed"
        )
        self.processor_dlq_topic = os.getenv("PROCESSOR_DLQ_TOPIC", "processor.dlq")

        # Service
        self.service_name = os.getenv("SERVICE_NAME", "processor_service")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"


settings = Settings()

