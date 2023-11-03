import asyncio

from tortoise import Tortoise

from src.consumer.models import (
    Consumer,
    ConsumerComponent,
    ConsumerState,
)
from src.core.definitions import ConsumerMode, ConsumerStatus
from src.core.settings.app import get_app_settings


async def main():
    app_settings = get_app_settings()

    models = [
        "src.automation_settings.models",
        "src.consumer.models",
    ]

    await Tortoise.init(db_url=app_settings.MARIA_DB.URI, modules={"models": models})
    await Tortoise.generate_schemas()

    heating_rod = await Consumer.create(name="Heating-Rod", priority=1)

    _ = await ConsumerComponent.create(
        name="Component_1",
        consumption=500,
        ip="192.168.0.103",
        relais=0,
        consumer=heating_rod,
        running=False,
    )
    _ = await ConsumerComponent.create(
        name="Component_2",
        consumption=1000,
        ip="192.168.0.103",
        relais=1,
        consumer=heating_rod,
        running=False,
    )

    _ = await ConsumerState.create(
        consumer=heating_rod,
        mode=ConsumerMode.AUTOMATIC,
        status=ConsumerStatus.STOPPED,
        current_conmsuption=0,
    )

    # consumer_1 = await Consumer.create(name="1111")
    # consumer_2 = await Consumer.create(name="2222", priority=2)
    # consumer_3 = await Consumer.create(name="3333", priority=3)

    # await ConsumerComponent.create(
    #    name="1111_component1", consumption=800, ip="...", relais=0, consumer=consumer_1, running=True
    # )
    # await ConsumerComponent.create(
    #    name="2222_component1", consumption=600, ip="...", relais=0, consumer=consumer_2
    # )
    # await ConsumerComponent.create(
    #    name="2222_component2", consumption=800, ip="...", relais=1, consumer=consumer_2, running=True
    # )
    # await ConsumerComponent.create(
    #    name="2222_component3", consumption=700, ip="...", relais=1, consumer=consumer_2, running=True
    # )
    # await ConsumerComponent.create(
    #    name="3333_component1",
    #    consumption=1000,
    #    ip="...",
    #    relais=0,
    #    consumer=consumer_3,
    # )

    # await ConsumerState.create(
    #    consumer=consumer_1, mode=ConsumerMode.AUTOMATIC, status=ConsumerStatus.RUNNING
    # )
    # await ConsumerState.create(consumer=consumer_2, mode=ConsumerMode.AUTOMATIC, status=ConsumerStatus.PARTIAL_RUNNING)
    # await ConsumerState.create(consumer=consumer_3, mode=ConsumerMode.AUTOMATIC)


if __name__ == "__main__":
    asyncio.run(main())
