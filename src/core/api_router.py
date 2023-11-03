from fastapi import APIRouter

from src import automation_settings, consumer, current_data

api_router = APIRouter()
api_router.include_router(automation_settings.router, prefix="/settings")
api_router.include_router(consumer.router, prefix="/consumer")
api_router.include_router(current_data.router, prefix="/current_data")
