from fastapi import APIRouter

from src import consumer, current_data

api_router = APIRouter()
api_router.include_router(consumer.router, prefix="/consumer")
api_router.include_router(current_data.router, prefix="/current_data")
