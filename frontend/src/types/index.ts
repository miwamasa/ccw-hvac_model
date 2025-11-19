export interface FloorSpec {
  floor_area: number;
  ceiling_height: number;
  wall_u_value: number;
  window_area: number;
  window_u_value: number;
  solar_heat_gain_coef: number;
}

export interface EquipmentSpec {
  lighting_power_density: number;
  oa_equipment_power_density: number;
  central_ahu_capacity: number;
  central_ahu_fan_power: number;
  central_chiller_capacity: number;
  central_chiller_cop: number;
  local_ac_capacity: number;
  local_ac_cop: number;
  local_ac_fan_power: number;
}

export interface MonthlyCondition {
  month: number;
  outdoor_temp: number;
  outdoor_humidity: number;
  indoor_temp_setpoint: number;
  indoor_humidity_setpoint: number;
  supply_air_temp: number;
  occupancy: number;
  occupancy_rate: number;
  operation_hours: number;
}

export interface SimulationRequest {
  floor_spec: FloorSpec;
  equipment_spec: EquipmentSpec;
  monthly_conditions: MonthlyCondition[];
}

export interface SimulationResult {
  month: number;
  outdoor_temp: number;
  indoor_temp: number;
  occupancy: number;
  occupancy_rate: number;
  load_wall_kW: number;
  load_window_kW: number;
  load_solar_kW: number;
  load_lighting_kW: number;
  load_oa_equipment_kW: number;
  load_person_sensible_kW: number;
  load_person_latent_kW: number;
  load_outdoor_air_latent_kW: number;
  sensible_load_kW: number;
  latent_load_kW: number;
  total_load_kW: number;
  shf: number;
  central_ahu_fan_kWh: number;
  central_chiller_kWh: number;
  central_total_kWh: number;
  local_fan_kWh: number;
  local_compressor_kWh: number;
  local_total_kWh: number;
  lighting_kWh: number;
  oa_equipment_kWh: number;
  outdoor_enthalpy: number;
  indoor_enthalpy: number;
}

export interface SimulationResponse {
  results: SimulationResult[];
  summary: {
    annual_central_total_kWh: number;
    annual_local_total_kWh: number;
    annual_total_load_kWh: number;
    average_monthly_load_kW: number;
  };
}

export interface PresetResponse {
  name: string;
  description: string;
  floor_spec: FloorSpec;
  equipment_spec: EquipmentSpec;
  monthly_conditions: MonthlyCondition[];
}

export interface PresetInfo {
  id: string;
  name: string;
  description: string;
}
