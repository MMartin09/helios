from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from influxdb_client import InfluxDBClient, QueryApi
from influxdb_client.client.write_api import SYNCHRONOUS, WriteApi

from src.consumer.repository import ConsumerComponentRepository, ConsumerRepository
from src.core.settings.app import get_app_settings
from src.services.influxdb_logger import InfluxDBLogger


@lru_cache(maxsize=1)
def get_influxdb_client() -> InfluxDBClient:
    app_settings = get_app_settings()
    return InfluxDBClient(
        url=app_settings.INFLUX_DB.URI,
        token=app_settings.INFLUX_DB.TOKEN,
        org=app_settings.INFLUX_DB.ORG,
    )


@lru_cache(maxsize=1)
def get_influxdb_write_api() -> WriteApi:
    return get_influxdb_client().write_api(write_options=SYNCHRONOUS)


@lru_cache(maxsize=1)
def get_influxdb_query_api() -> QueryApi:
    return get_influxdb_client().query_api()


@lru_cache(maxsize=1)
def get_influxdb_logger() -> InfluxDBLogger:
    app_settings = get_app_settings()
    return InfluxDBLogger(app_settings)


def get_consumer_repository() -> ConsumerRepository:
    return ConsumerRepository()


def get_consumer_component_repository() -> ConsumerComponentRepository:
    return ConsumerComponentRepository()


ConsumerRepositoryDep = Annotated[ConsumerRepository, Depends(ConsumerRepository)]
ConsumerComponentRepositoryDep = Annotated[
    ConsumerComponentRepository, Depends(ConsumerComponentRepository)
]
