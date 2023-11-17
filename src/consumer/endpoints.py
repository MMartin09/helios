from typing import Any, List

from fastapi import APIRouter, status

from src.consumer.models import (
    Consumer,
    ConsumerComponentOut_Pydantic,
    ConsumerIn_Pydantic,
    ConsumerOut_Pydantic,
)

router = APIRouter(tags=["consumer"])


@router.get(
    "/",
    response_model=List[ConsumerOut_Pydantic],
    summary="Get all consumers",
    description="Get a list of all consumers available in the database.",
)
async def get_consumers() -> Any:
    return await ConsumerOut_Pydantic.from_queryset(
        Consumer.all().prefetch_related("components")
    )


@router.post(
    "/", response_model=ConsumerOut_Pydantic, status_code=status.HTTP_201_CREATED
)
async def create_consumer(consumer: ConsumerIn_Pydantic) -> Any:
    consumer_obj = await Consumer.create(**consumer.model_dump())
    return await ConsumerOut_Pydantic.from_tortoise_orm(consumer_obj)


@router.get(
    "/{consumer_id}/component/", response_model=List[ConsumerComponentOut_Pydantic]
)
async def get_components(consumer_id: int) -> Any:
    ...


@router.get(
    "/{consumer_id}/component/{component_id}",
    response_model=ConsumerComponentOut_Pydantic,
)
async def get_component(consumer_id: int, component_id: int) -> Any:
    ...


@router.post(
    "/{consumer_id}/component/",
    response_model=ConsumerComponentOut_Pydantic,
    status_code=status.HTTP_201_CREATED,
)
async def create_component(consumer_id: int) -> Any:
    ...
