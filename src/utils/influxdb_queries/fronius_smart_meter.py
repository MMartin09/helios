from datetime import datetime, timedelta
from typing import Dict, List

from influxdb_client import QueryApi

from src.dto.smart_meter import SmartMeterMeasurement


def get_first_measurements_of_date(
    query_client: QueryApi, bucket: str, fields: List[str], day: str
) -> Dict[str, SmartMeterMeasurement]:
    """Retrieves the first measurements for specified fields from a given bucket for a specific date.

    Args:
        query_client: An instance of the QueryApi to perform data queries in InfluxDB.
        bucket: The name of the bucket where the data is stored.
        fields: A list of field names for the measurements to be retrieved.
        day: The specific date (YYYY-MM-DD format) for the measurements to be retrieved.

    Returns:
        A dictionary of measurements with field names as keys. Each key maps to a `SmartMeterMeasurement` object containing the field name, time, and value of the measurement.

    """
    return _query_measurements(query_client, bucket, fields, day, "first")


def get_last_measurements_of_date(
    query_client: QueryApi, bucket: str, fields: List[str], day: str
) -> Dict[str, SmartMeterMeasurement]:
    """Retrieves the last measurements for specified fields from a given bucket for a specific date.

    Args:
        query_client: An instance of the QueryApi to perform data queries in InfluxDB.
        bucket: The name of the bucket where the data is stored.
        fields: A list of field names for the measurements to be retrieved.
        day: The specific date (YYYY-MM-DD format) for the measurements to be retrieved.

    Returns:
        A dictionary of measurements with field names as keys. Each key maps to a `SmartMeterMeasurement` object containing the field name, time, and value of the measurement.

    """
    return _query_measurements(query_client, bucket, fields, day, "last")


def _query_measurements(
    query_client: QueryApi, bucket: str, fields: List[str], day: str, first_or_last: str
) -> Dict[str, SmartMeterMeasurement]:
    day_obj = datetime.strptime(day, "%Y-%m-%d")
    next_day_obj = day_obj + timedelta(days=1)
    next_day = next_day_obj.strftime("%Y-%m-%d")

    # Construct the fields filter using the list of target fields
    fields_filter = " or ".join([f'r._field == "{field}"' for field in fields])

    query = f"""
        from (bucket: "{bucket}")
          |> range(start: {day}T00:00:00Z, stop: {next_day})
          |> filter(fn: (r) =>
            r._measurement == "meter" and
            ({fields_filter})
          )
          |> {first_or_last}()
        |> group(columns: ["_field"])
    """

    tables = query_client.query(query)
    measurements = {}

    for table in tables:
        for record in table.records:
            field = record.get_field()
            measurement = SmartMeterMeasurement(
                **{
                    "field": field,
                    "time": record.get_time(),
                    "value": record.get_value(),
                }
            )
            measurements[field] = measurement

    return measurements
