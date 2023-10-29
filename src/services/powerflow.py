from loguru import logger
from tortoise.expressions import Q

from src.consumer.models import Consumer
from src.core.definitions import ConsumerMode, ConsumerStatus, GridMode
from src.services.grid_manager import grid_manager_service


class PowerflowService:
    def __init__(self) -> None:
        self._grid_manager_service = grid_manager_service
        self._grid_mode: GridMode = GridMode.NOT_SET

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
            consumers = await Consumer.filter(
                Q(state__mode=ConsumerMode.AUTOMATIC)
                & ~Q(state__status=ConsumerStatus.STOPPED)
            ).order_by("priority")
            logger.debug(f"Running or partial running consumers: {consumers}")

    def _update_grid_mode(self, p_grid) -> None:
        if (grid_mode := self._grid_manager_service.update(p_grid)) != self._grid_mode:
            logger.info(f"Switching GridMode from {self._grid_mode} to {grid_mode}")
            self._grid_mode = grid_mode


powerflow_service = PowerflowService()
