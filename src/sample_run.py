"""
サンプル実行スクリプト
Sample Execution Script

コマンドラインからシミュレーションを実行し、結果を保存する例
"""

from building_energy_model import BuildingEnergyModel
from presets import get_modern_office_preset, get_old_office_preset
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime


def run_simulation_example():
    """シミュレーション実行例"""
    
    print("="*70)
    print("ビルエネルギーシミュレーション - サンプル実行")
    print("="*70)
    print()
    
    # 1. 最新オフィスのシミュレーション
    print("1. 最新オフィスのシミュレーション実行中...")
    modern_preset = get_modern_office_preset()
    modern_model = BuildingEnergyModel(
        modern_preset['floor_spec'],
        modern_preset['equipment_spec'],
        modern_preset['monthly_conditions']
    )
    
    modern_results = modern_model.simulate_year()
    print("   ✓ 完了")
    print()
    
    # 2. 旧式オフィスのシミュレーション
    print("2. 旧式オフィスのシミュレーション実行中...")
    old_preset = get_old_office_preset()
    old_model = BuildingEnergyModel(
        old_preset['floor_spec'],
        old_preset['equipment_spec'],
        old_preset['monthly_conditions']
    )
    
    old_results = old_model.simulate_year()
    print("   ✓ 完了")
    print()
    
    # 3. 結果の表示
    print("="*70)
    print("シミュレーション結果サマリー")
    print("="*70)
    print()
    
    print("【最新オフィス】")
    print(f"  年間全館空調消費量: {modern_results['central_total_kWh'].sum():,.0f} kWh")
    print(f"  年間個別空調消費量: {modern_results['local_total_kWh'].sum():,.0f} kWh")
    print()
    
    print("【旧式オフィス】")
    print(f"  年間全館空調消費量: {old_results['central_total_kWh'].sum():,.0f} kWh")
    print(f"  年間個別空調消費量: {old_results['local_total_kWh'].sum():,.0f} kWh")
    print()
    
    # 4. 比較
    print("【比較分析】")
    modern_total = modern_results['central_total_kWh'].sum()
    old_total = old_results['central_total_kWh'].sum()
    reduction = ((old_total - modern_total) / old_total) * 100
    
    print(f"  エネルギー削減率: {reduction:.1f}%")
    print(f"  削減量: {old_total - modern_total:,.0f} kWh/年")
    print()
    
    # 5. 結果の保存
    print("="*70)
    print("結果の保存")
    print("="*70)
    print()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # CSV保存
    modern_csv = f"modern_office_results_{timestamp}.csv"
    old_csv = f"old_office_results_{timestamp}.csv"
    
    modern_results.to_csv(modern_csv, index=False, encoding='utf-8-sig')
    old_results.to_csv(old_csv, index=False, encoding='utf-8-sig')
    
    print(f"  ✓ 最新オフィス結果を保存: {modern_csv}")
    print(f"  ✓ 旧式オフィス結果を保存: {old_csv}")
    print()
    
    # 設定の保存
    modern_config = f"modern_office_config_{timestamp}.json"
    old_config = f"old_office_config_{timestamp}.json"
    
    modern_model.save_config(modern_config)
    old_model.save_config(old_config)
    
    print(f"  ✓ 最新オフィス設定を保存: {modern_config}")
    print(f"  ✓ 旧式オフィス設定を保存: {old_config}")
    print()
    
    # 6. 簡易グラフの作成
    print("="*70)
    print("グラフの作成")
    print("="*70)
    print()
    
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))
    
    # 月別エネルギー消費量
    months = modern_results['month'].tolist()
    
    axes[0].plot(months, modern_results['central_total_kWh'], 
                'b-o', label='最新オフィス（全館空調）', linewidth=2)
    axes[0].plot(months, old_results['central_total_kWh'], 
                'r-o', label='旧式オフィス（全館空調）', linewidth=2)
    axes[0].set_xlabel('月')
    axes[0].set_ylabel('エネルギー消費量 [kWh]')
    axes[0].set_title('全館空調システムのエネルギー消費量比較')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # 負荷比較
    axes[1].plot(months, modern_results['total_load_kW'], 
                'b-s', label='最新オフィス', linewidth=2)
    axes[1].plot(months, old_results['total_load_kW'], 
                'r-s', label='旧式オフィス', linewidth=2)
    axes[1].set_xlabel('月')
    axes[1].set_ylabel('総負荷 [kW]')
    axes[1].set_title('月別総負荷の比較')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    graph_file = f"comparison_graph_{timestamp}.png"
    plt.savefig(graph_file, dpi=150)
    print(f"  ✓ グラフを保存: {graph_file}")
    print()
    
    # 7. 月別詳細レポート
    print("="*70)
    print("月別詳細レポート（最新オフィス・全館空調）")
    print("="*70)
    print()
    
    report_df = modern_results[['month', 'outdoor_temp', 'total_load_kW', 
                                'central_total_kWh']].copy()
    report_df.columns = ['月', '外気温[℃]', '総負荷[kW]', '消費量[kWh]']
    
    print(report_df.to_string(index=False))
    print()
    
    print("="*70)
    print("サンプル実行完了")
    print("="*70)


def demonstrate_custom_configuration():
    """カスタム設定のデモンストレーション"""
    
    print("\n" + "="*70)
    print("カスタム設定のデモンストレーション")
    print("="*70)
    print()
    
    # 最新オフィスをベースにカスタマイズ
    preset = get_modern_office_preset()
    
    # 床面積を変更
    preset['floor_spec'].floor_area = 1500.0
    
    # 窓面積を増やす（窓面積比20%）
    preset['floor_spec'].window_area = 1500.0 * 0.20
    
    # 居住者数を増やす
    for condition in preset['monthly_conditions']:
        condition.occupancy = 75  # 50人 → 75人に増加
    
    print("カスタマイズした設定:")
    print(f"  床面積: {preset['floor_spec'].floor_area} m²")
    print(f"  窓面積: {preset['floor_spec'].window_area} m²")
    print(f"  居住者数: {preset['monthly_conditions'][0].occupancy} 人")
    print()
    
    # シミュレーション実行
    print("シミュレーション実行中...")
    model = BuildingEnergyModel(
        preset['floor_spec'],
        preset['equipment_spec'],
        preset['monthly_conditions']
    )
    
    results = model.simulate_year()
    print("✓ 完了")
    print()
    
    print("結果:")
    print(f"  年間全館空調消費量: {results['central_total_kWh'].sum():,.0f} kWh")
    print(f"  年間個別空調消費量: {results['local_total_kWh'].sum():,.0f} kWh")
    print()
    
    # 設定を保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    config_file = f"custom_config_{timestamp}.json"
    model.save_config(config_file)
    print(f"カスタム設定を保存: {config_file}")
    print()


if __name__ == "__main__":
    # メイン実行
    run_simulation_example()
    
    # カスタム設定デモ
    demonstrate_custom_configuration()
    
    print("\n" + "="*70)
    print("すべての処理が完了しました")
    print("="*70)
