export interface FloorSpec {
  floor_area: number;
  ceiling_height: number;
  wall_u_value: number;
  window_area: number;
  window_u_value: number;
  shgc: number;
}

export interface EquipmentSpec {
  lighting_power_density: number;
  oa_equipment_power_density: number;
  central_ahu_capacity: number;
  central_fan_power: number;
  central_chiller_capacity: number;
  central_chiller_cop: number;
  local_ac_capacity: number;
  local_ac_cop: number;
  local_fan_power: number;
}

export interface MonthlyCondition {
  month: number;
  outdoor_temp: number;
  outdoor_humidity: number;
  indoor_temp: number;
  indoor_humidity: number;
  supply_air_temp: number;
  occupancy: number;
  office_usage_rate: number;
  operating_hours: number;
  solar_radiation: number;
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
  outdoor_humidity: number;
  indoor_humidity: number;
  supply_air_temp: number;
  occupancy: number;
  office_usage_rate: number;
  operating_hours: number;
  solar_radiation: number;
  sensible_wall_kW: number;
  sensible_window_kW: number;
  sensible_solar_kW: number;
  sensible_lighting_kW: number;
  sensible_oa_equipment_kW: number;
  sensible_person_kW: number;
  latent_person_kW: number;
  latent_outdoor_air_kW: number;
  total_sensible_kW: number;
  total_latent_kW: number;
  total_load_kW: number;
  central_fan_kWh: number;
  central_chiller_kWh: number;
  central_total_kWh: number;
  local_fan_kWh: number;
  local_compressor_kWh: number;
  local_total_kWh: number;
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
