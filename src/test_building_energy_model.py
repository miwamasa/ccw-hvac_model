"""
ビルエネルギーモデル - テストコード
Building Energy Model - Test Suite

各機能の動作を検証するユニットテスト
"""

import unittest
import numpy as np
import pandas as pd
import os
import json

from building_energy_model import (
    FloorSpec, EquipmentSpec, MonthlyCondition,
    PsychrometricCalculator, HeatLoadCalculator,
    HVACSystemModel, BuildingEnergyModel
)
from presets import get_modern_office_preset, get_old_office_preset


class TestPsychrometricCalculator(unittest.TestCase):
    """空気線図計算のテスト"""
    
    def test_saturation_pressure(self):
        """飽和水蒸気圧の計算テスト"""
        # 20℃での飽和水蒸気圧は約2337 Pa
        p_sat = PsychrometricCalculator.saturation_pressure(20.0)
        self.assertAlmostEqual(p_sat, 2337, delta=50)
    
    def test_absolute_humidity(self):
        """絶対湿度の計算テスト"""
        # 25℃、60%RHでの絶対湿度は約0.012 kg/kg'
        abs_hum = PsychrometricCalculator.absolute_humidity(25.0, 60.0)
        self.assertAlmostEqual(abs_hum, 0.012, delta=0.002)
    
    def test_enthalpy(self):
        """エンタルピーの計算テスト"""
        # 25℃、絶対湿度0.01の場合のエンタルピー
        h = PsychrometricCalculator.enthalpy(25.0, 0.01)
        self.assertGreater(h, 0)
        self.assertLess(h, 100)  # 妥当な範囲


class TestHeatLoadCalculator(unittest.TestCase):
    """熱負荷計算のテスト"""
    
    def setUp(self):
        """テストの準備"""
        self.floor_spec = FloorSpec(
            floor_area=1000.0,
            ceiling_height=3.0,
            wall_u_value=0.5,
            window_area=200.0,
            window_u_value=2.5,
            solar_heat_gain_coef=0.5
        )
        
        self.equipment_spec = EquipmentSpec(
            lighting_power_density=10.0,
            oa_equipment_power_density=15.0,
            central_ahu_capacity=100.0,
            central_ahu_fan_power=10.0,
            central_chiller_capacity=300.0,
            central_chiller_cop=3.5,
            local_ac_capacity=50.0,
            local_ac_cop=3.0,
            local_ac_fan_power=5.0
        )
        
        self.condition = MonthlyCondition(
            month=7,
            outdoor_temp=30.0,
            outdoor_humidity=70.0,
            indoor_temp_setpoint=26.0,
            indoor_humidity_setpoint=60.0,
            supply_air_temp=18.0,
            occupancy=50,
            occupancy_rate=0.8,
            operation_hours=200
        )
        
        self.calculator = HeatLoadCalculator(self.floor_spec)
    
    def test_sensible_load_calculation(self):
        """顕熱負荷計算のテスト"""
        result = self.calculator.calculate_sensible_load(
            self.condition, self.equipment_spec
        )
        
        # 各負荷項目が計算されているか
        self.assertIn('wall', result)
        self.assertIn('window', result)
        self.assertIn('solar', result)
        self.assertIn('lighting', result)
        self.assertIn('oa_equipment', result)
        self.assertIn('person', result)
        self.assertIn('total', result)
        
        # 合計負荷が正の値であるか
        self.assertGreater(result['total'], 0)
        
        # 合計が各項目の和と一致するか
        calculated_total = (result['wall'] + result['window'] + 
                          result['solar'] + result['lighting'] + 
                          result['oa_equipment'] + result['person'])
        self.assertAlmostEqual(result['total'], calculated_total, places=2)
    
    def test_latent_load_calculation(self):
        """潜熱負荷計算のテスト"""
        result = self.calculator.calculate_latent_load(self.condition)
        
        # 各負荷項目が計算されているか
        self.assertIn('person', result)
        self.assertIn('outdoor_air', result)
        self.assertIn('total', result)
        
        # 人体潜熱が正の値であるか
        self.assertGreater(result['person'], 0)
        
        # 合計が各項目の和と一致するか
        self.assertAlmostEqual(
            result['total'], 
            result['person'] + result['outdoor_air'],
            places=2
        )
    
    def test_winter_condition(self):
        """冬季条件でのテスト"""
        winter_condition = MonthlyCondition(
            month=1,
            outdoor_temp=5.0,
            outdoor_humidity=50.0,
            indoor_temp_setpoint=22.0,
            indoor_humidity_setpoint=45.0,
            supply_air_temp=20.0,
            occupancy=50,
            occupancy_rate=0.8,
            operation_hours=200
        )
        
        result = self.calculator.calculate_sensible_load(
            winter_condition, self.equipment_spec
        )
        
        # 冬季でも計算が実行されるか
        self.assertIsNotNone(result['total'])


class TestHVACSystemModel(unittest.TestCase):
    """空調システムモデルのテスト"""
    
    def setUp(self):
        """テストの準備"""
        self.equipment_spec = EquipmentSpec(
            lighting_power_density=10.0,
            oa_equipment_power_density=15.0,
            central_ahu_capacity=100.0,
            central_ahu_fan_power=10.0,
            central_chiller_capacity=300.0,
            central_chiller_cop=3.5,
            local_ac_capacity=50.0,
            local_ac_cop=3.0,
            local_ac_fan_power=5.0
        )
        
        self.condition = MonthlyCondition(
            month=7,
            outdoor_temp=30.0,
            outdoor_humidity=70.0,
            indoor_temp_setpoint=26.0,
            indoor_humidity_setpoint=60.0,
            supply_air_temp=18.0,
            occupancy=50,
            occupancy_rate=0.8,
            operation_hours=200
        )
        
        self.model = HVACSystemModel(self.equipment_spec)
    
    def test_central_system_energy(self):
        """全館空調エネルギー計算のテスト"""
        result = self.model.calculate_central_system_energy(
            sensible_load=50.0,
            latent_load=10.0,
            condition=self.condition
        )
        
        # 各エネルギー項目が計算されているか
        self.assertIn('ahu_fan', result)
        self.assertIn('chiller', result)
        self.assertIn('total', result)
        
        # エネルギー消費が正の値であるか
        self.assertGreater(result['total'], 0)
        
        # COPが正しく適用されているか
        expected_chiller = 60.0 * 200 / 3.5  # (50+10) * hours / COP
        self.assertAlmostEqual(result['chiller'], expected_chiller, places=1)
    
    def test_local_system_energy(self):
        """個別空調エネルギー計算のテスト"""
        result = self.model.calculate_local_system_energy(
            sensible_load=50.0,
            latent_load=10.0,
            condition=self.condition
        )
        
        # 各エネルギー項目が計算されているか
        self.assertIn('fan', result)
        self.assertIn('compressor', result)
        self.assertIn('total', result)
        
        # エネルギー消費が正の値であるか
        self.assertGreater(result['total'], 0)


class TestBuildingEnergyModel(unittest.TestCase):
    """建物エネルギーモデル統合テスト"""
    
    def setUp(self):
        """テストの準備"""
        preset = get_modern_office_preset()
        self.model = BuildingEnergyModel(
            preset['floor_spec'],
            preset['equipment_spec'],
            preset['monthly_conditions']
        )
    
    def test_annual_simulation(self):
        """年間シミュレーションのテスト"""
        results = self.model.simulate_year()
        
        # 結果がDataFrameであるか
        self.assertIsInstance(results, pd.DataFrame)
        
        # 12ヶ月分のデータがあるか
        self.assertEqual(len(results), 12)
        
        # 必要なカラムが存在するか
        required_columns = [
            'month', 'sensible_load_kW', 'latent_load_kW',
            'central_total_kWh', 'local_total_kWh'
        ]
        for col in required_columns:
            self.assertIn(col, results.columns)
        
        # エネルギー消費が正の値であるか
        self.assertTrue((results['central_total_kWh'] >= 0).all())
        self.assertTrue((results['local_total_kWh'] >= 0).all())
    
    def test_config_save_load(self):
        """設定の保存・読み込みテスト"""
        # 設定を保存
        temp_file = '/tmp/test_config.json'
        self.model.save_config(temp_file)
        
        # ファイルが作成されているか
        self.assertTrue(os.path.exists(temp_file))
        
        # 設定を読み込み
        loaded_model = BuildingEnergyModel.load_config(temp_file)
        
        # 読み込まれた設定が元の設定と一致するか
        self.assertEqual(
            self.model.floor_spec.floor_area,
            loaded_model.floor_spec.floor_area
        )
        self.assertEqual(
            self.model.equipment_spec.central_chiller_cop,
            loaded_model.equipment_spec.central_chiller_cop
        )
        
        # クリーンアップ
        os.remove(temp_file)


class TestPresets(unittest.TestCase):
    """プリセット設定のテスト"""
    
    def test_modern_office_preset(self):
        """最新オフィスプリセットのテスト"""
        preset = get_modern_office_preset()
        
        # 必要なキーが存在するか
        self.assertIn('name', preset)
        self.assertIn('description', preset)
        self.assertIn('floor_spec', preset)
        self.assertIn('equipment_spec', preset)
        self.assertIn('monthly_conditions', preset)
        
        # 月別条件が12ヶ月分あるか
        self.assertEqual(len(preset['monthly_conditions']), 12)
        
        # 高効率設備の値が妥当か
        self.assertGreater(preset['equipment_spec'].central_chiller_cop, 4.0)
        self.assertLess(preset['equipment_spec'].lighting_power_density, 10.0)
    
    def test_old_office_preset(self):
        """旧式オフィスプリセットのテスト"""
        preset = get_old_office_preset()
        
        # 必要なキーが存在するか
        self.assertIn('name', preset)
        self.assertIn('description', preset)
        
        # 低効率設備の値が妥当か
        self.assertLess(preset['equipment_spec'].central_chiller_cop, 3.5)
        self.assertGreater(preset['equipment_spec'].lighting_power_density, 12.0)
    
    def test_preset_comparison(self):
        """プリセット間の比較テスト"""
        modern = get_modern_office_preset()
        old = get_old_office_preset()
        
        # 最新オフィスの方が高効率であることを確認
        self.assertGreater(
            modern['equipment_spec'].central_chiller_cop,
            old['equipment_spec'].central_chiller_cop
        )
        
        # 最新オフィスの方が断熱性能が良いことを確認
        self.assertLess(
            modern['floor_spec'].wall_u_value,
            old['floor_spec'].wall_u_value
        )


class TestIntegration(unittest.TestCase):
    """統合テスト"""
    
    def test_full_workflow(self):
        """完全なワークフローのテスト"""
        # プリセット読み込み
        preset = get_modern_office_preset()
        
        # モデル作成
        model = BuildingEnergyModel(
            preset['floor_spec'],
            preset['equipment_spec'],
            preset['monthly_conditions']
        )
        
        # シミュレーション実行
        results = model.simulate_year()
        
        # 結果検証
        self.assertEqual(len(results), 12)
        self.assertGreater(results['central_total_kWh'].sum(), 0)
        self.assertGreater(results['local_total_kWh'].sum(), 0)
        
        # 設定保存・読み込み
        temp_file = '/tmp/test_integration_config.json'
        model.save_config(temp_file)
        loaded_model = BuildingEnergyModel.load_config(temp_file)
        
        # 読み込んだモデルで再シミュレーション
        results_loaded = loaded_model.simulate_year()
        
        # 結果が一致するか
        pd.testing.assert_frame_equal(results, results_loaded)
        
        # クリーンアップ
        os.remove(temp_file)
    
    def test_energy_balance(self):
        """エネルギーバランスのテスト"""
        preset = get_modern_office_preset()
        model = BuildingEnergyModel(
            preset['floor_spec'],
            preset['equipment_spec'],
            preset['monthly_conditions']
        )
        
        results = model.simulate_year()
        
        # 各月でエネルギー消費が負になっていないか
        self.assertTrue((results['central_total_kWh'] >= 0).all())
        self.assertTrue((results['local_total_kWh'] >= 0).all())
        
        # 負荷とエネルギー消費の関係性チェック
        # 一般的に高負荷の月は高エネルギー消費
        summer_months = results[results['month'].isin([7, 8])]
        winter_months = results[results['month'].isin([1, 2])]
        
        # 夏季と冬季でエネルギー消費に違いがあるか
        self.assertNotEqual(
            summer_months['central_total_kWh'].mean(),
            winter_months['central_total_kWh'].mean()
        )


def run_tests():
    """テストスイートを実行"""
    # テストスイート作成
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # すべてのテストクラスを追加
    suite.addTests(loader.loadTestsFromTestCase(TestPsychrometricCalculator))
    suite.addTests(loader.loadTestsFromTestCase(TestHeatLoadCalculator))
    suite.addTests(loader.loadTestsFromTestCase(TestHVACSystemModel))
    suite.addTests(loader.loadTestsFromTestCase(TestBuildingEnergyModel))
    suite.addTests(loader.loadTestsFromTestCase(TestPresets))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # テスト実行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    result = run_tests()
    
    # テスト結果のサマリー
    print("\n" + "="*70)
    print("テスト結果サマリー")
    print("="*70)
    print(f"実行テスト数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失敗: {len(result.failures)}")
    print(f"エラー: {len(result.errors)}")
    print("="*70)
    
    # 終了コード
    exit(0 if result.wasSuccessful() else 1)
