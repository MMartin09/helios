from typing import Any, Dict

import httpx
from loguru import logger

from src.consumer.models import ConsumerComponent


class ShellySwitch:
    """Integration for Shelly switches.

    The integration supports only "Gen 2" devices.

    TODO: Implement error handling
    TODO: Implement a base class for switches

    """

    def __init__(self) -> None:
        ...

    async def switch_on(self, component: ConsumerComponent) -> None:
        """Switch the output channel on.

        Args:
            component: Target component.

        """
        await self._switch_output(component, on=True)

    async def switch_off(self, component: ConsumerComponent) -> None:
        """Switch the output channel off.

        Args:
            component: Target component.

        """
        await self._switch_output(component, on=False)

    async def get_switch_status(self, component: ConsumerComponent) -> bool:
        """Get the current status of the output channel.

        False means the output channel is switched off.
        True means the output channel is switched on.

        Args:
            component: Target component.

        Returns:
            Current state of the output channel.

        """
        response = await self._send_request(component, method="Switch.GetStatus")
        return response["output"]

    async def _switch_output(self, component: ConsumerComponent, on: bool) -> None:
        """Generic function to switch the output channel to the target state.

        Args:
            component: Target component.
            on: New output state.

        """
        await self._send_request(component, method="Switch.Set", params={"on": on})

    @staticmethod
    async def _send_request(
        component: ConsumerComponent, method: str, params: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:
        """Send a request to a Shelly switch.

        Args:
            component: Target component.
            method: Method to execute (e.g., Switch.Set to set the output channel)
            params: Additional parameters supplied in the payload of the request.

        Returns:
            The response of the request.

        """
        url = f"http://{component.ip}/rpc/{method}"
        params = {"id": component.relais, **(params or {})}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()

                return response.json()
            except httpx.HTTPError as err:
                logger.error(err)
