from src.consumer.models import ConsumerComponent
from src.integrations.switch.base import BaseSwitch
from src.integrations.switch.shelly import ShellySwitch


class Switch(BaseSwitch):
    """Factory class used to encapsulate the concrete switch type.

    Use this class wherever it is required to interact with a switch.
    The classes check the type of the passed in component and calls the correct integration.

    """

    def __init__(self) -> None:
        self._shelly_switch = ShellySwitch()

    async def switch_on(self, component: ConsumerComponent) -> None:
        # TODO: Check Type
        await self._shelly_switch.switch_on(component)

    async def switch_off(self, component: ConsumerComponent) -> None:
        # TODO: Check Type
        await self._shelly_switch.switch_off(component)

    async def get_switch_status(self, component: ConsumerComponent) -> bool:
        # TODO: Check Type
        return await self._shelly_switch.get_switch_status(component)
