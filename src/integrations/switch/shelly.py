import logging
from typing import Any, Dict

import httpx
from loguru import logger
from tenacity import RetryError, after_log, retry, stop_after_attempt, wait_fixed

from src.consumer.models import ConsumerComponent
from src.integrations.switch.switch import BaseSwitch


class ShellySwitch(BaseSwitch):
    """Integration for Shelly switches.

    The integration supports only "Gen 2" devices.

    TODO: Implement error handling
    TODO: Implement a base class for switches

    """

    def __init__(self) -> None:
        ...

    async def switch_on(self, component: ConsumerComponent) -> None:
        await self._switch_output(component, on=True)

    async def switch_off(self, component: ConsumerComponent) -> None:
        await self._switch_output(component, on=False)

    async def get_switch_status(self, component: ConsumerComponent) -> bool:
        try:
            response = await self._send_request(component, method="Switch.GetStatus")
            return response["output"]
        except RetryError:
            # TODO: What should happen here...
            return False

    async def _switch_output(self, component: ConsumerComponent, on: bool) -> None:
        """Generic function to switch the output channel to the target state.

        Args:
            component: Target component.
            on: New output state.

        """
        await self._send_request(component, method="Switch.Set", params={"on": on})

    @staticmethod
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(5),
        after=after_log(logger, logging.ERROR),
    )
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
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
