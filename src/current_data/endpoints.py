from typing import Any

from fastapi import APIRouter, Request
from influxdb_client import Point
from loguru import logger

from src.core.dependencies import get_influxdb_write_api
from src.services.powerflow import powerflow_service
from src.utils.fronius_data_parser import FroniusDataParser

router = APIRouter(tags=["current_data"])


@router.post("/powerflow")
async def powerflow(request: Request) -> Any:
    request_data = await request.json()

    current_data = FroniusDataParser().parse_powerflow(request_data)
    logger.info(f"Current Powerflow data: {current_data.model_dump()}")

    await powerflow_service.update(current_data.p_grid)

    influxdb_write_api = get_influxdb_write_api()
    data_point = Point.from_dict(
        {"measurement": "powerflow", "fields": current_data.model_dump()}
    )
    influxdb_write_api.write(bucket="helios_powerflow", record=data_point)

    return {"status": "ok"}


@router.post("/meter")
async def meter(request: Request) -> Any:
    request_data = await request.json()
    current_data = FroniusDataParser().parse_meter(request_data)

    logger.info(f"Current Meter data: {current_data.model_dump()}")

    influxdb_write_api = get_influxdb_write_api()
    data_point = Point.from_dict(
        {"measurement": "meter", "fields": current_data.model_dump()}
    )
    influxdb_write_api.write(bucket="helios_powerflow", record=data_point)

    return {"status": "ok"}
