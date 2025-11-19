"""
プリセット設定
Building Energy Model - Preset Configurations

最新オフィスと旧式オフィスのデフォルト設定を提供
"""

from building_energy_model import FloorSpec, EquipmentSpec, MonthlyCondition
from typing import Dict, List


def get_modern_office_preset() -> Dict:
    """
    最新オフィスのプリセット
    - 高断熱・高気密
    - 高効率空調設備
    - LED照明
    - 省エネOA機器
    """
    floor_spec = FloorSpec(
        floor_area=1000.0,  # 1000m²
        ceiling_height=3.0,  # 3m
        wall_u_value=0.3,  # 高断熱 0.3 W/m²K
        window_area=150.0,  # 窓面積比15%
        window_u_value=1.5,  # Low-E複層ガラス 1.5 W/m²K
        solar_heat_gain_coef=0.4  # 日射遮蔽性能良好 0.4
    )
    
    equipment_spec = EquipmentSpec(
        lighting_power_density=8.0,  # LED照明 8 W/m²
        oa_equipment_power_density=12.0,  # 省エネPC 12 W/m²
        
        # 全館空調（高効率）
        central_ahu_capacity=120.0,
        central_ahu_fan_power=8.0,  # インバータ制御
        central_chiller_capacity=350.0,
        central_chiller_cop=4.5,  # 高効率チラー
        
        # 個別空調（高効率）
        local_ac_capacity=60.0,
        local_ac_cop=4.0,  # 高効率個別空調
        local_ac_fan_power=5.0
    )
    
    monthly_conditions = _get_default_monthly_conditions()
    
    return {
        'name': '最新オフィス',
        'description': '高断熱・高気密、高効率設備を備えた最新オフィスビル',
        'floor_spec': floor_spec,
        'equipment_spec': equipment_spec,
        'monthly_conditions': monthly_conditions
    }


def get_old_office_preset() -> Dict:
    """
    旧式オフィスのプリセット
    - 低断熱
    - 低効率空調設備
    - 蛍光灯照明
    - 旧式OA機器
    """
    floor_spec = FloorSpec(
        floor_area=1000.0,  # 1000m²
        ceiling_height=3.0,  # 3m
        wall_u_value=0.8,  # 低断熱 0.8 W/m²K
        window_area=200.0,  # 窓面積比20%
        window_u_value=4.0,  # 単板ガラス 4.0 W/m²K
        solar_heat_gain_coef=0.7  # 日射遮蔽性能低い 0.7
    )
    
    equipment_spec = EquipmentSpec(
        lighting_power_density=15.0,  # 蛍光灯 15 W/m²
        oa_equipment_power_density=20.0,  # 旧式PC 20 W/m²
        
        # 全館空調（低効率）
        central_ahu_capacity=120.0,
        central_ahu_fan_power=15.0,  # 定風量
        central_chiller_capacity=350.0,
        central_chiller_cop=3.0,  # 低効率チラー
        
        # 個別空調（低効率）
        local_ac_capacity=60.0,
        local_ac_cop=2.5,  # 低効率個別空調
        local_ac_fan_power=8.0
    )
    
    monthly_conditions = _get_default_monthly_conditions()
    
    return {
        'name': '旧式オフィス',
        'description': '低断熱、低効率設備の旧式オフィスビル',
        'floor_spec': floor_spec,
        'equipment_spec': equipment_spec,
        'monthly_conditions': monthly_conditions
    }


def _get_default_monthly_conditions() -> List[MonthlyCondition]:
    """
    デフォルトの月別運用条件（東京標準）
    """
    # 東京の平均気温・湿度データ
    conditions = [
        # 冬季（1-3月）
        MonthlyCondition(
            month=1, outdoor_temp=5.2, outdoor_humidity=52,
            indoor_temp_setpoint=22.0, indoor_humidity_setpoint=45,
            supply_air_temp=20.0, occupancy=50, occupancy_rate=0.85,
            operation_hours=200
        ),
        MonthlyCondition(
            month=2, outdoor_temp=5.7, outdoor_humidity=53,
            indoor_temp_setpoint=22.0, indoor_humidity_setpoint=45,
            supply_air_temp=20.0, occupancy=50, occupancy_rate=0.85,
            operation_hours=180
        ),
        MonthlyCondition(
            month=3, outdoor_temp=8.7, outdoor_humidity=55,
            indoor_temp_setpoint=22.0, indoor_humidity_setpoint=50,
            supply_air_temp=20.0, occupancy=50, occupancy_rate=0.85,
            operation_hours=200
        ),
        # 春季（4-5月）
        MonthlyCondition(
            month=4, outdoor_temp=13.9, outdoor_humidity=60,
            indoor_temp_setpoint=24.0, indoor_humidity_setpoint=50,
            supply_air_temp=18.0, occupancy=50, occupancy_rate=0.80,
            operation_hours=200
        ),
        MonthlyCondition(
            month=5, outdoor_temp=18.2, outdoor_humidity=65,
            indoor_temp_setpoint=24.0, indoor_humidity_setpoint=55,
            supply_air_temp=18.0, occupancy=50, occupancy_rate=0.80,
            operation_hours=200
        ),
        # 梅雨・夏季（6-9月）
        MonthlyCondition(
            month=6, outdoor_temp=21.4, outdoor_humidity=75,
            indoor_temp_setpoint=26.0, indoor_humidity_setpoint=60,
            supply_air_temp=16.0, occupancy=50, occupancy_rate=0.75,
            operation_hours=200
        ),
        MonthlyCondition(
            month=7, outdoor_temp=25.0, outdoor_humidity=78,
            indoor_temp_setpoint=26.0, indoor_humidity_setpoint=60,
            supply_air_temp=16.0, occupancy=50, occupancy_rate=0.70,
            operation_hours=200
        ),
        MonthlyCondition(
            month=8, outdoor_temp=26.4, outdoor_humidity=77,
            indoor_temp_setpoint=26.0, indoor_humidity_setpoint=60,
            supply_air_temp=16.0, occupancy=50, occupancy_rate=0.60,
            operation_hours=180
        ),
        MonthlyCondition(
            month=9, outdoor_temp=22.8, outdoor_humidity=75,
            indoor_temp_setpoint=26.0, indoor_humidity_setpoint=60,
            supply_air_temp=18.0, occupancy=50, occupancy_rate=0.75,
            operation_hours=200
        ),
        # 秋季（10-11月）
        MonthlyCondition(
            month=10, outdoor_temp=17.5, outdoor_humidity=68,
            indoor_temp_setpoint=24.0, indoor_humidity_setpoint=55,
            supply_air_temp=18.0, occupancy=50, occupancy_rate=0.85,
            operation_hours=200
        ),
        MonthlyCondition(
            month=11, outdoor_temp=12.1, outdoor_humidity=60,
            indoor_temp_setpoint=22.0, indoor_humidity_setpoint=50,
            supply_air_temp=20.0, occupancy=50, occupancy_rate=0.85,
            operation_hours=200
        ),
        # 冬季（12月）
        MonthlyCondition(
            month=12, outdoor_temp=7.6, outdoor_humidity=56,
            indoor_temp_setpoint=22.0, indoor_humidity_setpoint=45,
            supply_air_temp=20.0, occupancy=50, occupancy_rate=0.80,
            operation_hours=180
        ),
    ]
    
    return conditions


def get_all_presets() -> Dict[str, Dict]:
    """すべてのプリセットを取得"""
    return {
        'modern': get_modern_office_preset(),
        'old': get_old_office_preset()
    }
