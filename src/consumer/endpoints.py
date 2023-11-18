import asyncio
from typing import Any, List

from fastapi import APIRouter, HTTPException, status

from src.consumer.models import (
    Consumer,
    ConsumerComponent,
    ConsumerComponentIn_Pydantic,
    ConsumerComponentOut_Pydantic,
    ConsumerIn_Pydantic,
    ConsumerOut_Pydantic,
)
from src.consumer.repository import ConsumerRepository

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
async def create_consumer(consumer_in: ConsumerIn_Pydantic) -> Any:
    consumer_obj = await Consumer.create(**consumer_in.model_dump())
    return await ConsumerOut_Pydantic.from_tortoise_orm(consumer_obj)


@router.get("/{consumer_id}/component/")
async def get_components(consumer_id: int) -> Any:
    consumer = await ConsumerRepository().get(consumer_id)
    components = await consumer.components

    # TODO: Test what happens if the consumer has no component (Shouldn't be the case but test it)
    components_out = await asyncio.gather(
        *[
            ConsumerComponentOut_Pydantic.from_tortoise_orm(component)
            for component in components
        ]
    )

    return components_out


@router.get(
    "/{consumer_id}/component/{component_id}",
    response_model=ConsumerComponentOut_Pydantic,
)
async def get_component(consumer_id: int, component_id: int) -> Any:
    consumer = await ConsumerRepository().get(consumer_id)
    component = await consumer.components.filter(id=component_id).first()

    if not component:
        raise HTTPException(
            status_code=404,
            detail=f"Consumer {consumer.id} has no component with id={component_id}",
        )

    return await ConsumerComponentOut_Pydantic.from_tortoise_orm(component)


@router.post(
    "/{consumer_id}/component/",
    response_model=ConsumerComponentOut_Pydantic,
    status_code=status.HTTP_201_CREATED,
)
async def create_component(
    consumer_id: int, component_in: ConsumerComponentIn_Pydantic
) -> Any:
    consumer = await ConsumerRepository().get(consumer_id)

    component_obj = await ConsumerComponent.create(
        consumer=consumer, **component_in.model_dump()
    )
    return await ConsumerComponentOut_Pydantic.from_tortoise_orm(component_obj)
