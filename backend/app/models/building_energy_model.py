"""
ビルエネルギーモデル - コアロジック
Building Energy Model - Core Logic

月単位でビルのエネルギー収支と室内環境を計算するモデル
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple
import json


@dataclass
class FloorSpec:
    """フロア仕様"""
    floor_area: float  # 床面積 [m²]
    ceiling_height: float  # 天井高 [m]
    wall_u_value: float  # 壁U値 [W/m²K]
    window_area: float  # 窓面積 [m²]
    window_u_value: float  # 窓U値 [W/m²K]
    solar_heat_gain_coef: float  # 日射熱取得係数 [-]
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


@dataclass
class EquipmentSpec:
    """設備仕様"""
    lighting_power_density: float  # 照明電力密度 [W/m²]
    oa_equipment_power_density: float  # OA機器電力密度 [W/m²]
    
    # 全館空調システム
    central_ahu_capacity: float  # 外調機能力 [kW]
    central_ahu_fan_power: float  # 外調機ファン動力 [kW]
    central_chiller_capacity: float  # 熱源容量 [kW]
    central_chiller_cop: float  # 熱源COP [-]
    
    # 個別空調システム
    local_ac_capacity: float  # 個別空調容量 [kW]
    local_ac_cop: float  # 個別空調COP [-]
    local_ac_fan_power: float  # 個別空調ファン動力 [kW]
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


@dataclass
class MonthlyCondition:
    """月別運用条件"""
    month: int
    outdoor_temp: float  # 外気温 [℃]
    outdoor_humidity: float  # 外気相対湿度 [%]
    indoor_temp_setpoint: float  # 室温設定 [℃]
    indoor_humidity_setpoint: float  # 室内湿度設定 [%]
    supply_air_temp: float  # 給気温度設定 [℃]
    occupancy: int  # 居住者数 [人]
    occupancy_rate: float  # オフィス利用率 [-]
    operation_hours: float  # 月間運転時間 [h]
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


class PsychrometricCalculator:
    """空気線図計算クラス"""
    
    @staticmethod
    def saturation_pressure(temp: float) -> float:
        """飽和水蒸気圧 [Pa] - Antoine式"""
        return 611 * np.exp(17.27 * temp / (temp + 237.3))
    
    @staticmethod
    def absolute_humidity(temp: float, rh: float) -> float:
        """絶対湿度 [kg/kg'] """
        p_sat = PsychrometricCalculator.saturation_pressure(temp)
        p_v = p_sat * rh / 100
        return 0.622 * p_v / (101325 - p_v)
    
    @staticmethod
    def enthalpy(temp: float, abs_humidity: float) -> float:
        """エンタルピー [kJ/kg']"""
        return 1.005 * temp + abs_humidity * (2501 + 1.846 * temp)


class HeatLoadCalculator:
    """熱負荷計算クラス"""
    
    # 定数
    PERSON_SENSIBLE_HEAT = 60  # 人体顕熱 [W/人]
    PERSON_LATENT_HEAT = 40  # 人体潜熱 [W/人]
    OUTSIDE_AIR_RATE = 30  # 外気導入量 [m³/h/人]
    
    # 月別日射量データ（東京の標準値）[W/m²]
    SOLAR_RADIATION_MAP = {
        1: 120, 2: 150, 3: 180, 4: 200, 5: 220, 6: 200,
        7: 220, 8: 200, 9: 180, 10: 150, 11: 120, 12: 100
    }
    
    def __init__(self, floor_spec: FloorSpec):
        self.floor_spec = floor_spec
    
    def calculate_sensible_load(
        self, 
        condition: MonthlyCondition,
        equipment_spec: EquipmentSpec
    ) -> Dict[str, float]:
        """顕熱負荷計算 [kW]"""
        temp_diff = condition.outdoor_temp - condition.indoor_temp_setpoint
        
        # 外壁貫流熱（簡易計算：床面積の40%を外壁面積と仮定）
        wall_area = self.floor_spec.floor_area * 0.4
        wall_load = (self.floor_spec.wall_u_value * wall_area * temp_diff) / 1000
        
        # 窓貫流熱
        window_load = (self.floor_spec.window_u_value * 
                      self.floor_spec.window_area * temp_diff) / 1000
        
        # 日射熱取得
        solar_radiation = self.SOLAR_RADIATION_MAP.get(condition.month, 150)
        solar_load = (self.floor_spec.window_area * 
                     self.floor_spec.solar_heat_gain_coef * 
                     solar_radiation) / 1000
        
        # 照明発熱
        lighting_load = (equipment_spec.lighting_power_density * 
                        self.floor_spec.floor_area * 
                        condition.occupancy_rate) / 1000
        
        # OA機器発熱
        oa_load = (equipment_spec.oa_equipment_power_density * 
                  self.floor_spec.floor_area * 
                  condition.occupancy_rate) / 1000
        
        # 人体顕熱
        person_load = (self.PERSON_SENSIBLE_HEAT * condition.occupancy) / 1000
        
        # 合計顕熱負荷
        total_sensible = (wall_load + window_load + solar_load + 
                         lighting_load + oa_load + person_load)
        
        return {
            'wall': wall_load,
            'window': window_load,
            'solar': solar_load,
            'lighting': lighting_load,
            'oa_equipment': oa_load,
            'person': person_load,
            'total': total_sensible
        }
    
    def calculate_latent_load(self, condition: MonthlyCondition) -> Dict[str, float]:
        """潜熱負荷計算 [kW]"""
        # 人体潜熱
        person_latent = (self.PERSON_LATENT_HEAT * condition.occupancy) / 1000
        
        # 外気潜熱
        outdoor_abs_hum = PsychrometricCalculator.absolute_humidity(
            condition.outdoor_temp, condition.outdoor_humidity)
        indoor_abs_hum = PsychrometricCalculator.absolute_humidity(
            condition.indoor_temp_setpoint, condition.indoor_humidity_setpoint)
        
        air_volume = self.OUTSIDE_AIR_RATE * condition.occupancy  # m³/h
        air_density = 1.2  # kg/m³
        moisture_diff = outdoor_abs_hum - indoor_abs_hum
        latent_heat_evap = 2501  # kJ/kg
        
        outdoor_latent = (air_volume * air_density * moisture_diff * 
                         latent_heat_evap) / 3600  # kW
        
        total_latent = person_latent + max(0, outdoor_latent)
        
        return {
            'person': person_latent,
            'outdoor_air': max(0, outdoor_latent),
            'total': total_latent
        }


class HVACSystemModel:
    """空調システムモデル"""
    
    def __init__(self, equipment_spec: EquipmentSpec):
        self.equipment_spec = equipment_spec
    
    def calculate_central_system_energy(
        self, 
        sensible_load: float, 
        latent_load: float,
        condition: MonthlyCondition
    ) -> Dict[str, float]:
        """全館空調システムのエネルギー消費量計算 [kWh/月]"""
        
        total_load = sensible_load + latent_load
        
        # 外調機ファン動力
        ahu_fan_energy = (self.equipment_spec.central_ahu_fan_power * 
                         condition.operation_hours)
        
        # 熱源エネルギー（冷房負荷のみ考慮、暖房は簡易化）
        if total_load > 0:
            chiller_energy = (total_load * condition.operation_hours / 
                            self.equipment_spec.central_chiller_cop)
        else:
            # 暖房の場合（簡易的にCOPを同じと仮定）
            chiller_energy = (abs(total_load) * condition.operation_hours / 
                            self.equipment_spec.central_chiller_cop)
        
        total_energy = ahu_fan_energy + chiller_energy
        
        return {
            'ahu_fan': ahu_fan_energy,
            'chiller': chiller_energy,
            'total': total_energy
        }
    
    def calculate_local_system_energy(
        self, 
        sensible_load: float, 
        latent_load: float,
        condition: MonthlyCondition
    ) -> Dict[str, float]:
        """個別空調システムのエネルギー消費量計算 [kWh/月]"""
        
        total_load = sensible_load + latent_load
        
        # 個別空調ファン動力
        fan_energy = (self.equipment_spec.local_ac_fan_power * 
                     condition.operation_hours)
        
        # 個別空調圧縮機エネルギー
        if total_load > 0:
            compressor_energy = (total_load * condition.operation_hours / 
                               self.equipment_spec.local_ac_cop)
        else:
            compressor_energy = (abs(total_load) * condition.operation_hours / 
                               self.equipment_spec.local_ac_cop)
        
        total_energy = fan_energy + compressor_energy
        
        return {
            'fan': fan_energy,
            'compressor': compressor_energy,
            'total': total_energy
        }


class BuildingEnergyModel:
    """建物エネルギーモデル統合クラス"""
    
    def __init__(
        self, 
        floor_spec: FloorSpec, 
        equipment_spec: EquipmentSpec,
        monthly_conditions: List[MonthlyCondition]
    ):
        self.floor_spec = floor_spec
        self.equipment_spec = equipment_spec
        self.monthly_conditions = monthly_conditions
        self.heat_calc = HeatLoadCalculator(floor_spec)
        self.hvac_model = HVACSystemModel(equipment_spec)
        self.psych_calc = PsychrometricCalculator()
    
    def simulate_year(self) -> pd.DataFrame:
        """年間シミュレーション実行"""
        results = []
        
        for condition in self.monthly_conditions:
            # 負荷計算
            sensible = self.heat_calc.calculate_sensible_load(
                condition, self.equipment_spec)
            latent = self.heat_calc.calculate_latent_load(condition)
            
            # 全館空調エネルギー計算
            central_energy = self.hvac_model.calculate_central_system_energy(
                sensible['total'], latent['total'], condition)
            
            # 個別空調エネルギー計算
            local_energy = self.hvac_model.calculate_local_system_energy(
                sensible['total'], latent['total'], condition)
            
            # 照明・OA機器エネルギー
            lighting_energy = (self.equipment_spec.lighting_power_density * 
                             self.floor_spec.floor_area * 
                             condition.occupancy_rate * 
                             condition.operation_hours) / 1000
            
            oa_equipment_energy = (self.equipment_spec.oa_equipment_power_density * 
                                  self.floor_spec.floor_area * 
                                  condition.occupancy_rate * 
                                  condition.operation_hours) / 1000
            
            # 空気線図の状態点計算
            outdoor_enthalpy = self.psych_calc.enthalpy(
                condition.outdoor_temp,
                self.psych_calc.absolute_humidity(
                    condition.outdoor_temp, condition.outdoor_humidity)
            )
            
            indoor_enthalpy = self.psych_calc.enthalpy(
                condition.indoor_temp_setpoint,
                self.psych_calc.absolute_humidity(
                    condition.indoor_temp_setpoint, 
                    condition.indoor_humidity_setpoint)
            )
            
            # 顕熱比計算
            total_load = sensible['total'] + latent['total']
            shf = sensible['total'] / total_load if total_load != 0 else 0
            
            results.append({
                'month': condition.month,
                'outdoor_temp': condition.outdoor_temp,
                'indoor_temp': condition.indoor_temp_setpoint,
                'occupancy': condition.occupancy,
                'occupancy_rate': condition.occupancy_rate,
                
                # 負荷内訳（熱量ベース）[kW]
                'load_wall_kW': sensible['wall'],
                'load_window_kW': sensible['window'],
                'load_solar_kW': sensible['solar'],
                'load_lighting_kW': sensible['lighting'],
                'load_oa_equipment_kW': sensible['oa_equipment'],
                'load_person_sensible_kW': sensible['person'],
                'load_person_latent_kW': latent['person'],
                'load_outdoor_air_latent_kW': latent['outdoor_air'],
                
                # 合計負荷 [kW]
                'sensible_load_kW': sensible['total'],
                'latent_load_kW': latent['total'],
                'total_load_kW': total_load,
                'shf': shf,
                
                # エネルギー消費量 [kWh]
                'central_ahu_fan_kWh': central_energy['ahu_fan'],
                'central_chiller_kWh': central_energy['chiller'],
                'central_total_kWh': central_energy['total'],
                
                'local_fan_kWh': local_energy['fan'],
                'local_compressor_kWh': local_energy['compressor'],
                'local_total_kWh': local_energy['total'],
                
                'lighting_kWh': lighting_energy,
                'oa_equipment_kWh': oa_equipment_energy,
                
                # 空気線図
                'outdoor_enthalpy': outdoor_enthalpy,
                'indoor_enthalpy': indoor_enthalpy,
            })
        
        return pd.DataFrame(results)
    
    def save_config(self, filepath: str):
        """設定をJSONファイルに保存"""
        config = {
            'floor_spec': self.floor_spec.to_dict(),
            'equipment_spec': self.equipment_spec.to_dict(),
            'monthly_conditions': [cond.to_dict() for cond in self.monthly_conditions]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load_config(cls, filepath: str):
        """JSONファイルから設定を読み込み"""
        with open(filepath, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        floor_spec = FloorSpec.from_dict(config['floor_spec'])
        equipment_spec = EquipmentSpec.from_dict(config['equipment_spec'])
        monthly_conditions = [
            MonthlyCondition.from_dict(cond) 
            for cond in config['monthly_conditions']
        ]
        
        return cls(floor_spec, equipment_spec, monthly_conditions)
