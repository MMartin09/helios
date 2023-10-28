from functools import lru_cache

from pydantic_settings import BaseSettings


class ApiSettings(BaseSettings):
    OPENAPI_ROUTE: str = "/docs"
    API_PREFIX: str = "/api"


@lru_cache(maxsize=1)
def get_api_settings() -> ApiSettings:
    return ApiSettings()
