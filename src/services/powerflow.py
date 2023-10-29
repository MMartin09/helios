from typing import List

from loguru import logger
from tortoise.expressions import Q

from src.consumer.models import Consumer
from src.core.definitions import ConsumerMode, ConsumerStatus, GridMode
from src.services.grid_manager import grid_manager_service


class StartConsumerService:
    def __init__(self) -> None:
        ...

    async def get_next_consumer(self) -> None:
        consumers = await self._get_stopped_consumers()
        if not consumers:
            logger.debug("No consumer left to start")
            return

    async def _get_stopped_consumers(self) -> List[Consumer]:
        return await Consumer.filter(
            Q(state__mode=ConsumerMode.AUTOMATIC)
            & ~Q(state__status=ConsumerStatus.RUNNING)
        ).order_by("-priority")


class StopConsumerService:
    def __init__(self) -> None:
        ...

    async def get_next_consumer(self) -> None:
        consumers = await self._get_running_consumers()
        if consumers:
            logger.debug("No consumer left to stop")
            return

        logger.debug(f"Found {len(consumers)} running consumers in automatic mode!")

    async def _get_running_consumers(self) -> List[Consumer]:
        return await Consumer.filter(
            Q(state__mode=ConsumerMode.AUTOMATIC)
            & ~Q(state__status=ConsumerStatus.RUNNING)
        ).order_by("-priority")


class PowerflowService:
    """TODO: Add docs"""

    def __init__(self) -> None:
        self._grid_manager_service = grid_manager_service
        self._grid_mode: GridMode = GridMode.NOT_SET

        self._start_consumer_service = StartConsumerService()
        self._stop_consumer_service = StopConsumerService()

    async def update(self, p_grid: float) -> None:
        """Update the service state with the current grid value.

        Args:
            p_grid: Current grid value.
        """

        self._update_grid_mode(p_grid)

        if self._grid_mode == GridMode.FEED_IN:
            consumers = await Consumer.filter(
                Q(state__mode=ConsumerMode.AUTOMATIC)
                & ~Q(state__status=ConsumerStatus.RUNNING)
            ).order_by("-priority")
            # logger.debug(f"Stopped or partial running consumers: {consumers}")

            for consumer in consumers:
                components = await consumer.components.all()
                c = [
                    f"name={component.name};consumption={component.consumption};running={component.running}"
                    for component in components
                ]
                logger.debug(f"Consumer: {consumer.name}; Components={list(c)}")

        elif self._grid_mode == GridMode.CONSUME:
            await self._stop_consumer_service.get_next_consumer()

    def _update_grid_mode(self, p_grid) -> None:
        """Update the GridMode using the current grid value.

        Args:
            p_grid: Current grid value.
        """

        if (grid_mode := self._grid_manager_service.update(p_grid)) != self._grid_mode:
            logger.info(f"Switching GridMode from {self._grid_mode} to {grid_mode}")
            self._grid_mode = grid_mode


powerflow_service = PowerflowService()
