import asyncio
from itertools import combinations

from tortoise import Tortoise
from tortoise.expressions import Q
from tortoise.query_utils import Prefetch

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
        "src.consumer.models",
    ]

    await Tortoise.init(db_url=app_settings.MARIA_DB.URI, modules={"models": models})
    await Tortoise.generate_schemas()

    await Consumer.all().prefetch_related("components")
    consumer = (
        await Consumer.filter(name="Heating-Rod").prefetch_related("components").first()
    )
    print(consumer.consumer_type())
    return
    # consumer_state = await consumer.state.first()
    # print(consumer_state.current_consumption)

    virtual_surplus = 800

    components = await consumer.components.all()

    best_surplus = float("inf")
    best_combination = None

    for r in range(1, len(components) + 1):
        for component_combination in combinations(components, r):
            print(list(component_combination))
            combination_consumption = sum(
                component.consumption for component in component_combination
            )
            new_surplus = virtual_surplus - combination_consumption
            print(component_combination, combination_consumption, new_surplus)

            if -250 <= new_surplus < best_surplus:
                best_surplus = new_surplus
                best_combination = component_combination

    print(f"BEST COMBINATION {best_combination}! NEW SURPLUS WILL BE: {best_surplus}")

    return

    heating_rod = await Consumer.create(name="Heating-Rod", priority=1)

    _ = await ConsumerComponent.create(
        name="Component_1",
        consumption=500,
        ip="192.168.0.103",
        relais=0,
        consumer=heating_rod,
    )
    _ = await ConsumerComponent.create(
        name="Component_2",
        consumption=1000,
        ip="192.168.0.103",
        relais=1,
        consumer=heating_rod,
    )

    _ = await ConsumerState.create(
        consumer=heating_rod, mode=ConsumerMode.AUTOMATIC, status=ConsumerStatus.RUNNING
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


async def query_sample():
    models = [
        "src.consumer.models",
    ]
    app_settings = get_app_settings()

    Tortoise.init_models(models, "models")
    await Tortoise.init(db_url=app_settings.MARIA_DB.URI, modules={"models": models})

    consumers = await Consumer.all().prefetch_related(
        Prefetch(
            "state",
            queryset=ConsumerState.filter(
                Q(mode=ConsumerMode.AUTOMATIC) & ~Q(status=ConsumerStatus.RUNNING)
            ),
        )
    )
    for consumer in consumers:
        print(consumer.name)


if __name__ == "__main__":
    asyncio.run(main())
    # asyncio.run(query_sample())
