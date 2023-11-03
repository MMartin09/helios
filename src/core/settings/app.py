from functools import lru_cache

from pydantic import BaseModel
from pydantic_settings import BaseSettings


class MariaDBSettings(BaseModel):
    URI: str = "mysql://helios:Helios_2001!@127.0.0.1:3306/helios"


class InfluxDBSettings(BaseSettings):
    URI: str = "http://127.0.0.1:8086"
    TOKEN: str = "v8Uv7peMjQyp4a5zjDtpES03eEfcONuWn4TZoF1r-ww1A4qHe9HimAA7BMYPc28GXkbbmJdtBLKM2f7o-yTCqw=="
    ORG: str = "helios"


class AppSettings(BaseSettings):
    APP_TITLE: str = "helios"
    APP_DESCRIPTION: str = "Helios Automation and Monitoring"
    APP_VERSION: str = "0.1"

    MARIA_DB: MariaDBSettings = MariaDBSettings()
    INFLUX_DB: InfluxDBSettings = InfluxDBSettings()


@lru_cache(maxsize=1)
def get_app_settings() -> AppSettings:
    return AppSettings()
