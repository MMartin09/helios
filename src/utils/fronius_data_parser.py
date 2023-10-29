from typing import Any, Dict

from src.dto.powerflow import DataMeter, DataPowerflow


class FroniusDataParser:
    """
    TODO: Create an abstract base class "BaseDataParser" to prepare the implementation of other brands.
    """

    @staticmethod
    def parse_powerflow(request_data: Dict[str, Any]) -> DataPowerflow:
        request_body = request_data["Body"]
        site_data = request_body["Site"]

        return DataPowerflow(p_pv=site_data["P_PV"], p_grid=site_data["P_Grid"])

    @staticmethod
    def parse_meter(request_data: Dict[str, Any]) -> DataMeter:
        request_body = request_data["Body"]

        # TODO: The 1 should be replaced with a field representing the ID of the meter
        meter_data = request_body["1"]

        return DataMeter(
            energy_plus=meter_data["EnergyReal_WAC_Plus_Absolute"],
            energy_minus=meter_data["EnergyReal_WAC_Minus_Absolute"],
            energy_consumed=meter_data["EnergyReal_WAC_Sum_Consumed"],
            energy_produced=meter_data["EnergyReal_WAC_Sum_Produced"],
        )
