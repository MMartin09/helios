from datetime import datetime

from pydantic import BaseModel


class SmartMeterMeasurement(BaseModel):
    """Smart meter measurement structure."""

    field: str
    time: datetime
    value: float
