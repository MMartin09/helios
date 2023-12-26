from contextlib import AsyncExitStack, asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from tortoise import Tortoise, connections

from src.automation_settings.service import get_automation_settings_service
from src.consumer.services.consumer import ConsumerManager
from src.core.application.scheduler import scheduler_context
from src.core.settings.app import get_app_settings


async def init_orm(db_url: str) -> None:
    models = [
        "src.automation_settings.models",
        "src.consumer.models",
    ]

    Tortoise.init_models(models, "models")
    await Tortoise.init(db_url=db_url, modules={"models": models})


async def init_automation_settings() -> None:
    ass = get_automation_settings_service()
    await ass.add_missing_settings_to_the_database()
    await ass.load_from_db()


@asynccontextmanager
async def service_lifespan(app: FastAPI) -> AsyncIterator[None]:
    app_settings = get_app_settings()
    await init_orm(app_settings.MARIA_DB.URI)
    await init_automation_settings()

    # TODO: Not really good here. But for now its ok.
    _consumer_manager = ConsumerManager()
    await _consumer_manager.synchronize_status_with_db()

    async with AsyncExitStack() as stack:
        await stack.enter_async_context(scheduler_context())
        yield
        await connections.close_all()  # Close TortoiseORM connection
