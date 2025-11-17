FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

# Переменные окружения
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Порт для FastAPI
EXPOSE 8001

# Команда запуска
CMD ["uvicorn", "processor_service.main:app", "--host", "0.0.0.0", "--port", "8001"]

