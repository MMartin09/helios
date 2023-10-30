from typing import List

import httpx
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
        if not consumers:
            logger.debug("No consumer left to stop")
            return

        # TODO: If the rules are implemented to check if a consumer can be stopped iterate over the consumers
        target_consumer = consumers[0]

        logger.debug(f"Found {len(consumers)} running consumers in automatic mode!")
        logger.debug(f"Target consumer: {target_consumer.id} ({target_consumer.name}")

        # Query all components of the consumer and sort them descending by the consumption
        components = await target_consumer.components.all().order_by("-consumption")
        # Filter out only the running components
        running_components = [
            component for component in components if component.running
        ]
        # Target component is the running component with the highest consumption (or the only one if it is an SCC)
        target_component = running_components[0]

        consumer_state = await target_consumer.state.first()
        if len(components) == 1:  # SCC
            logger.debug(
                f"Stopping component {target_component.id} ({target_component.name}) consumption={target_component.consumption}! Switching consumer from {ConsumerStatus.RUNNING} to {ConsumerStatus.STOPPED}"
            )

            await self._stop_component(target_component)

            # TODO: Same code below
            consumer_state.status = ConsumerStatus.STOPPED
            await consumer_state.save()
        else:  # MCC
            current_mode = consumer_state.status
            new_mode = (
                ConsumerStatus.PARTIAL_RUNNING
                if len(running_components) > 1
                else ConsumerStatus.STOPPED
            )

            logger.debug(
                f"Stopping component {target_component.id} ({target_component.name}) consumption={target_component.consumption}! Switching consumer from {current_mode} to {new_mode}"
            )

            await self._stop_component(target_component)

            consumer_state.status = new_mode
            await consumer_state.save()

    async def _get_running_consumers(self) -> List[Consumer]:
        return await Consumer.filter(
            Q(state__mode=ConsumerMode.AUTOMATIC)
            & ~Q(state__status=ConsumerStatus.STOPPED)
        ).order_by("-priority")

    async def _stop_component(self, component) -> None:
        component.running = False
        await component.save()

        payload = {"id": component.relais, "on": False}
        url = f"http://{component.ip}/rpc/Switch.Set"
        try:
            response = httpx.get(url, params=payload)
            response.raise_for_status()

            return response.json()

        except httpx.HTTPError as exc:
            print(f"Error while turning off Shelly: {exc}")
            return None


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
