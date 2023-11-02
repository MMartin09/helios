from functools import lru_cache

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS, WriteApi

from src.core.settings.app import get_app_settings


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
