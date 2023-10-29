from typing import Any, List

from fastapi import APIRouter
from loguru import logger

from src.consumer.models import (
    Consumer,
    ConsumerIn_Pydantic,
    ConsumerOut_Pydantic,
)

router = APIRouter(tags=["consumer"])


@router.get("/", response_model=List[ConsumerOut_Pydantic])
async def get_consumers() -> Any:
    c = await Consumer.all().prefetch_related("components")
    c = await c[0].components.all()
    logger.debug(c)
    return await ConsumerOut_Pydantic.from_queryset(
        Consumer.all().prefetch_related("components")
    )


@router.post("/", response_model=ConsumerOut_Pydantic)
async def create_consumer(consumer: ConsumerIn_Pydantic) -> Any:
    consumer_obj = await Consumer.create(**consumer.model_dump())
    return await ConsumerOut_Pydantic.from_tortoise_orm(consumer_obj)
