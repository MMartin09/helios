from typing import Dict

from loguru import logger

from src.automation_settings import models
from src.core.settings.automation import AutomationSettings, get_automation_settings


class AutomationSettingsService:
    """Service for the management of the AutomationSettings."""

    def __init__(self) -> None:
        self._automation_settings = get_automation_settings()

    def get_settings(self) -> AutomationSettings:
        """Get the current AutomationSettings.

        Returns:
            Current AutomationSettings.

        """
        return self._automation_settings

    async def update_settings(self, updated_settings: Dict[str, str]) -> None:
        """Update AutomationSettings value(s).

        Update the value of one or multiple keys in the AutomationSettings map.
        The change is directly applied to the local instance and updated in the database.

        Args:
            updated_settings: Dictionary of keys to update including the new value (<key>: <new_value>).

        """
        for key, value in updated_settings.items():
            # Update value in Pydantic settings object
            self._automation_settings = self._automation_settings.copy(
                update={key: value}
            )
            # Update value in DB
            await models.AutomationSettings.filter(key=key).update(value=value)

    async def load_from_db(self) -> None:
        """Load the AutomationSettings from the database.

        Load the AutomationSettings from the database and set the values in the local instance.

        """
        settings_db = await models.AutomationSettings.all()
        settings_dict = {setting.key: setting.value for setting in settings_db}
        for key, value in settings_dict.items():
            # Update value in Pydantic settings object
            self._automation_settings = self._automation_settings.copy(
                update={key: value}
            )

    async def add_missing_settings_to_the_database(self) -> None:
        """Add missing keys to the database.

        Check if all AutomationSettings keys are present in the database.
        If there is one missing it is added to the database with the default value.

        """
        # Get all keys that are available in the database
        settings_db = await models.AutomationSettings.all()
        db_keys = {setting.key for setting in settings_db}
        # Get all keys that are available in the local map
        model_fields_keys = set(self._automation_settings.model_fields)

        missing_keys = model_fields_keys - db_keys
        if not missing_keys:
            logger.debug("No key is missing in the database.")
            return

        for key in missing_keys:
            default_value = self._automation_settings.model_fields[key].default
            await models.AutomationSettings.create(key=key, value=default_value)
            logger.info(
                f"Key {key} was missing in the database and is created with default value {default_value}"
            )


def get_automation_settings_service() -> AutomationSettingsService:
    return AutomationSettingsService()
