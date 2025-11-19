import { useState, useEffect } from 'react';
import { simulationApi } from './api/client';
import type { SimulationResponse, PresetInfo, PresetResponse } from './types';
import ResultsChart from './components/ResultsChart';
import PresetSelector from './components/PresetSelector';
import { Building2, Play, Loader2 } from 'lucide-react';

function App() {
  const [presets, setPresets] = useState<PresetInfo[]>([]);
  const [selectedPreset, setSelectedPreset] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<SimulationResponse | null>(null);
  const [error, setError] = useState<string>('');

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

  const handleRunSimulation = async () => {
    if (!selectedPreset) return;

    setLoading(true);
    setError('');
    setResults(null);

    try {
      // Get preset data
      let preset: PresetResponse;
      if (selectedPreset === 'modern') {
        preset = await simulationApi.getModernPreset();
      } else {
        preset = await simulationApi.getOldPreset();
      }

      // Run simulation
      const response = await simulationApi.runSimulation({
        floor_spec: preset.floor_spec,
        equipment_spec: preset.equipment_spec,
        monthly_conditions: preset.monthly_conditions,
      });

      setResults(response);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'シミュレーションの実行に失敗しました');
      console.error(err);
    } finally {
      setLoading(false);
    }
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
        <div className="max-w-6xl mx-auto">
          {/* Control Panel */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-8">
            <h2 className="text-2xl font-semibold mb-4 text-gray-800 dark:text-white">
              設定
            </h2>

            <div className="space-y-4">
              <PresetSelector
                presets={presets}
                selectedPreset={selectedPreset}
                onSelect={setSelectedPreset}
              />

              <button
                onClick={handleRunSimulation}
                disabled={loading || !selectedPreset}
                className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    実行中...
                  </>
                ) : (
                  <>
                    <Play className="w-5 h-5" />
                    シミュレーション実行
                  </>
                )}
              </button>
            </div>

            {error && (
              <div className="mt-4 p-4 bg-red-100 dark:bg-red-900/30 border border-red-400 dark:border-red-700 text-red-700 dark:text-red-400 rounded-lg">
                {error}
              </div>
            )}
          </div>

          {/* Results */}
          {results && (
            <div className="space-y-8">
              {/* Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
                  <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                    年間全館空調
                  </h3>
                  <p className="text-2xl font-bold text-indigo-600 dark:text-indigo-400">
                    {results.summary.annual_central_total_kWh.toLocaleString()} kWh
                  </p>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
                  <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                    年間個別空調
                  </h3>
                  <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                    {results.summary.annual_local_total_kWh.toLocaleString()} kWh
                  </p>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
                  <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                    年間総負荷
                  </h3>
                  <p className="text-2xl font-bold text-orange-600 dark:text-orange-400">
                    {results.summary.annual_total_load_kWh.toLocaleString()} kWh
                  </p>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
                  <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                    平均月次負荷
                  </h3>
                  <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                    {results.summary.average_monthly_load_kW.toFixed(1)} kW
                  </p>
                </div>
              </div>

              {/* Charts */}
              <ResultsChart results={results.results} />
            </div>
          )}
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
