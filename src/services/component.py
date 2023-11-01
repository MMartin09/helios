import httpx
from loguru import logger

from src.consumer.models import ConsumerComponent


class ComponentService:
    """Consumer Component Service.

    TODO: The service has to check the type of the component (e.g., Shelly Switch) and call the correc functions.

    """

    async def start_component(self, component: ConsumerComponent) -> None:
        if component.running:
            logger.info(
                f"Request to start component {component.id} but component is already running"
            )

        self._switch_shelly_switch(ip=component.ip, relais=component.relais, on=True)

        component.running = True
        await component.save()

    async def stop_component(self, component: ConsumerComponent) -> None:
        if not component.running:
            logger.info(
                f"Request to stop component {component.id} but component is already stopped"
            )

        self._switch_shelly_switch(ip=component.ip, relais=component.relais, on=False)

        component.running = False
        await component.save()

    def _switch_shelly_switch(self, ip: str, relais: int, on: bool) -> None:
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
        except httpx.HTTPError as e:
            # TODO: Maybe this should be sent as an error message using PushOver
            # TODO: Maybe it would be better to print the component id instead of the ip
            logger.error(f"Error switching state of device {ip} to status {on}: {e}")
