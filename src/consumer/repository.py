from typing import Any, Generic, Type, TypeVar

from fastapi import HTTPException
from tortoise import Model

from src.consumer.models import Consumer

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
