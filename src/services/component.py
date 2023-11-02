import httpx
from loguru import logger

from src.consumer.models import ConsumerComponent


class ComponentService:
    """Consumer Component Service.

    TODO: The service has to check the type of the component (e.g., Shelly Switch) and call the correct functions.
    TODO: Log the "switch" in InfluxDB

    """

    async def start_component(self, component: ConsumerComponent) -> None:
        await self._switch_component(component, on=True)

    async def stop_component(self, component: ConsumerComponent) -> None:
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
            self._switch_shelly_switch(ip=component.ip, relais=component.relais, on=on)
        except httpx.HTTPError:
            # TODO: Send error using PushOver
            logger.error(
                f"Error trying switching component {component.id} {'on' if on else 'off'}!"
            )
            return

        component.running = on
        await component.save()

    @staticmethod
    def _switch_shelly_switch(ip: str, relais: int, on: bool) -> None:
        """Switch the output state of a Shelly switch.

        Args:
            ip: IPv4-Address of the switch.
            relais: Relais number to switch.
            on: True to set the output to active. False otherwise.

        """
        payload = {"id": relais, "on": on}
        url = f"http://{ip}/rpc/Switch.Set"

        try:
            response = httpx.get(url, params=payload)
            response.raise_for_status()
        except httpx.HTTPError as err:
            logger.error(err)
