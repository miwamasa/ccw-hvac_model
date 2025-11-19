"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel
from typing import List, Optional


class FloorSpecSchema(BaseModel):
    floor_area: float
    ceiling_height: float
    wall_u_value: float
    window_area: float
    window_u_value: float
    solar_heat_gain_coef: float


class EquipmentSpecSchema(BaseModel):
    lighting_power_density: float
    oa_equipment_power_density: float
    central_ahu_capacity: float
    central_ahu_fan_power: float
    central_chiller_capacity: float
    central_chiller_cop: float
    local_ac_capacity: float
    local_ac_cop: float
    local_ac_fan_power: float


class MonthlyConditionSchema(BaseModel):
    month: int
    outdoor_temp: float
    outdoor_humidity: float
    indoor_temp_setpoint: float
    indoor_humidity_setpoint: float
    supply_air_temp: float
    occupancy: int
    occupancy_rate: float
    operation_hours: float


class SimulationRequest(BaseModel):
    floor_spec: FloorSpecSchema
    equipment_spec: EquipmentSpecSchema
    monthly_conditions: List[MonthlyConditionSchema]


class SimulationResult(BaseModel):
    month: int
    outdoor_temp: float
    indoor_temp: float
    outdoor_humidity: float
    indoor_humidity: float
    supply_air_temp: float
    occupancy: int
    office_usage_rate: float
    operating_hours: float
    solar_radiation: float
    sensible_wall_kW: float
    sensible_window_kW: float
    sensible_solar_kW: float
    sensible_lighting_kW: float
    sensible_oa_equipment_kW: float
    sensible_person_kW: float
    latent_person_kW: float
    latent_outdoor_air_kW: float
    total_sensible_kW: float
    total_latent_kW: float
    total_load_kW: float
    central_fan_kWh: float
    central_chiller_kWh: float
    central_total_kWh: float
    local_fan_kWh: float
    local_compressor_kWh: float
    local_total_kWh: float


class SimulationResponse(BaseModel):
    results: List[SimulationResult]
    summary: dict


class PresetResponse(BaseModel):
    name: str
    description: str
    floor_spec: FloorSpecSchema
    equipment_spec: EquipmentSpecSchema
    monthly_conditions: List[MonthlyConditionSchema]
