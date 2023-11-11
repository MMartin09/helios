from typing import Any

from fastapi import APIRouter, Request
from loguru import logger

from src.core.dependencies import get_influxdb_logger
from src.services.powerflow import powerflow_service
from src.utils.fronius_data_parser import FroniusDataParser

router = APIRouter(tags=["current_data"])


@router.post("/powerflow")
async def powerflow(request: Request) -> Any:
    request_data = await request.json()

    current_data = FroniusDataParser().parse_powerflow(request_data)
    logger.info(f"Current Powerflow data: {current_data.model_dump()}")

    await powerflow_service.update(current_data.p_grid)

    influxdb_logger = get_influxdb_logger()
    influxdb_logger.log_current_powerflow_data(current_data)

    return {"status": "ok"}


@router.post("/meter")
async def meter(request: Request) -> Any:
    request_data = await request.json()
    current_data = FroniusDataParser().parse_meter(request_data)

    logger.info(f"Current Meter data: {current_data.model_dump()}")

    influxdb_logger = get_influxdb_logger()
    influxdb_logger.log_current_meter_data(current_data)

    return {"status": "ok"}


@router.get("/temperature")
async def temperature(switch: str, temperature: float) -> Any:
    logger.debug(f"Current temperature data: {temperature}")
    return {"status": "ok"}
