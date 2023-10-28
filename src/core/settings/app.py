from functools import lru_cache

from pydantic import BaseModel
from pydantic_settings import BaseSettings


class MariaDBSettings(BaseModel):
    URI: str = "mysql://helios:Helios_2001!@127.0.0.1:3306/helios"


class AppSettings(BaseSettings):
    APP_TITLE: str = "helios"
    APP_DESCRIPTION: str = "Helios Automation and Monitoring"
    APP_VERSION: str = "1.0"

    MARIA_DB: MariaDBSettings = MariaDBSettings()


@lru_cache(maxsize=1)
def get_app_settings() -> AppSettings:
    return AppSettings()
