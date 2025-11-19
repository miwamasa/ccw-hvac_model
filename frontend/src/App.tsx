import { useState, useEffect } from 'react';
import { simulationApi } from './api/client';
import type {
  SimulationResponse,
  PresetInfo,
  PresetResponse,
  FloorSpec,
  EquipmentSpec,
  MonthlyCondition
} from './types';
import ResultsChart from './components/ResultsChart';
import PresetSelector from './components/PresetSelector';
import ConfigForm from './components/ConfigForm';
import MonthlyConditionsTable from './components/MonthlyConditionsTable';
import { Building2, Play, Loader2, Save, FileDown, Settings, BarChart3, Upload } from 'lucide-react';

type TabType = 'config' | 'simulate' | 'results';

function App() {
  const [presets, setPresets] = useState<PresetInfo[]>([]);
  const [selectedPreset, setSelectedPreset] = useState<string>('');
  const [activeTab, setActiveTab] = useState<TabType>('config');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<SimulationResponse | null>(null);
  const [error, setError] = useState<string>('');

  // Configuration state
  const [configName, setConfigName] = useState<string>('カスタム設定');
  const [configDescription, setConfigDescription] = useState<string>('');
  const [floorSpec, setFloorSpec] = useState<FloorSpec>({
    floor_area: 1000,
    ceiling_height: 3.0,
    wall_u_value: 0.3,
    window_area: 150,
    window_u_value: 1.5,
    solar_heat_gain_coef: 0.4,
  });
  const [equipmentSpec, setEquipmentSpec] = useState<EquipmentSpec>({
    lighting_power_density: 8.0,
    oa_equipment_power_density: 15.0,
    central_ahu_capacity: 100.0,
    central_ahu_fan_power: 15.0,
    central_chiller_capacity: 200.0,
    central_chiller_cop: 4.5,
    local_ac_capacity: 150.0,
    local_ac_cop: 3.5,
    local_ac_fan_power: 5.0,
  });
  const [monthlyConditions, setMonthlyConditions] = useState<MonthlyCondition[]>(
    Array.from({ length: 12 }, (_, i) => ({
      month: i + 1,
      outdoor_temp: 15,
      outdoor_humidity: 50,
      indoor_temp_setpoint: 22,
      indoor_humidity_setpoint: 45,
      supply_air_temp: 20,
      occupancy: 50,
      occupancy_rate: 0.85,
      operation_hours: 200,
    }))
  );

  // Load presets on mount
  useEffect(() => {
    const loadPresets = async () => {
      try {
        const data = await simulationApi.listPresets();
        setPresets(data.presets);
        if (data.presets.length > 0) {
          setSelectedPreset(data.presets[0].id);
        }
      } catch (err) {
        setError('プリセットの読み込みに失敗しました');
        console.error(err);
      }
    };
    loadPresets();
  }, []);

  // Load preset data when preset selection changes
  useEffect(() => {
    if (!selectedPreset) return;

    const loadPresetData = async () => {
      try {
        let preset: PresetResponse;
        if (selectedPreset === 'modern') {
          preset = await simulationApi.getModernPreset();
        } else {
          preset = await simulationApi.getOldPreset();
        }

        setConfigName(preset.name);
        setConfigDescription(preset.description);
        setFloorSpec(preset.floor_spec);
        setEquipmentSpec(preset.equipment_spec);
        setMonthlyConditions(preset.monthly_conditions);
      } catch (err) {
        console.error('Failed to load preset data:', err);
      }
    };

    loadPresetData();
  }, [selectedPreset]);

  const handleRunSimulation = async () => {
    setLoading(true);
    setError('');
    setResults(null);

    try {
      const response = await simulationApi.runSimulation({
        floor_spec: floorSpec,
        equipment_spec: equipmentSpec,
        monthly_conditions: monthlyConditions,
      });

      setResults(response);
      setActiveTab('results');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'シミュレーションの実行に失敗しました');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveConfig = async () => {
    try {
      const blob = await simulationApi.saveConfig({
        name: configName,
        description: configDescription,
        floor_spec: floorSpec,
        equipment_spec: equipmentSpec,
        monthly_conditions: monthlyConditions,
      });

      // Download file
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${configName}_${new Date().toISOString().slice(0, 10)}.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError('設定の保存に失敗しました');
      console.error(err);
    }
  };

  const handleSaveResults = async () => {
    try {
      const blob = await simulationApi.saveResults({
        floor_spec: floorSpec,
        equipment_spec: equipmentSpec,
        monthly_conditions: monthlyConditions,
      });

      // Download file
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `simulation_results_${new Date().toISOString().slice(0, 10)}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError('結果の保存に失敗しました');
      console.error(err);
    }
  };

  const handleLoadConfig = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      const text = await file.text();
      const config = JSON.parse(text);

      // Validate and load configuration
      if (config.name) setConfigName(config.name);
      if (config.description) setConfigDescription(config.description);
      if (config.floor_spec) setFloorSpec(config.floor_spec);
      if (config.equipment_spec) setEquipmentSpec(config.equipment_spec);
      if (config.monthly_conditions) setMonthlyConditions(config.monthly_conditions);

      setError('');
      setActiveTab('config');
    } catch (err) {
      setError('設定ファイルの読み込みに失敗しました');
      console.error(err);
    }

    // Reset file input
    event.target.value = '';
  };

  const handleMonthlyConditionChange = (
    index: number,
    field: keyof MonthlyCondition,
    value: string
  ) => {
    const newConditions = [...monthlyConditions];
    newConditions[index] = {
      ...newConditions[index],
      [field]: field === 'month' || field === 'occupancy'
        ? parseInt(value) || 0
        : parseFloat(value) || 0,
    };
    setMonthlyConditions(newConditions);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8 text-center">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Building2 className="w-12 h-12 text-indigo-600 dark:text-indigo-400" />
            <h1 className="text-4xl font-bold text-gray-800 dark:text-white">
              ビルエネルギーシミュレーター
            </h1>
          </div>
          <p className="text-lg text-gray-600 dark:text-gray-300">
            オフィスビルの空調システムのエネルギー消費をシミュレーションします
          </p>
        </div>

        {/* Main Content */}
        <div className="max-w-7xl mx-auto">
          {/* Preset Selector and Actions */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-8">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div className="flex-1 min-w-[200px]">
                <PresetSelector
                  presets={presets}
                  selectedPreset={selectedPreset}
                  onSelect={setSelectedPreset}
                />
              </div>
              <div className="flex gap-2">
                <label className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors duration-200 cursor-pointer">
                  <Upload className="w-5 h-5" />
                  設定読込
                  <input
                    type="file"
                    accept=".json"
                    onChange={handleLoadConfig}
                    className="hidden"
                  />
                </label>
                <button
                  onClick={handleSaveConfig}
                  className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors duration-200"
                >
                  <Save className="w-5 h-5" />
                  設定保存
                </button>
                {results && (
                  <button
                    onClick={handleSaveResults}
                    className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors duration-200"
                  >
                    <FileDown className="w-5 h-5" />
                    結果保存
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg mb-8">
            <div className="border-b border-gray-200 dark:border-gray-700">
              <nav className="flex -mb-px">
                <button
                  onClick={() => setActiveTab('config')}
                  className={`flex items-center gap-2 px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                    activeTab === 'config'
                      ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                      : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
                  }`}
                >
                  <Settings className="w-5 h-5" />
                  設定
                </button>
                <button
                  onClick={() => setActiveTab('simulate')}
                  className={`flex items-center gap-2 px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                    activeTab === 'simulate'
                      ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                      : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
                  }`}
                >
                  <Play className="w-5 h-5" />
                  シミュレーション
                </button>
                <button
                  onClick={() => setActiveTab('results')}
                  disabled={!results}
                  className={`flex items-center gap-2 px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                    activeTab === 'results'
                      ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                      : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 disabled:opacity-50 disabled:cursor-not-allowed'
                  }`}
                >
                  <BarChart3 className="w-5 h-5" />
                  結果
                </button>
              </nav>
            </div>

            <div className="p-6">
              {/* Config Tab */}
              {activeTab === 'config' && (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        設定名
                      </label>
                      <input
                        type="text"
                        value={configName}
                        onChange={(e) => setConfigName(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        説明
                      </label>
                      <input
                        type="text"
                        value={configDescription}
                        onChange={(e) => setConfigDescription(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      />
                    </div>
                  </div>

                  <ConfigForm
                    floorSpec={floorSpec}
                    equipmentSpec={equipmentSpec}
                    onFloorSpecChange={setFloorSpec}
                    onEquipmentSpecChange={setEquipmentSpec}
                  />

                  <MonthlyConditionsTable
                    conditions={monthlyConditions}
                    onChange={handleMonthlyConditionChange}
                  />
                </div>
              )}

              {/* Simulate Tab */}
              {activeTab === 'simulate' && (
                <div className="text-center py-8">
                  <button
                    onClick={handleRunSimulation}
                    disabled={loading}
                    className="inline-flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-semibold py-3 px-8 rounded-lg transition-colors duration-200 text-lg"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="w-6 h-6 animate-spin" />
                        実行中...
                      </>
                    ) : (
                      <>
                        <Play className="w-6 h-6" />
                        シミュレーション実行
                      </>
                    )}
                  </button>

                  {error && (
                    <div className="mt-6 p-4 bg-red-100 dark:bg-red-900/30 border border-red-400 dark:border-red-700 text-red-700 dark:text-red-400 rounded-lg max-w-2xl mx-auto">
                      {error}
                    </div>
                  )}

                  {results && (
                    <div className="mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                      <div className="bg-gray-50 dark:bg-gray-700 rounded-lg shadow p-6">
                        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                          年間全館空調
                        </h3>
                        <p className="text-2xl font-bold text-indigo-600 dark:text-indigo-400">
                          {results.summary.annual_central_total_kWh.toLocaleString()} kWh
                        </p>
                      </div>

                      <div className="bg-gray-50 dark:bg-gray-700 rounded-lg shadow p-6">
                        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                          年間個別空調
                        </h3>
                        <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                          {results.summary.annual_local_total_kWh.toLocaleString()} kWh
                        </p>
                      </div>

                      <div className="bg-gray-50 dark:bg-gray-700 rounded-lg shadow p-6">
                        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                          年間総負荷
                        </h3>
                        <p className="text-2xl font-bold text-orange-600 dark:text-orange-400">
                          {results.summary.annual_total_load_kWh.toLocaleString()} kWh
                        </p>
                      </div>

                      <div className="bg-gray-50 dark:bg-gray-700 rounded-lg shadow p-6">
                        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                          平均月次負荷
                        </h3>
                        <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                          {results.summary.average_monthly_load_kW.toFixed(1)} kW
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Results Tab */}
              {activeTab === 'results' && results && (
                <ResultsChart results={results.results} />
              )}

              {activeTab === 'results' && !results && (
                <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                  まずシミュレーションを実行してください
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-12 text-center text-gray-600 dark:text-gray-400">
          <p>© 2024 Building Energy Simulation v2.0</p>
        </div>
      </div>
    </div>
  );
}

export default App;
