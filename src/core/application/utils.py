from typing import Any, Dict

from src.core.settings.app import AppSettings


def build_app_configuration(app_settings: AppSettings) -> Dict[str, Any]:
    """Generate FastAPI configuration object.

    Extract the target configuration from the APPSettings and map them into a FasAPI compatible configuration object.

    The target fields are:
        - title
        - description
        - version

    In the AppSettings those fields have to be named after the pattern `APP_<field>`.

    Args:
        app_settings: AppSettings object.

    Returns:
        FastAPI configuration object.
    """

    fields = ["title", "description", "version"]

    config = {key: getattr(app_settings, f"APP_{key.upper()}") for key in fields}
    return config
