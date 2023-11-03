from pydantic import BaseModel


class AutomationSettings(BaseModel):
    """Configuration for the consumer automation.

    Note: As these settings should be able to be changed dynamically the class does not extend `BaseSettings`.

    """

    WINDOW_TIME: int = 5
    CONSUME_THRESHOLD: int = 200


automation_settings = AutomationSettings()


def get_automation_settings() -> AutomationSettings:
    return automation_settings
