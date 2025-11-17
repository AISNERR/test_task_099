#!/bin/bash

# Скрипт для применения миграций

set -e

SERVICE=$1

if [ -z "$SERVICE" ]; then
    echo "Usage: ./scripts/migrate.sh [order_service|processor_service]"
    exit 1
fi

if [ "$SERVICE" != "order_service" ] && [ "$SERVICE" != "processor_service" ]; then
    echo "❌ Invalid service. Use 'order_service' or 'processor_service'"
    exit 1
fi

echo "🔄 Running migrations for $SERVICE..."

cd "$SERVICE"

if [ ! -f "alembic.ini" ]; then
    echo "❌ alembic.ini not found in $SERVICE"
    exit 1
fi

# Применение миграций
alembic upgrade head

echo "✅ Migrations applied successfully for $SERVICE"

