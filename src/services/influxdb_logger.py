from typing import Any, Dict

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from src.core.settings.app import AppSettings
from src.dto.powerflow import DataMeter, DataPowerflow


class InfluxDBLogger:
    """Service class to log data in InfluxDB.

    Args:
        app_settings: AppSettings object to initialize the InfluxDBClient.

    """

    def __init__(self, app_settings: AppSettings) -> None:
        self._client = InfluxDBClient(
            url=app_settings.INFLUX_DB.URI,
            token=app_settings.INFLUX_DB.TOKEN,
            org=app_settings.INFLUX_DB.ORG,
        )
        self._write_api = self._client.write_api(write_options=SYNCHRONOUS)

    def log_current_powerflow_data(self, data: DataPowerflow) -> None:
        """Log the current powerflow data.

        Args:
            data: DataPowerflow object containing the current data.

        """
        bucket = "helios_powerflow"

        measurement = "powerflow"
        fields = data.model_dump()
        self._log_data(bucket, measurement, fields)

    def log_current_meter_data(self, data: DataMeter) -> None:
        """Log the current meter data.

        Args:
            data: DataMeter object containing the current data.

        """
        bucket = "helios_powerflow"

        measurement = "meter"
        fields = data.model_dump()
        self._log_data(bucket, measurement, fields)

    def _log_data(self, bucket: str, measurement: str, fields: Dict[str, Any]) -> None:
        record = self._generate_record(measurement, fields)
        self._write_data(bucket, record)

    def _generate_record(self, measurement: str, fields: Dict[str, Any]) -> Point:
        return Point.from_dict({"measurement": measurement, "fields": fields})

    def _write_data(self, bucket: str, record: Point) -> None:
        # TODO: Error handling
        self._write_api.write(bucket, record=record)
