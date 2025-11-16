"""
Order Service - главный файл приложения
"""
from fastapi import FastAPI
from order_service.api.routes import router

app = FastAPI(title="Order Service", version="1.0.0")

app.include_router(router)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "order_service"}

