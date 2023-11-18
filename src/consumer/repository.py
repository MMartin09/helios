from typing import Any, Generic, Type, TypeVar

from fastapi import HTTPException
from tortoise import Model

from src.consumer.models import Consumer, ConsumerComponent

T = TypeVar("T", bound=Model)


class BaseRepository(Generic[T]):
    model = Type[T]

    async def _get(self, key: str, value: Any):
        result = await self.model.filter(**{key: value}).first()

        if not result:
            # TODO: Implement Logging
            raise HTTPException(
                status_code=404,
                detail=f"No {self.model.__name__} with id={value} found",
            )

        return result


class ConsumerRepository(BaseRepository[Consumer]):
    model = Consumer

    async def get(self, id: int) -> Consumer:
        consumer = await self._get(key="id", value=id)
        return consumer


class ComponentRepository:
    async def get_by_consumer(
        self, consumer_id: int, component_id: int
    ) -> ConsumerComponent:
        if not await Consumer.filter(id=consumer_id).exists():
            raise HTTPException(
                status_code=404, detail=f"No consumer with id={consumer_id} found"
            )

        component = await ConsumerComponent.filter(
            consumer=consumer_id, id=component_id
        ).first()
        if not component:
            raise HTTPException(
                status_code=404,
                detail=f"Consumer {consumer_id} has no component with id={component_id}",
            )
        return component
