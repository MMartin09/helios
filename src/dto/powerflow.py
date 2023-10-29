from pydantic import BaseModel, field_validator


class DataPowerflow(BaseModel):
    """Powerflow Data structure."""

    p_pv: float
    p_grid: float

    @field_validator("p_pv", mode="before")
    def p_pv_default_value(cls, v: float | None) -> float:
        return v or 0.0


class DataMeter(BaseModel):
    """Smartmeter Data structure."""

    energy_plus: float
    energy_minus: float
    energy_consumed: float
    energy_produced: float
