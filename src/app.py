from fastapi import FastAPI
from starlette.responses import RedirectResponse

from src.core.api_router import api_router
from src.core.application.lifespan import service_lifespan
from src.core.application.utils import build_app_configuration
from src.core.settings.api import get_api_settings
from src.core.settings.app import get_app_settings


def get_app() -> FastAPI:
    app_settings = get_app_settings()
    api_settings = get_api_settings()
    app_configuration = build_app_configuration(app_settings)

    app = FastAPI(lifespan=service_lifespan, **app_configuration)

    @app.get("/", include_in_schema=False)
    def get_main() -> RedirectResponse:
        return RedirectResponse(api_settings.OPENAPI_ROUTE)

    app.include_router(api_router, prefix=api_settings.API_PREFIX)

    return app


app = get_app()
