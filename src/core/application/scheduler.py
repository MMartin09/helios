from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from influxdb_client import QueryApi

from src.core.dependencies import get_influxdb_query_api
from src.utils.influxdb_queries.fronius_smart_meter import (
    get_first_measurements_of_date,
)

scheduler = AsyncIOScheduler()


def scheduler_function():
    query_api: QueryApi = get_influxdb_query_api()

    bucket = "helios_powerflow"
    fields = ["energy_consumed", "energy_produced", "energy_minus", "energy_plus"]

    data = get_first_measurements_of_date(
        query_client=query_api, bucket=bucket, fields=fields, day="2023-12-25"
    )
    print(data)


@asynccontextmanager
async def scheduler_context():
    try:
        print("STARTING THE SCHEDULER")
        scheduler.add_job(scheduler_function, "interval", minutes=1)
        scheduler.start()
        yield
    finally:
        print("SHUTTING DOWN THE SCHEDULER")
        scheduler.shutdown()
