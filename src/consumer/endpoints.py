from typing import Any

from fastapi import APIRouter

from src.consumer.models import Consumer, ConsumerIn_Pydantic, ConsumerOut_Pydantic

router = APIRouter()


@router.get("/", response_model=ConsumerOut_Pydantic)
async def get_consumers() -> Any:
    return await ConsumerOut_Pydantic.from_queryset(Consumer.all())


@router.post("/", response_model=ConsumerOut_Pydantic)
async def create_consumer(consumer: ConsumerIn_Pydantic) -> Any:
    consumer_obj = await Consumer.create(**consumer.model_dump())
    return await ConsumerOut_Pydantic.from_tortoise_orm(consumer_obj)
