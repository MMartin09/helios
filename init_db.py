import asyncio

from tortoise import Tortoise

from src.consumer.models import (
    Consumer,
    ConsumerComponent,
    ConsumerState,
)
from src.core.settings.app import get_app_settings


async def main():
    app_settings = get_app_settings()

    models = [
        "src.consumer.models",
    ]

    await Tortoise.init(db_url=app_settings.MARIA_DB.URI, modules={"models": models})
    await Tortoise.generate_schemas()

    heating_rod = await Consumer.create(id="4855199C3C38", name="Heating-Rod")

    _ = await ConsumerComponent.create(
        name="Component_1",
        consumption=500,
        ip="192.168.0.154",
        relais=0,
        consumer=heating_rod,
    )
    _ = await ConsumerComponent.create(
        name="Component_2",
        consumption=1000,
        ip="192.168.0.154",
        relais=1,
        consumer=heating_rod,
    )

    _ = await ConsumerState.create(consumer=heating_rod)


if __name__ == "__main__":
    asyncio.run(main())
