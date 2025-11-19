import { useState } from 'react';
import type { FloorSpec, EquipmentSpec } from '../types';

interface ConfigFormProps {
  floorSpec: FloorSpec;
  equipmentSpec: EquipmentSpec;
  onFloorSpecChange: (spec: FloorSpec) => void;
  onEquipmentSpecChange: (spec: EquipmentSpec) => void;
}

export default function ConfigForm({
  floorSpec,
  equipmentSpec,
  onFloorSpecChange,
  onEquipmentSpecChange,
}: ConfigFormProps) {
  const handleFloorChange = (field: keyof FloorSpec, value: string) => {
    onFloorSpecChange({
      ...floorSpec,
      [field]: parseFloat(value) || 0,
    });
  };

  const handleEquipmentChange = (field: keyof EquipmentSpec, value: string) => {
    onEquipmentSpecChange({
      ...equipmentSpec,
      [field]: parseFloat(value) || 0,
    });
  };

  return (
    <div className="space-y-6">
      {/* Floor Specifications */}
      <div>
        <h3 className="text-lg font-semibold mb-3 text-gray-800 dark:text-white">
          建物仕様
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              床面積 (m²)
            </label>
            <input
              type="number"
              value={floorSpec.floor_area}
              onChange={(e) => handleFloorChange('floor_area', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              step="0.1"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              天井高 (m)
            </label>
            <input
              type="number"
              value={floorSpec.ceiling_height}
              onChange={(e) => handleFloorChange('ceiling_height', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              step="0.1"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              壁U値 (W/m²K)
            </label>
            <input
              type="number"
              value={floorSpec.wall_u_value}
              onChange={(e) => handleFloorChange('wall_u_value', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              step="0.01"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              窓面積 (m²)
            </label>
            <input
              type="number"
              value={floorSpec.window_area}
              onChange={(e) => handleFloorChange('window_area', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              step="0.1"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              窓U値 (W/m²K)
            </label>
            <input
              type="number"
              value={floorSpec.window_u_value}
              onChange={(e) => handleFloorChange('window_u_value', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              step="0.1"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              日射熱取得係数
            </label>
            <input
              type="number"
              value={floorSpec.solar_heat_gain_coef}
              onChange={(e) => handleFloorChange('solar_heat_gain_coef', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              step="0.01"
            />
          </div>
        </div>
      </div>

      {/* Equipment Specifications */}
      <div>
        <h3 className="text-lg font-semibold mb-3 text-gray-800 dark:text-white">
          設備仕様
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              照明電力密度 (W/m²)
            </label>
            <input
              type="number"
              value={equipmentSpec.lighting_power_density}
              onChange={(e) => handleEquipmentChange('lighting_power_density', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              step="0.1"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              OA機器電力密度 (W/m²)
            </label>
            <input
              type="number"
              value={equipmentSpec.oa_equipment_power_density}
              onChange={(e) => handleEquipmentChange('oa_equipment_power_density', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              step="0.1"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              外調機容量 (kW)
            </label>
            <input
              type="number"
              value={equipmentSpec.central_ahu_capacity}
              onChange={(e) => handleEquipmentChange('central_ahu_capacity', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              step="0.1"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              外調機ファン動力 (kW)
            </label>
            <input
              type="number"
              value={equipmentSpec.central_ahu_fan_power}
              onChange={(e) => handleEquipmentChange('central_ahu_fan_power', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              step="0.1"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              熱源容量 (kW)
            </label>
            <input
              type="number"
              value={equipmentSpec.central_chiller_capacity}
              onChange={(e) => handleEquipmentChange('central_chiller_capacity', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              step="0.1"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              熱源COP
            </label>
            <input
              type="number"
              value={equipmentSpec.central_chiller_cop}
              onChange={(e) => handleEquipmentChange('central_chiller_cop', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              step="0.1"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              個別空調容量 (kW)
            </label>
            <input
              type="number"
              value={equipmentSpec.local_ac_capacity}
              onChange={(e) => handleEquipmentChange('local_ac_capacity', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              step="0.1"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              個別空調COP
            </label>
            <input
              type="number"
              value={equipmentSpec.local_ac_cop}
              onChange={(e) => handleEquipmentChange('local_ac_cop', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              step="0.1"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              個別空調ファン動力 (kW)
            </label>
            <input
              type="number"
              value={equipmentSpec.local_ac_fan_power}
              onChange={(e) => handleEquipmentChange('local_ac_fan_power', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              step="0.1"
            />
          </div>
        </div>
      </div>
    </div>
  );
}
