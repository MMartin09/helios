import httpx
from loguru import logger

from src import integrations
from src.consumer.models import ConsumerComponent
from src.core.dependencies import get_influxdb_logger


class ComponentManager:
    """Consumer Component Manager.

    TODO: The service has to check the type of the component (e.g., Shelly Switch) and call the correct functions.
    TODO: Log the "switch" in InfluxDB

    """

    def __init__(self) -> None:
        self._influxdb_logger = get_influxdb_logger()
        self._shelly_switch_integration = integrations.ShellySwitch()

    async def start_component(self, component: ConsumerComponent) -> None:
        """Start a consumer component.

        Args:
            component: Target component.

        """
        await self._switch_component(component, on=True)

    async def stop_component(self, component: ConsumerComponent) -> None:
        """Stop a consumer component.

        Args:
            component: Target component.

        """
        await self._switch_component(component, on=False)

    async def _switch_component(self, component: ConsumerComponent, on: bool) -> None:
        """Switch a component to the target state.

        Args:
            component: Target component.
            on: Target output state.

        """
        if component.running == on:
            state = "running" if on else "stopped"
            logger.info(
                f"Request to {'start' if on else 'stop'} component {component.id} but component is already {state}"
            )
            return

        try:
            if on:
                await self._shelly_switch_integration.switch_on(component)
            else:
                await self._shelly_switch_integration.switch_off(component)
        except httpx.HTTPError:
            # TODO: Send error using PushOver
            # TODO: Add consumer id in log (makes it easier to read)
            logger.error(
                f"Error trying switching component {component.id} {'on' if on else 'off'}!"
            )
            return

        consumer = await component.consumer
        self._influxdb_logger.log_component_state_transition(
            component=component,
            consumer_id=consumer.id,
            old_state=component.running,
            new_state=on,
        )

        component.running = on
        await component.save()
