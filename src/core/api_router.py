from fastapi import APIRouter

from src import consumer

api_router = APIRouter()
api_router.include_router(consumer.router, prefix="/consumer")
