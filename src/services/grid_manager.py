from datetime import datetime, timedelta
from typing import List

from loguru import logger

from src.core.definitions import GridMode
from src.core.settings.automation import automation_settings


class GridManagerService:
    """Determine the current GridMode using the Simple Moving Average (SMA) of grid values.

    By utilizing the SMA over a specified `WINDOW_TIME`, this service smoothens short-term fluctuations in grid values.
    Directly relying on instantaneous grid values might lead to reactive mode switches, for example, if a brief cloud
    passes by and momentarily reduces PV production. Such a direct approach could cause the system to prematurely
    switch to the "consume" mode. By averaging out grid values using the SMA, we mitigate these rapid, temporary
    fluctuations, ensuring that mode transitions are more stable and reflective of broader trends.
    Decisions to switch modes are further refined by using a defined `THRESHOLD` which sets the switching level.
    """

    def __init__(self) -> None:
        self._grid_values: List = []
        self._grid_mode: GridMode = GridMode.NOT_SET

        self._window_time: timedelta = timedelta(
            minutes=automation_settings.WINDOW_TIME
        )
        self._threshold: int = automation_settings.CONSUME_THRESHOLD

    def update(self, p_grid: float) -> GridMode:
        """Update the service with a new grid value.

        Args:
            p_grid: Current grid value.

        Returns:
            The current GridMode.

        """
        now = datetime.now()
        self._grid_values.append((now, p_grid))
        self._prune_old_grid_values(now)

        sma = self._calc_sma()
        logger.debug(f"SMA Value: {sma}")
        self._grid_mode = self._determine_grid_mode(grid_value=sma)

        return self._grid_mode

    def get_current_grid_mode(self) -> GridMode:
        """Return the current GridMode.

        Returns:
            The current GridMode.

        """
        return self._grid_mode

    def _prune_old_grid_values(self, now: datetime) -> None:
        """Prune old grid values from the list.

        Prune grid values that are older than the current time minus the window time.
        Those values have to be removed to calculate the SMA correctly.

        Args:
            now: Current time.

        """
        cutoff_time = now - self._window_time
        self._grid_values = [
            (ts, value) for ts, value in self._grid_values if ts > cutoff_time
        ]

    def _calc_sma(self) -> float:
        """Calculate the current SMA value.

        Returns:
            The current SMA value.

        """
        sma = sum(val for _, val in self._grid_values) / len(self._grid_values)
        sma = round(sma, 2)
        return sma

    def _determine_grid_mode(self, grid_value: float) -> GridMode:
        """Determine the current GridMode.

        The current GridMode is determined using the current SMA and the 'switching' threshold.

        Args:
            grid_value: Current Grid value. (The SMA is used in this case)

        Returns:
            The current GridMode.

        """
        if grid_value < self._threshold:
            return GridMode.FEED_IN
        else:
            return GridMode.CONSUME


grid_manager_service = GridManagerService()
