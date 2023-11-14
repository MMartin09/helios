from abc import ABC, abstractmethod

from src.consumer.models import ConsumerComponent


class BaseSwitch(ABC):
    """Base class for the integration of switches."""

    @abstractmethod
    async def switch_on(self, component: ConsumerComponent) -> None:
        """Switch the output channel on.

        Args:
            component: Target component.

        """
        ...

    @abstractmethod
    async def switch_off(self, component: ConsumerComponent) -> None:
        """Switch the output channel off.

        Args:
            component: Target component.

        """
        ...

    @abstractmethod
    async def get_switch_status(self, component: ConsumerComponent) -> bool:
        """Get the current status of the output channel.

        False means the output channel is switched off.
        True means the output channel is switched on.

        TODO: Maybe add an enum for on and off

        Args:
            component: Target component.

        Returns:
            Current state of the output channel.

        """
        ...
