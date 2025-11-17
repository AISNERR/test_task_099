#!/bin/bash

# Скрипт для запуска всех сервисов локально

set -e

echo "🚀 Starting Order Management System..."

# Проверка наличия Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Проверка наличия Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Запуск через Docker Compose
echo "📦 Starting services with Docker Compose..."
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 10

# Проверка здоровья сервисов
echo "🏥 Checking service health..."

# Order Service
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Order Service is healthy"
else
    echo "⚠️  Order Service is not responding yet"
fi

# Processor Service
if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    echo "✅ Processor Service is healthy"
else
    echo "⚠️  Processor Service is not responding yet"
fi

echo ""
echo "🎉 Services are starting!"
echo ""
echo "📚 API Documentation:"
echo "   Order Service:    http://localhost:8000/docs"
echo "   Processor Service: http://localhost:8001/docs"
echo ""
echo "📊 View logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose down"

