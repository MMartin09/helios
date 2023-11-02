from itertools import combinations
from typing import List, Tuple

from loguru import logger
from tortoise.expressions import Q

from src.consumer.models import Consumer, ConsumerComponent
from src.core.definitions import ConsumerMode, ConsumerStatus, ConsumerType, GridMode
from src.services.component import ComponentService
from src.services.grid_manager import grid_manager_service


class ConsumerServiceBase:
    def __init__(self) -> None:
        self._component_service = ComponentService()


class StartConsumerService(ConsumerServiceBase):
    def __init__(self) -> None:
        super().__init__()

    async def get_next_consumer(self, surplus: float) -> None:
        consumers = await self._get_stopped_consumers()
        if not consumers:
            logger.debug("No consumer left to start")
            return

        # TODO: If the rules are implemented to check if a consumer can be started iterate over the consumers
        target_consumer = consumers[0]

        if target_consumer.consumer_type() == ConsumerType.SCC:
            ...
        elif target_consumer.consumer_type() == ConsumerType.MCC:
            consumer_state = await target_consumer.state.first()
            components = await target_consumer.components.all()

            # Current surplus if no component of the consumer would run
            virtual_surplus = surplus + consumer_state.current_consumption

            (
                best_combination,
                combination_consumption,
            ) = await self._get_best_combination(components, virtual_surplus)
            running_components = [
                component for component in components if component.running
            ]

            if not best_combination:
                logger.info("No component could be started")
                return

            best_combination_set = set(best_combination)
            running_components_set = set(running_components)

            components_to_start = list(best_combination_set - running_components_set)
            components_to_stop = list(running_components_set - best_combination_set)

            logger.debug(
                f"Target Consumer {target_consumer.name}: Best Combination: {best_combination}; To Start: {components_to_start}; To Stop: {components_to_stop}"
            )
            logger.debug(f"Currently running components: {running_components}")

            new_mode = (
                ConsumerStatus.RUNNING
                if len(best_combination) == len(components)
                else ConsumerStatus.PARTIAL_RUNNING
            )

            consumer_state.status = new_mode
            consumer_state.current_consumption = combination_consumption
            await consumer_state.save()

            for component in components_to_stop:
                await self._component_service.stop_component(component)
            for component in components_to_start:
                await self._component_service.start_component(component)

    async def _get_stopped_consumers(self) -> List[Consumer]:
        return (
            await Consumer.filter(
                Q(state__mode=ConsumerMode.AUTOMATIC)
                & ~Q(state__status=ConsumerStatus.RUNNING)
            )
            .order_by("-priority")
            .prefetch_related("components")
        )

    async def _get_best_combination(
        self, components: List[ConsumerComponent], current_surplus: float
    ) -> Tuple[List[ConsumerComponent], float]:
        best = {
            "surplus": float("inf"),
            "combination": None,
            "consumption": float("inf"),
        }

        for r in range(1, len(components) + 1):
            for combination in combinations(components, r):
                combination_consumption = sum(
                    component.consumption for component in combination
                )
                new_surplus = current_surplus - combination_consumption

                if 0 <= new_surplus < best["surplus"]:
                    best["surplus"] = new_surplus
                    best["combination"] = combination
                    best["consumption"] = combination_consumption

        return best["combination"], best["consumption"]


class StopConsumerService(ConsumerServiceBase):
    def __init__(self) -> None:
        super().__init__()

    async def get_next_consumer(self) -> None:
        consumers = await self._get_running_consumers()
        if not consumers:
            logger.debug("No consumer left to stop")
            return

        # TODO: If the rules are implemented to check if a consumer can be stopped iterate over the consumers
        target_consumer = consumers[0]

        logger.debug(f"Found {len(consumers)} running consumers in automatic mode!")
        logger.debug(f"Target consumer: {target_consumer.id} ({target_consumer.name})")

        # Query all components of the consumer and sort them descending by the consumption
        components = await target_consumer.components.all().order_by("-consumption")
        # Filter out only the running components
        running_components = [
            component for component in components if component.running
        ]
        # Target component is the running component with the highest consumption (or the only one if it is an SCC)
        target_component = running_components[0]

        consumer_state = await target_consumer.state.first()

        if target_consumer.consumer_type() == ConsumerType.SCC:
            logger.debug(
                f"Stopping component {target_component.id} ({target_component.name}) consumption={target_component.consumption}! Switching consumer from {ConsumerStatus.RUNNING} to {ConsumerStatus.STOPPED}"
            )

            await self._stop_component(target_component)

            # TODO: Same code below
            consumer_state.status = ConsumerStatus.STOPPED
            await consumer_state.save()
        elif target_consumer.consumer_type() == ConsumerType.MCC:
            current_mode = consumer_state.status
            new_mode = (
                ConsumerStatus.PARTIAL_RUNNING
                if len(running_components) > 1
                else ConsumerStatus.STOPPED
            )

            logger.debug(
                f"Stopping component {target_component.id} ({target_component.name}) consumption={target_component.consumption}! Switching consumer from {current_mode} to {new_mode}"
            )

            await self._component_service.stop_component(target_component)

            consumer_state.status = new_mode
            consumer_state.current_consumption -= target_component.consumption
            await consumer_state.save()

    async def _get_running_consumers(self) -> List[Consumer]:
        return (
            await Consumer.filter(
                Q(state__mode=ConsumerMode.AUTOMATIC)
                & ~Q(state__status=ConsumerStatus.STOPPED)
            )
            .order_by("-priority")
            .prefetch_related("components")
        )


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
            await self._start_consumer_service.get_next_consumer(surplus=abs(p_grid))
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
