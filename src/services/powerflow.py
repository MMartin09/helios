from loguru import logger

from src.core.definitions import GridMode
from src.services.grid_manager import grid_manager_service


class PowerflowService:
    def __init__(self) -> None:
        self._grid_manager_service = grid_manager_service
        self._grid_mode: GridMode = GridMode.NOT_SET

    def update(self, p_grid: float) -> None:
        """Update the service state with the current grid value.

        Args:
            p_grid: Current grid value.

        """

        self._update_grid_mode(p_grid)
        logger.info("Updated Grid Mode")

    def _update_grid_mode(self, p_grid) -> None:
        if new_grid_mode := self._grid_manager_service.update(p_grid):
            self._grid_mode = new_grid_mode


powerflow_service = PowerflowService()
