"""
Processor Service - главный файл приложения
"""
from fastapi import FastAPI

app = FastAPI(title="Processor Service", version="1.0.0")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "processor_service"}

