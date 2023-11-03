from typing import Any

from fastapi import APIRouter, Depends

from src.automation_settings.service import (
    AutomationSettingsService,
    get_automation_settings_service,
)
from src.core.settings.automation import AutomationSettings

router = APIRouter(tags=["settings"])


@router.get("/")
async def get_settings(
    ass: AutomationSettingsService = Depends(get_automation_settings_service)
) -> Any:
    return ass.get_settings()


@router.patch("/")
async def update_settings(
    settings: AutomationSettings,
    ass: AutomationSettingsService = Depends(get_automation_settings_service),
) -> Any:
    updated_settings = settings.model_dump(exclude_unset=True)
    await ass.update_settings(updated_settings)

    return {"Hello": "world"}
