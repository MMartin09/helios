from typing import List

from tortoise.expressions import Q

from src.consumer.models import Consumer
from src.core.definitions import ConsumerMode, ConsumerStatus


class ConsumerManager:
    """Consumer Manager."""

    def __init__(self) -> None:
        ...

    async def get_running_consumers(self) -> List[Consumer] | None:
        """Get all running consumers ordered by priority in descending order.

        Consumers are filtered to include only those in mode AUTOMATIC and not in status STOPPED.
        Consumers marked as status PARTIAL_RUNNING are also included.

        Returns:
            The list of running consumers. None if no consumer is running.

        """
        return (
            await Consumer.filter(
                Q(state__mode=ConsumerMode.AUTOMATIC)
                & ~Q(state__status=ConsumerStatus.STOPPED)
            )
            .order_by("-priority")
            .prefetch_related("components")
        )

    async def get_stopped_consumers(self) -> List[Consumer] | None:
        """Get all stopped consumers ordered by priority in ascending order.

        Consumers are filtered to include only those in mode AUTOMATIC and not in status RUNNING.
        Consumers marked as status PARTIAL_RUNNING are also included.

        Returns:
            The list of stopped consumers. None if no consumer is stopped.

        """
        return (
            await Consumer.filter(
                Q(state__mode=ConsumerMode.AUTOMATIC)
                & ~Q(state__status=ConsumerStatus.RUNNING)
            )
            .order_by("-priority")
            .prefetch_related("components")
        )
