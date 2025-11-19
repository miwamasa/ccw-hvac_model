"""
ビルエネルギーシミュレーションアプリ
Building Energy Simulation Application

Streamlitベースの対話的Webアプリケーション
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime
import io

from building_energy_model import (
    BuildingEnergyModel, FloorSpec, EquipmentSpec, MonthlyCondition
)
from presets import get_all_presets


# ページ設定
st.set_page_config(
    page_title="ビルエネルギーシミュレーション",
    page_icon="🏢",
    layout="wide"
)


def initialize_session_state():
    """セッション状態の初期化"""
    if 'simulation_results' not in st.session_state:
        st.session_state.simulation_results = None
    if 'current_config' not in st.session_state:
        st.session_state.current_config = None
    if 'compare_mode' not in st.session_state:
        st.session_state.compare_mode = False


def render_sidebar():
    """サイドバーのレンダリング"""
    st.sidebar.title("⚙️ 設定")
    
    # プリセット選択
    st.sidebar.header("1. プリセット選択")
    presets = get_all_presets()
    preset_options = {
        '最新オフィス': 'modern',
        '旧式オフィス': 'old',
        'カスタム設定': 'custom'
    }
    
    selected_preset = st.sidebar.selectbox(
        "プリセット",
        list(preset_options.keys()),
        key='preset_selector'
    )
    
    preset_key = preset_options[selected_preset]
    
    # 設定の読み込み・保存
    st.sidebar.header("2. 設定ファイル")
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("📁 読み込み", use_container_width=True):
            st.session_state.show_load_dialog = True
    
    with col2:
        if st.button("💾 保存", use_container_width=True):
            st.session_state.show_save_dialog = True
    
    # 比較モード
    st.sidebar.header("3. 表示オプション")
    st.session_state.compare_mode = st.sidebar.checkbox(
        "比較モード（最新 vs 旧式）",
        value=st.session_state.compare_mode
    )
    
    return preset_key, selected_preset


def render_floor_spec_editor(floor_spec: FloorSpec, key_prefix: str = "") -> FloorSpec:
    """フロア仕様エディタ"""
    st.subheader("🏗️ フロア仕様")
    
    col1, col2 = st.columns(2)
    
    with col1:
        floor_area = st.number_input(
            "床面積 [m²]",
            min_value=100.0,
            max_value=10000.0,
            value=floor_spec.floor_area,
            step=100.0,
            key=f"{key_prefix}floor_area"
        )
        
        ceiling_height = st.number_input(
            "天井高 [m]",
            min_value=2.0,
            max_value=5.0,
            value=floor_spec.ceiling_height,
            step=0.1,
            key=f"{key_prefix}ceiling_height"
        )
        
        wall_u_value = st.number_input(
            "壁U値 [W/m²K]",
            min_value=0.1,
            max_value=2.0,
            value=floor_spec.wall_u_value,
            step=0.1,
            key=f"{key_prefix}wall_u_value"
        )
    
    with col2:
        window_area = st.number_input(
            "窓面積 [m²]",
            min_value=10.0,
            max_value=1000.0,
            value=floor_spec.window_area,
            step=10.0,
            key=f"{key_prefix}window_area"
        )
        
        window_u_value = st.number_input(
            "窓U値 [W/m²K]",
            min_value=0.5,
            max_value=6.0,
            value=floor_spec.window_u_value,
            step=0.1,
            key=f"{key_prefix}window_u_value"
        )
        
        solar_heat_gain_coef = st.number_input(
            "日射熱取得係数 [-]",
            min_value=0.1,
            max_value=1.0,
            value=floor_spec.solar_heat_gain_coef,
            step=0.05,
            key=f"{key_prefix}solar_heat_gain_coef"
        )
    
    return FloorSpec(
        floor_area=floor_area,
        ceiling_height=ceiling_height,
        wall_u_value=wall_u_value,
        window_area=window_area,
        window_u_value=window_u_value,
        solar_heat_gain_coef=solar_heat_gain_coef
    )


def render_equipment_spec_editor(equipment_spec: EquipmentSpec, key_prefix: str = "") -> EquipmentSpec:
    """設備仕様エディタ"""
    st.subheader("🔧 設備仕様")
    
    # 照明・OA機器
    st.markdown("**照明・OA機器**")
    col1, col2 = st.columns(2)
    
    with col1:
        lighting_power_density = st.number_input(
            "照明電力密度 [W/m²]",
            min_value=5.0,
            max_value=30.0,
            value=equipment_spec.lighting_power_density,
            step=1.0,
            key=f"{key_prefix}lighting"
        )
    
    with col2:
        oa_equipment_power_density = st.number_input(
            "OA機器電力密度 [W/m²]",
            min_value=5.0,
            max_value=30.0,
            value=equipment_spec.oa_equipment_power_density,
            step=1.0,
            key=f"{key_prefix}oa_equipment"
        )
    
    # 全館空調
    st.markdown("**全館空調システム**")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        central_ahu_capacity = st.number_input(
            "外調機能力 [kW]",
            min_value=10.0,
            max_value=500.0,
            value=equipment_spec.central_ahu_capacity,
            step=10.0,
            key=f"{key_prefix}central_ahu_cap"
        )
    
    with col2:
        central_ahu_fan_power = st.number_input(
            "外調機ファン [kW]",
            min_value=1.0,
            max_value=50.0,
            value=equipment_spec.central_ahu_fan_power,
            step=1.0,
            key=f"{key_prefix}central_ahu_fan"
        )
    
    with col3:
        central_chiller_capacity = st.number_input(
            "熱源容量 [kW]",
            min_value=50.0,
            max_value=1000.0,
            value=equipment_spec.central_chiller_capacity,
            step=10.0,
            key=f"{key_prefix}central_chiller_cap"
        )
    
    with col4:
        central_chiller_cop = st.number_input(
            "熱源COP [-]",
            min_value=2.0,
            max_value=6.0,
            value=equipment_spec.central_chiller_cop,
            step=0.1,
            key=f"{key_prefix}central_chiller_cop"
        )
    
    # 個別空調
    st.markdown("**個別空調システム**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        local_ac_capacity = st.number_input(
            "個別空調容量 [kW]",
            min_value=10.0,
            max_value=200.0,
            value=equipment_spec.local_ac_capacity,
            step=10.0,
            key=f"{key_prefix}local_ac_cap"
        )
    
    with col2:
        local_ac_cop = st.number_input(
            "個別空調COP [-]",
            min_value=2.0,
            max_value=5.0,
            value=equipment_spec.local_ac_cop,
            step=0.1,
            key=f"{key_prefix}local_ac_cop"
        )
    
    with col3:
        local_ac_fan_power = st.number_input(
            "個別空調ファン [kW]",
            min_value=1.0,
            max_value=20.0,
            value=equipment_spec.local_ac_fan_power,
            step=1.0,
            key=f"{key_prefix}local_ac_fan"
        )
    
    return EquipmentSpec(
        lighting_power_density=lighting_power_density,
        oa_equipment_power_density=oa_equipment_power_density,
        central_ahu_capacity=central_ahu_capacity,
        central_ahu_fan_power=central_ahu_fan_power,
        central_chiller_capacity=central_chiller_capacity,
        central_chiller_cop=central_chiller_cop,
        local_ac_capacity=local_ac_capacity,
        local_ac_cop=local_ac_cop,
        local_ac_fan_power=local_ac_fan_power
    )


def render_monthly_conditions_editor(conditions: list) -> list:
    """月別条件エディタ"""
    st.subheader("📅 月別運用条件")
    
    # データフレームで一括編集
    df_conditions = pd.DataFrame([
        {
            '月': c.month,
            '外気温[℃]': c.outdoor_temp,
            '外気湿度[%]': c.outdoor_humidity,
            '室温設定[℃]': c.indoor_temp_setpoint,
            '室内湿度設定[%]': c.indoor_humidity_setpoint,
            '給気温度[℃]': c.supply_air_temp,
            '居住者数[人]': c.occupancy,
            '利用率[-]': c.occupancy_rate,
            '運転時間[h]': c.operation_hours
        }
        for c in conditions
    ])
    
    edited_df = st.data_editor(
        df_conditions,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed"
    )
    
    # 編集されたデータからMonthlyConditionリストを生成
    updated_conditions = []
    for _, row in edited_df.iterrows():
        updated_conditions.append(MonthlyCondition(
            month=int(row['月']),
            outdoor_temp=float(row['外気温[℃]']),
            outdoor_humidity=float(row['外気湿度[%]']),
            indoor_temp_setpoint=float(row['室温設定[℃]']),
            indoor_humidity_setpoint=float(row['室内湿度設定[%]']),
            supply_air_temp=float(row['給気温度[℃]']),
            occupancy=int(row['居住者数[人]']),
            occupancy_rate=float(row['利用率[-]']),
            operation_hours=float(row['運転時間[h]'])
        ))
    
    return updated_conditions


def plot_energy_comparison(df: pd.DataFrame, df_compare: pd.DataFrame = None):
    """エネルギー消費量比較グラフ"""
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('全館空調システム', '個別空調システム'),
        vertical_spacing=0.15
    )
    
    months = df['month'].tolist()
    
    # 全館空調
    fig.add_trace(
        go.Bar(name='ファン', x=months, y=df['central_ahu_fan_kWh'],
               marker_color='lightblue'),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(name='熱源', x=months, y=df['central_chiller_kWh'],
               marker_color='darkblue'),
        row=1, col=1
    )
    
    # 個別空調
    fig.add_trace(
        go.Bar(name='ファン', x=months, y=df['local_fan_kWh'],
               marker_color='lightcoral', showlegend=False),
        row=2, col=1
    )
    fig.add_trace(
        go.Bar(name='圧縮機', x=months, y=df['local_compressor_kWh'],
               marker_color='darkred'),
        row=2, col=1
    )
    
    # 比較モードの場合
    if df_compare is not None:
        fig.add_trace(
            go.Scatter(name='全館空調（比較）', x=months, 
                      y=df_compare['central_total_kWh'],
                      mode='lines+markers', line=dict(dash='dash', color='blue')),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(name='個別空調（比較）', x=months, 
                      y=df_compare['local_total_kWh'],
                      mode='lines+markers', line=dict(dash='dash', color='red')),
            row=2, col=1
        )
    
    fig.update_xaxes(title_text="月", row=2, col=1)
    fig.update_yaxes(title_text="エネルギー消費量 [kWh]", row=1, col=1)
    fig.update_yaxes(title_text="エネルギー消費量 [kWh]", row=2, col=1)
    
    fig.update_layout(
        height=700,
        barmode='stack',
        hovermode='x unified',
        title_text="空調システム別エネルギー消費量比較"
    )
    
    return fig


def plot_load_breakdown(df: pd.DataFrame):
    """負荷内訳グラフ（熱量ベース）"""
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('顕熱負荷内訳', '潜熱負荷内訳'),
        vertical_spacing=0.15
    )
    
    months = df['month'].tolist()
    
    # 顕熱負荷
    fig.add_trace(
        go.Bar(name='壁貫流熱', x=months, y=df['load_wall_kW']),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(name='窓貫流熱', x=months, y=df['load_window_kW']),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(name='日射熱', x=months, y=df['load_solar_kW']),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(name='照明', x=months, y=df['load_lighting_kW']),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(name='OA機器', x=months, y=df['load_oa_equipment_kW']),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(name='人体', x=months, y=df['load_person_sensible_kW']),
        row=1, col=1
    )
    
    # 潜熱負荷
    fig.add_trace(
        go.Bar(name='人体', x=months, y=df['load_person_latent_kW'],
               marker_color='orange', showlegend=False),
        row=2, col=1
    )
    fig.add_trace(
        go.Bar(name='外気', x=months, y=df['load_outdoor_air_latent_kW'],
               marker_color='lightgreen'),
        row=2, col=1
    )
    
    fig.update_xaxes(title_text="月", row=2, col=1)
    fig.update_yaxes(title_text="顕熱負荷 [kW]", row=1, col=1)
    fig.update_yaxes(title_text="潜熱負荷 [kW]", row=2, col=1)
    
    fig.update_layout(
        height=700,
        barmode='stack',
        hovermode='x unified',
        title_text="月別負荷内訳（熱量ベース）"
    )
    
    return fig


def plot_system_comparison_summary(df: pd.DataFrame):
    """システム比較サマリー"""
    fig = go.Figure()
    
    months = df['month'].tolist()
    
    fig.add_trace(go.Scatter(
        name='全館空調',
        x=months,
        y=df['central_total_kWh'],
        mode='lines+markers',
        line=dict(color='blue', width=3),
        marker=dict(size=8)
    ))
    
    fig.add_trace(go.Scatter(
        name='個別空調',
        x=months,
        y=df['local_total_kWh'],
        mode='lines+markers',
        line=dict(color='red', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title="全館空調 vs 個別空調 エネルギー消費量比較",
        xaxis_title="月",
        yaxis_title="エネルギー消費量 [kWh]",
        hovermode='x unified',
        height=400
    )
    
    return fig


def main():
    """メインアプリケーション"""
    initialize_session_state()
    
    st.title("🏢 ビルエネルギーシミュレーション")
    st.markdown("---")
    
    # サイドバー
    preset_key, preset_name = render_sidebar()
    
    # メインコンテンツ
    tab1, tab2, tab3, tab4 = st.tabs([
        "📝 設定", "📊 シミュレーション", "📈 結果", "💾 データ"
    ])
    
    # タブ1: 設定
    with tab1:
        st.header("設定")
        
        presets = get_all_presets()
        
        if preset_key in presets:
            preset = presets[preset_key]
            st.info(f"**{preset['name']}** を選択中: {preset['description']}")
            
            floor_spec = render_floor_spec_editor(preset['floor_spec'])
            equipment_spec = render_equipment_spec_editor(preset['equipment_spec'])
            monthly_conditions = render_monthly_conditions_editor(preset['monthly_conditions'])
        else:
            # カスタム設定
            st.info("カスタム設定モード")
            
            # デフォルト値として最新オフィスを使用
            default_preset = presets['modern']
            floor_spec = render_floor_spec_editor(default_preset['floor_spec'])
            equipment_spec = render_equipment_spec_editor(default_preset['equipment_spec'])
            monthly_conditions = render_monthly_conditions_editor(default_preset['monthly_conditions'])
        
        # 設定を保存
        st.session_state.current_config = {
            'floor_spec': floor_spec,
            'equipment_spec': equipment_spec,
            'monthly_conditions': monthly_conditions
        }
    
    # タブ2: シミュレーション
    with tab2:
        st.header("シミュレーション実行")
        
        if st.button("🚀 シミュレーション実行", type="primary", use_container_width=True):
            if st.session_state.current_config is None:
                st.error("設定を確認してください")
            else:
                with st.spinner("計算中..."):
                    config = st.session_state.current_config
                    model = BuildingEnergyModel(
                        config['floor_spec'],
                        config['equipment_spec'],
                        config['monthly_conditions']
                    )
                    
                    results = model.simulate_year()
                    st.session_state.simulation_results = results
                    
                    # 比較モードの場合
                    if st.session_state.compare_mode:
                        # 旧式オフィスでも計算
                        old_preset = presets['old']
                        model_old = BuildingEnergyModel(
                            old_preset['floor_spec'],
                            old_preset['equipment_spec'],
                            old_preset['monthly_conditions']
                        )
                        results_old = model_old.simulate_year()
                        st.session_state.comparison_results = results_old
                    
                    st.success("✅ シミュレーション完了！")
        
        # 結果サマリー
        if st.session_state.simulation_results is not None:
            st.subheader("結果サマリー")
            
            df = st.session_state.simulation_results
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "年間全館空調",
                    f"{df['central_total_kWh'].sum():,.0f} kWh"
                )
            
            with col2:
                st.metric(
                    "年間個別空調",
                    f"{df['local_total_kWh'].sum():,.0f} kWh"
                )
            
            with col3:
                diff = df['central_total_kWh'].sum() - df['local_total_kWh'].sum()
                diff_pct = (diff / df['local_total_kWh'].sum()) * 100
                st.metric(
                    "差分（全館 - 個別）",
                    f"{diff:,.0f} kWh",
                    f"{diff_pct:+.1f}%"
                )
    
    # タブ3: 結果
    with tab3:
        st.header("シミュレーション結果")
        
        if st.session_state.simulation_results is None:
            st.info("シミュレーションを実行してください")
        else:
            df = st.session_state.simulation_results
            df_compare = st.session_state.get('comparison_results', None)
            
            # システム比較
            st.plotly_chart(
                plot_system_comparison_summary(df),
                use_container_width=True
            )
            
            # 詳細グラフ
            st.plotly_chart(
                plot_energy_comparison(df, df_compare),
                use_container_width=True
            )
            
            st.plotly_chart(
                plot_load_breakdown(df),
                use_container_width=True
            )
    
    # タブ4: データ
    with tab4:
        st.header("データ管理")
        
        if st.session_state.simulation_results is not None:
            df = st.session_state.simulation_results
            
            st.subheader("シミュレーション結果")
            st.dataframe(df, use_container_width=True)
            
            # CSV保存
            st.subheader("CSV保存")
            
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
            csv_data = csv_buffer.getvalue()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"building_energy_sim_{timestamp}.csv"
            
            st.download_button(
                label="📥 CSVダウンロード",
                data=csv_data,
                file_name=filename,
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("シミュレーション結果がありません")


if __name__ == "__main__":
    main()
