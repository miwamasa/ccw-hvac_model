"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any


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
    model_config = ConfigDict(extra='allow')  # Allow extra fields from pandas DataFrame

    month: int
    outdoor_temp: float
    indoor_temp: float
    occupancy: int
    occupancy_rate: float
    load_wall_kW: float
    load_window_kW: float
    load_solar_kW: float
    load_lighting_kW: float
    load_oa_equipment_kW: float
    load_person_sensible_kW: float
    load_person_latent_kW: float
    load_outdoor_air_latent_kW: float
    sensible_load_kW: float
    latent_load_kW: float
    total_load_kW: float
    shf: float
    central_ahu_fan_kWh: float
    central_chiller_kWh: float
    central_total_kWh: float
    local_fan_kWh: float
    local_compressor_kWh: float
    local_total_kWh: float
    lighting_kWh: float
    oa_equipment_kWh: float
    outdoor_enthalpy: float
    indoor_enthalpy: float


class SimulationResponse(BaseModel):
    results: List[dict]  # Use dict to handle any DataFrame columns
    summary: dict


class PresetResponse(BaseModel):
    name: str
    description: str
    floor_spec: FloorSpecSchema
    equipment_spec: EquipmentSpecSchema
    monthly_conditions: List[MonthlyConditionSchema]


class ConfigSaveRequest(BaseModel):
    name: str
    description: str
    floor_spec: FloorSpecSchema
    equipment_spec: EquipmentSpecSchema
    monthly_conditions: List[MonthlyConditionSchema]


class ActualDataSchema(BaseModel):
    """Actual monthly energy consumption data"""
    month: int
    central_total_kWh: Optional[float] = None
    local_total_kWh: Optional[float] = None
    total_kWh: Optional[float] = None


class ComparisonMetrics(BaseModel):
    """Metrics for comparing simulation vs actual data"""
    rmse: float  # Root Mean Square Error
    mae: float  # Mean Absolute Error
    mape: float  # Mean Absolute Percentage Error
    r_squared: float  # Coefficient of determination
    max_error: float  # Maximum absolute error
    max_error_month: int  # Month with maximum error


class ComparisonRequest(BaseModel):
    """Request to compare simulation with actual data"""
    floor_spec: FloorSpecSchema
    equipment_spec: EquipmentSpecSchema
    monthly_conditions: List[MonthlyConditionSchema]
    actual_data: List[ActualDataSchema]
    comparison_target: str = "total_kWh"  # central_total_kWh, local_total_kWh, or total_kWh


class ComparisonResponse(BaseModel):
    """Response with comparison results"""
    simulation_results: List[dict]
    actual_data: List[ActualDataSchema]
    metrics: ComparisonMetrics
    comparison_target: str


class ParameterRange(BaseModel):
    """Range specification for a parameter to calibrate"""
    parameter_name: str  # e.g., "floor_spec.wall_u_value"
    min_value: float
    max_value: float
    step: Optional[float] = None  # For grid search
    num_steps: int = 10  # Number of steps for grid search


class CalibrationRequest(BaseModel):
    """Request for parameter calibration"""
    floor_spec: FloorSpecSchema
    equipment_spec: EquipmentSpecSchema
    monthly_conditions: List[MonthlyConditionSchema]
    actual_data: List[ActualDataSchema]
    comparison_target: str = "total_kWh"
    parameter_ranges: List[ParameterRange]
    method: str = "grid"  # "grid" for survey, "optimize" for statistical


class CalibrationResult(BaseModel):
    """Single calibration result"""
    parameters: dict
    metrics: ComparisonMetrics
    simulation_results: Optional[List[dict]] = None


class CalibrationResponse(BaseModel):
    """Response with calibration results"""
    best_result: CalibrationResult
    all_results: List[CalibrationResult]
    method: str
    iterations: int
