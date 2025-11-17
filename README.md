# Система управления заказами

Распределенная система из двух микросервисов для управления заказами с использованием событийно-ориентированной архитектуры.

## Архитектура

Система состоит из двух автономных микросервисов:

1. **Order Service** - принимает запросы на создание заказов, сохраняет их в БД и публикует события
2. **Processor Service** - подписывается на события создания заказов, обрабатывает их и публикует результаты

### Технологический стек

- **Python 3.11**
- **FastAPI** - веб-фреймворк
- **PostgreSQL** - реляционная БД
- **Kafka** - брокер сообщений
- **Ormar** - ORM для работы с БД
- **Alembic** - миграции БД
- **Docker & Docker Compose** - контейнеризация

### Архитектурные принципы

- **TDD (Test-Driven Development)** - разработка через тестирование
- **DDD (Domain-Driven Design)** - доменно-ориентированное проектирование
- **Чистая архитектура** - разделение на слои (Domain, Services, Infrastructure, API)
- **Event-Driven Architecture** - событийно-ориентированная архитектура
- **SAGA Pattern** - распределенные транзакции через события

## Структура проекта

```
test_task_099/
├── order_service/          # Сервис заказов
│   ├── alembic/            # Миграции БД
│   ├── api/                # HTTP API слой
│   ├── consumers/          # Kafka consumers
│   ├── domain/              # Доменные модели и события
│   ├── infrastructure/     # Инфраструктура (БД, Kafka)
│   ├── services/           # Бизнес-логика
│   ├── tests/              # Тесты
│   ├── Dockerfile
│   └── requirements.txt
├── processor_service/       # Сервис обработки
│   ├── alembic/            # Миграции БД
│   ├── consumers/          # Kafka consumers
│   ├── domain/              # Доменные модели и события
│   ├── infrastructure/     # Инфраструктура (БД, Kafka)
│   ├── services/           # Бизнес-логика
│   ├── tests/              # Тесты
│   ├── Dockerfile
│   └── requirements.txt
└── docker-compose.yml      # Оркестрация контейнеров
```

## Быстрый старт

### Предварительные требования

- Docker и Docker Compose
- Python 3.11+ (для локальной разработки)

### Запуск через Docker Compose

1. Клонируйте репозиторий:
```bash
git clone <repository_url>
cd test_task_099
```

2. Запустите все сервисы:
```bash
docker-compose up -d
```

3. Дождитесь запуска всех сервисов (проверьте логи):
```bash
docker-compose logs -f
```

4. Сервисы будут доступны:
   - Order Service: http://localhost:8000
   - Processor Service: http://localhost:8001
   - Order Service API Docs: http://localhost:8000/docs
   - Processor Service API Docs: http://localhost:8001/docs

### Локальный запуск (для разработки)

1. Настройте переменные окружения:
```bash
# Order Service
cp order_service/.env.example order_service/.env
# Отредактируйте order_service/.env при необходимости

# Processor Service
cp processor_service/.env.example processor_service/.env
# Отредактируйте processor_service/.env при необходимости
```

2. Установите зависимости:
```bash
cd order_service
pip install -r requirements.txt

cd ../processor_service
pip install -r requirements.txt
```

2. Запустите PostgreSQL и Kafka через Docker Compose:
```bash
docker-compose up -d order_db processor_db zookeeper kafka
```

3. Выполните миграции:
```bash
# Order Service
cd order_service
alembic upgrade head

# Processor Service
cd ../processor_service
alembic upgrade head
```

4. Запустите сервисы:
```bash
# Order Service (в отдельном терминале)
cd order_service
uvicorn order_service.main:app --reload --port 8000

# Processor Service (в отдельном терминале)
cd processor_service
uvicorn processor_service.main:app --reload --port 8001
```

## API Endpoints

### Order Service (http://localhost:8000)

#### POST /orders
Создание нового заказа

**Request Body:**
```json
{
  "customer_id": "customer_123",
  "items": [
    {
      "product_id": "prod_1",
      "quantity": 2
    }
  ],
  "total_amount": 1500.50
}
```

**Response (201):**
```json
{
  "order_id": "uuid",
  "customer_id": "customer_123",
  "items": [...],
  "total_amount": 1500.50,
  "status": "created"
}
```

#### GET /orders/{order_id}
Получение статуса заказа

**Response (200):**
```json
{
  "order_id": "uuid",
  "customer_id": "customer_123",
  "items": [...],
  "total_amount": 1500.50,
  "status": "created|processed|failed"
}
```

#### GET /health
Health check endpoint

### Processor Service (http://localhost:8001)

#### GET /health
Health check endpoint

## События Kafka

### order.created
Публикуется Order Service при создании заказа.

**Топик:** `order.created`

**Структура:**
```json
{
  "order_id": "uuid",
  "customer_id": "customer_123",
  "items": [
    {
      "product_id": "prod_1",
      "quantity": 2
    }
  ],
  "total_amount": 1500.50,
  "created_at": "2024-01-01T12:00:00"
}
```

### order.processed
Публикуется Processor Service после обработки заказа.

**Топик:** `order.processed`

**Структура:**
```json
{
  "order_id": "uuid",
  "status": "success|failed",
  "error_message": "",
  "processed_at": "2024-01-01T12:00:05"
}
```

## Тестирование

### Запуск тестов

```bash
# Order Service
cd order_service
pytest tests/ -v

# Processor Service
cd processor_service
pytest tests/ -v

# Все тесты
pytest order_service/tests processor_service/tests -v
```

### Покрытие тестами

```bash
pytest --cov=order_service --cov=processor_service --cov-report=html
```

## Миграции БД

### Создание новой миграции

```bash
# Order Service
cd order_service
alembic revision --autogenerate -m "description"

# Processor Service
cd processor_service
alembic revision --autogenerate -m "description"
```

### Применение миграций

```bash
# Order Service
cd order_service
alembic upgrade head

# Processor Service
cd processor_service
alembic upgrade head
```

### Откат миграций

```bash
alembic downgrade -1
```

## Обеспечение надежности

### Идемпотентность

- **Order Processing**: Уникальный индекс на `order_id` в таблице `order_processing` гарантирует, что один заказ не будет обработан дважды
- **Status Updates**: Проверка существования заказа перед обновлением статуса

### Retry механизм

Реализован retry механизм с экспоненциальной задержкой для:
- Публикации событий в Kafka (3 попытки, задержка 1s, backoff 2x)
- Обработки событий из Kafka (3 попытки)
- Обновления статусов заказов (3 попытки)

### Обработка ошибок

- Все ошибки логируются с полным контекстом
- При неудачной публикации события заказ все равно создается (eventual consistency)
- В продакшене рекомендуется добавить Dead Letter Queue для сообщений, которые не удалось обработать после всех retry

### Транзакционность

- Создание заказа и публикация события выполняются последовательно
- При ошибке публикации события заказ остается в БД (можно добавить флаг "event_published" для отслеживания)
- Processor Service сохраняет состояние обработки в БД перед публикацией события

## Логирование

Логирование настроено для всех значимых событий:
- Создание заказов
- Публикация/получение событий Kafka
- Обработка заказов
- Ошибки и retry попытки

## Мониторинг

Health check endpoints доступны на:
- Order Service: `GET http://localhost:8000/health`
- Processor Service: `GET http://localhost:8001/health`

## Ограничения и возможные улучшения

### Текущие ограничения

1. Нет Dead Letter Queue для сообщений, которые не удалось обработать
2. Нет механизма отслеживания непубликованных событий
3. Симуляция обработки заказов (в реальной системе нужна бизнес-логика)
4. Нет метрик и мониторинга (Prometheus, Grafana)

### Возможные улучшения

1. **Dead Letter Queue** - для сообщений, которые не удалось обработать после всех retry
2. **Outbox Pattern** - для гарантии публикации событий (транзакционная outbox таблица)
3. **Метрики** - интеграция с Prometheus и Grafana
4. **Трассировка** - распределенная трассировка через OpenTelemetry
5. **Rate Limiting** - ограничение количества запросов
6. **Аутентификация** - JWT токены для API
7. **Кэширование** - Redis для кэширования часто запрашиваемых данных
8. **Шардирование** - для масштабирования БД

## Контакты
Misha Aisner
southeast21k@gmail.com Misha Aisner
