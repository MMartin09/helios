import asyncio

from tortoise import Tortoise

from src.consumer.models import Component, Consumer, State
from src.core.settings.app import get_app_settings


async def main():
    app_settings = get_app_settings()

    models = [
        "src.consumer.models",
    ]

    await Tortoise.init(db_url=app_settings.MARIA_DB.URI, modules={"models": models})
    await Tortoise.generate_schemas()

    heating_rod = await Consumer.create(id="4855199C3C38", name="Heating-Rod")

    _ = await Component.create(name="Component_1", consumer=heating_rod)
    _ = await Component.create(name="Component_2", consumer=heating_rod)

    _ = await State.create(consumer=heating_rod)


if __name__ == "__main__":
    asyncio.run(main())
