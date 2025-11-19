import { Plus, Trash2 } from 'lucide-react';
import type { ParameterRange } from '../types';

interface ParameterSelectorProps {
  parameterRanges: ParameterRange[];
  onChange: (ranges: ParameterRange[]) => void;
}

// Available parameters for calibration
const AVAILABLE_PARAMETERS = [
  // Building and Equipment Parameters
  { name: 'floor_spec.wall_u_value', label: '壁U値', unit: 'W/m²K', defaultMin: 0.1, defaultMax: 1.0 },
  { name: 'floor_spec.window_u_value', label: '窓U値', unit: 'W/m²K', defaultMin: 1.0, defaultMax: 6.0 },
  { name: 'floor_spec.solar_heat_gain_coef', label: '日射熱取得係数', unit: '', defaultMin: 0.1, defaultMax: 0.9 },
  { name: 'equipment_spec.lighting_power_density', label: '照明電力密度', unit: 'W/m²', defaultMin: 5.0, defaultMax: 20.0 },
  { name: 'equipment_spec.oa_equipment_power_density', label: 'OA機器電力密度', unit: 'W/m²', defaultMin: 5.0, defaultMax: 30.0 },
  { name: 'equipment_spec.central_chiller_cop', label: '熱源COP', unit: '', defaultMin: 2.0, defaultMax: 6.0 },
  { name: 'equipment_spec.local_ac_cop', label: '個別空調COP', unit: '', defaultMin: 2.0, defaultMax: 5.0 },

  // Seasonal Parameters - Winter (11-3月)
  { name: 'winter_indoor_temp_setpoint', label: '冬季 室温設定', unit: '°C', defaultMin: 18.0, defaultMax: 24.0 },
  { name: 'winter_indoor_humidity_setpoint', label: '冬季 室内湿度設定', unit: '%', defaultMin: 30.0, defaultMax: 60.0 },
  { name: 'winter_supply_air_temp', label: '冬季 給気温度設定', unit: '°C', defaultMin: 15.0, defaultMax: 25.0 },

  // Seasonal Parameters - Summer (7-9月)
  { name: 'summer_indoor_temp_setpoint', label: '夏季 室温設定', unit: '°C', defaultMin: 22.0, defaultMax: 28.0 },
  { name: 'summer_indoor_humidity_setpoint', label: '夏季 室内湿度設定', unit: '%', defaultMin: 40.0, defaultMax: 70.0 },
  { name: 'summer_supply_air_temp', label: '夏季 給気温度設定', unit: '°C', defaultMin: 12.0, defaultMax: 20.0 },

  // Seasonal Parameters - Mid-season (4-6, 10月)
  { name: 'mid_indoor_temp_setpoint', label: '中間期 室温設定', unit: '°C', defaultMin: 20.0, defaultMax: 26.0 },
  { name: 'mid_indoor_humidity_setpoint', label: '中間期 室内湿度設定', unit: '%', defaultMin: 35.0, defaultMax: 65.0 },
  { name: 'mid_supply_air_temp', label: '中間期 給気温度設定', unit: '°C', defaultMin: 14.0, defaultMax: 22.0 },
];

export default function ParameterSelector({
  parameterRanges,
  onChange,
}: ParameterSelectorProps) {
  const handleAdd = () => {
    const firstAvailable = AVAILABLE_PARAMETERS[0];
    const newRange: ParameterRange = {
      parameter_name: firstAvailable.name,
      min_value: firstAvailable.defaultMin,
      max_value: firstAvailable.defaultMax,
      num_steps: 10,
    };
    onChange([...parameterRanges, newRange]);
  };

  const handleRemove = (index: number) => {
    const newRanges = parameterRanges.filter((_, i) => i !== index);
    onChange(newRanges);
  };

  const handleChange = (
    index: number,
    field: keyof ParameterRange,
    value: string | number
  ) => {
    const newRanges = [...parameterRanges];
    newRanges[index] = {
      ...newRanges[index],
      [field]: typeof value === 'string' ? parseFloat(value) || 0 : value,
    };
    onChange(newRanges);
  };

  const handleParameterChange = (index: number, paramName: string) => {
    const param = AVAILABLE_PARAMETERS.find((p) => p.name === paramName);
    if (!param) return;

    const newRanges = [...parameterRanges];
    newRanges[index] = {
      ...newRanges[index],
      parameter_name: paramName,
      min_value: param.defaultMin,
      max_value: param.defaultMax,
    };
    onChange(newRanges);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-800 dark:text-white">
          調整パラメータ
        </h3>
        <button
          onClick={handleAdd}
          className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors duration-200"
        >
          <Plus className="w-4 h-4" />
          パラメータ追加
        </button>
      </div>

      {parameterRanges.length === 0 ? (
        <div className="text-center py-8 text-gray-500 dark:text-gray-400">
          調整するパラメータを追加してください
        </div>
      ) : (
        <div className="space-y-3">
          {parameterRanges.map((range, index) => {
            const param = AVAILABLE_PARAMETERS.find(
              (p) => p.name === range.parameter_name
            );
            return (
              <div
                key={index}
                className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
              >
                <div className="flex items-start gap-4">
                  <div className="flex-1 grid grid-cols-1 md:grid-cols-4 gap-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        パラメータ
                      </label>
                      <select
                        value={range.parameter_name}
                        onChange={(e) =>
                          handleParameterChange(index, e.target.value)
                        }
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      >
                        {AVAILABLE_PARAMETERS.map((p) => (
                          <option key={p.name} value={p.name}>
                            {p.label}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        最小値 {param?.unit && `(${param.unit})`}
                      </label>
                      <input
                        type="number"
                        value={range.min_value}
                        onChange={(e) =>
                          handleChange(index, 'min_value', e.target.value)
                        }
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        step="0.1"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        最大値 {param?.unit && `(${param.unit})`}
                      </label>
                      <input
                        type="number"
                        value={range.max_value}
                        onChange={(e) =>
                          handleChange(index, 'max_value', e.target.value)
                        }
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        step="0.1"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        分割数
                      </label>
                      <input
                        type="number"
                        value={range.num_steps}
                        onChange={(e) =>
                          handleChange(index, 'num_steps', e.target.value)
                        }
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        min="2"
                        max="100"
                      />
                    </div>
                  </div>

                  <button
                    onClick={() => handleRemove(index)}
                    className="mt-6 p-2 text-red-600 hover:bg-red-100 dark:hover:bg-red-900 rounded-lg transition-colors duration-200"
                    title="削除"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      <div className="text-sm text-gray-600 dark:text-gray-400">
        <p>
          ※ グリッドサーチの場合、全パラメータの組み合わせを試行します（計算時間がかかる場合があります）
          <br />※ 統計的最適化の場合、効率的に最適なパラメータを探索します
        </p>
      </div>
    </div>
  );
}
