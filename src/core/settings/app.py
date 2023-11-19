from functools import lru_cache

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class MariaDBSettings(BaseModel):
    URI: str


class InfluxDBSettings(BaseModel):
    URI: str
    TOKEN: str
    ORG: str


class AppSettings(BaseSettings):
    APP_TITLE: str = "helios"
    APP_DESCRIPTION: str = "Helios Automation and Monitoring"
    APP_VERSION: str = "0.1"

    MARIA_DB: MariaDBSettings
    INFLUX_DB: InfluxDBSettings

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_nested_delimiter="__"
    )


@lru_cache(maxsize=1)
def get_app_settings() -> AppSettings:
    return AppSettings()
