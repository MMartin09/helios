import asyncio
from typing import Any, List

from fastapi import APIRouter, status

from src.consumer.models import (
    Consumer,
    ConsumerComponent,
    ConsumerComponentIn_Pydantic,
    ConsumerComponentOut_Pydantic,
    ConsumerIn_Pydantic,
    ConsumerOut_Pydantic,
    ConsumerState,
    ConsumerStateOut_Pydantic,
)
from src.core.dependencies import ConsumerComponentRepositoryDep, ConsumerRepositoryDep

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
    # TODO: Should also be moved into the Repository.
    consumer_obj = await Consumer.create(**consumer_in.model_dump())
    await ConsumerState.create(consumer=consumer_obj)
    return await ConsumerOut_Pydantic.from_tortoise_orm(consumer_obj)


@router.get("/{consumer_id}/state/", response_model=ConsumerStateOut_Pydantic)
async def get_state(
    consumer_id: int, consumer_repository: ConsumerRepositoryDep
) -> Any:
    state_obj = await consumer_repository.get_state(consumer_id)
    return await ConsumerStateOut_Pydantic.from_tortoise_orm(state_obj)


@router.get("/{consumer_id}/component/")
async def get_components(
    consumer_id: int, consumer_component_repository: ConsumerComponentRepositoryDep
) -> Any:
    components = await consumer_component_repository.get_all_by_consumer(consumer_id)

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
async def get_component(
    consumer_id: int,
    component_id: int,
    consumer_component_repository: ConsumerComponentRepositoryDep,
) -> Any:
    component = await consumer_component_repository.get_by_consumer(
        consumer_id, component_id
    )
    return await ConsumerComponentOut_Pydantic.from_tortoise_orm(component)


@router.post(
    "/{consumer_id}/component/",
    response_model=ConsumerComponentOut_Pydantic,
    status_code=status.HTTP_201_CREATED,
)
async def create_component(
    consumer_id: int,
    component_in: ConsumerComponentIn_Pydantic,
    consumer_repository: ConsumerRepositoryDep,
) -> Any:
    # TODO: Movie into repository
    consumer = await consumer_repository.get(consumer_id)

    component_obj = await ConsumerComponent.create(
        consumer=consumer, **component_in.model_dump()
    )
    return await ConsumerComponentOut_Pydantic.from_tortoise_orm(component_obj)
