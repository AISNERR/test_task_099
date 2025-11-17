FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода внутрь пакета order_service
COPY . /app/order_service

# Переменные окружения
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Рабочая директория приложения
WORKDIR /app

# Порт для FastAPI
EXPOSE 8000

# Команда запуска
CMD ["uvicorn", "order_service.main:app", "--host", "0.0.0.0", "--port", "8000"]

