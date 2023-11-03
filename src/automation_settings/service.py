from typing import Dict

from src.automation_settings import models
from src.core.settings.automation import AutomationSettings, get_automation_settings


class AutomationSettingsService:
    def __init__(self) -> None:
        self._automation_settings = get_automation_settings()

    def get_settings(self) -> AutomationSettings:
        return self._automation_settings

    async def update_settings(self, updated_settings: Dict[str, str]) -> None:
        for key, value in updated_settings.items():
            # Update value in Pydantic settings object
            setattr(self._automation_settings, key, value)
            # Update value in DB
            await models.AutomationSettings.filter(key=key).update(value=value)


def get_automation_settings_service() -> AutomationSettingsService:
    return AutomationSettingsService()
