#!/bin/bash

# Скрипт для запуска тестов

set -e

echo "🧪 Running tests..."

# Проверка наличия pytest
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest is not installed. Installing..."
    pip install pytest pytest-asyncio
fi

# Запуск тестов для Order Service
echo "📦 Testing Order Service..."
cd order_service
if [ -d "tests" ]; then
    pytest tests/ -v --tb=short
else
    echo "⚠️  No tests found in order_service/tests"
fi
cd ..

# Запуск тестов для Processor Service
echo "📦 Testing Processor Service..."
cd processor_service
if [ -d "tests" ]; then
    pytest tests/ -v --tb=short
else
    echo "⚠️  No tests found in processor_service/tests"
fi
cd ..

echo ""
echo "✅ All tests completed!"

