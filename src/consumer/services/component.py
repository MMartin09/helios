import httpx
from influxdb_client import Point, WriteApi
from loguru import logger

from src import integrations
from src.consumer.models import ConsumerComponent
from src.core.dependencies import get_influxdb_write_api


class ComponentManager:
    """Consumer Component Manager.

    TODO: The service has to check the type of the component (e.g., Shelly Switch) and call the correct functions.
    TODO: Log the "switch" in InfluxDB

    """

    def __init__(self) -> None:
        self._influxdb_write_api: WriteApi = get_influxdb_write_api()
        self.shelly_switch_integration = integrations.ShellySwitch()

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
                await self.shelly_switch_integration.switch_on(component)
            else:
                await self.shelly_switch_integration.switch_off(component)
        except httpx.HTTPError:
            # TODO: Send error using PushOver
            # TODO: Add consumer id in log (makes it easier to read)
            logger.error(
                f"Error trying switching component {component.id} {'on' if on else 'off'}!"
            )
            return

        # TODO: Move the logging into the InfluxDB Logger

        consumer = await component.consumer
        data_point = Point.from_dict(
            {
                "measurement": "state_transition",
                "tags": {"consumer": consumer.id, "component": component.id},
                "fields": {"old_state": component.running, "new_state": on},
            }
        )

        self._influxdb_write_api.write(bucket="helios_consumer_logs", record=data_point)

        component.running = on
        await component.save()
