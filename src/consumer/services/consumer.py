from typing import List

from loguru import logger
from tortoise.expressions import Q

from src import integrations
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

    async def synchronize_status_with_db(self) -> None:
        """

        TODO: Refactoring required
        TODO: What if the consumer is on mode "Hand_<>"
        TODO: Don't use the ShellySwitch integration
        TODO: Should the part with the components moved to the component manager?

        """
        _switch_integration = integrations.Switch()

        consumers = await Consumer.all().prefetch_related("components")

        for consumer in consumers:
            consumer_state = await consumer.state
            consumer_components = await consumer.components

            consumer_dirty = False
            consumer_consumption = 0
            running_components = 0
            for component in consumer_components:
                running = await _switch_integration.get_switch_status(component)
                if running != component.running:
                    logger.info(
                        f"Updating component {component.id} (consumer={consumer.id}). Status in db={component.running}; True state={running}"
                    )
                    component.running = running
                    await component.save()

                    consumer_dirty = True
                if running:
                    consumer_consumption += component.consumption
                    running_components += 1

            if consumer_dirty:
                consumer_state.current_consumption = consumer_consumption

                if running_components == 0:
                    consumer_state.status = ConsumerStatus.STOPPED
                elif running_components == len(consumer_components):
                    consumer_state.status = ConsumerStatus.STOPPED
                elif running_components <= len(consumer_components):
                    consumer_state.status = ConsumerStatus.PARTIAL_RUNNING

                await consumer_state.save()

                logger.info(
                    f"Updated consumer {consumer.id}! Status={consumer_state.status}; Consumption={consumer_state.current_consumption}"
                )
