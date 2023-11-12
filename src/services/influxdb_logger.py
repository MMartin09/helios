from typing import Any, Dict

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from src.consumer.models import ConsumerComponent
from src.core.settings.app import AppSettings
from src.dto.powerflow import DataMeter, DataPowerflow


class InfluxDBLogger:
    """Service class to log data in InfluxDB.

    TODO: Implement error handling for the data logging

    Args:
        app_settings: AppSettings object to initialize the InfluxDBClient.

    """

    BUCKET_MAPPING = {
        "powerflow": "helios_powerflow",
        "meter": "helios_powerflow",
        "sma": "helios_powerflow",
        "state_transition": "helios_consumer_logs",
    }

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
        measurement = "powerflow"
        fields = data.model_dump()
        self._log_data(measurement, fields)

    def log_current_meter_data(self, data: DataMeter) -> None:
        """Log the current meter data.

        Args:
            data: DataMeter object containing the current data.

        """
        measurement = "meter"
        fields = data.model_dump()
        self._log_data(measurement, fields)

    def log_current_sma_value(self, sma: float) -> None:
        """Log the current SMA value.

        Args:
            sma: Current SMA value.

        """
        measurement = "sma"
        fields = {"sma": sma}
        self._log_data(measurement, fields)

    def log_component_state_transition(
        self,
        component: ConsumerComponent,
        consumer_id: int,
        old_state: bool,
        new_state: bool,
    ) -> None:
        """Log the state transition of a component.

        Args:
            component: Target component.
            consumer_id: Id of the related consumer.
            old_state: Old output state.
            new_state: New input state.

        """
        measurement = "state_transition"
        transition_type = self._determine_component_transition_type(
            old_state, new_state
        )
        tags = {
            "transition_entity": "component",
            "consumer": consumer_id,
            "component": component.id,
        }
        fields = {"transition_type": transition_type}
        self._log_data(measurement=measurement, fields=fields, tags=tags)

    def _log_data(
        self,
        measurement: str,
        fields: Dict[str, Any],
        tags: Dict[str, Any] | None = None,
    ) -> None:
        """Log data into InfluxDB.

        Args:
            measurement: Measurement name
            fields: Fields to add to the record.

        """
        bucket = self.BUCKET_MAPPING[measurement]
        record = self._generate_record(
            measurement=measurement, fields=fields, tags=tags
        )
        self._write_data(bucket, record)

    def _generate_record(
        self,
        measurement: str,
        fields: Dict[str, Any],
        tags: Dict[str, Any] | None = None,
    ) -> Point:
        """Generate a InfluxDB data point.

        Args:
            measurement: Measurement name
            fields: Fields to add to the record.
            tags: Optional. Set of tags added to the measurement.

        Returns:
            An InfluxDB data point.

        """
        return Point.from_dict(
            {"measurement": measurement, "fields": fields, "tags": tags or {}}
        )

    def _write_data(self, bucket: str, record: Point) -> None:
        """Write a data point into an InfluxDB bucket.

        TODO: Error handling

        Args:
            bucket: Target bucket.
            record: Data point to write.

        """
        self._write_api.write(bucket, record=record)

    def _determine_component_transition_type(
        self, old_state: bool, new_state: bool
    ) -> str:
        """Determine the transition type of consumer component

        TODO: Not really happy with this solution.

        Args:
            old_state: Old output state.
            new_state: New input state.

        Returns:
            Transition type of the component. E.g., on_to_off.

        """
        old_state_str = "on" if old_state else "off"
        new_state_str = "on" if new_state else "off"

        return f"{old_state_str}_to_{new_state_str}"
