import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import type { ActualData, SimulationResult, ComparisonMetrics } from '../types';

interface ComparisonChartProps {
  simulationResults: SimulationResult[];
  actualData: ActualData[];
  comparisonTarget: string;
  metrics?: ComparisonMetrics;
}

export default function ComparisonChart({
  simulationResults,
  actualData,
  comparisonTarget,
  metrics,
}: ComparisonChartProps) {
  // Prepare chart data
  const chartData = simulationResults.map((result) => {
    const actualItem = actualData.find((d) => d.month === result.month);

    let simulatedValue: number;
    let actualValue: number | undefined;

    if (comparisonTarget === 'total_kWh') {
      simulatedValue = result.central_total_kWh + result.local_total_kWh;
      actualValue = actualItem?.total_kWh;
    } else if (comparisonTarget === 'central_total_kWh') {
      simulatedValue = result.central_total_kWh;
      actualValue = actualItem?.central_total_kWh;
    } else {
      simulatedValue = result.local_total_kWh;
      actualValue = actualItem?.local_total_kWh;
    }

    return {
      month: `${result.month}月`,
      シミュレーション: Math.round(simulatedValue),
      実測: actualValue !== undefined ? Math.round(actualValue) : null,
    };
  });

  // Get target name in Japanese
  const targetNames: Record<string, string> = {
    total_kWh: '合計消費電力',
    central_total_kWh: '全館空調消費電力',
    local_total_kWh: '個別空調消費電力',
  };

  const targetName = targetNames[comparisonTarget] || comparisonTarget;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-800 dark:text-white">
          比較グラフ: {targetName}
        </h3>
      </div>

      {metrics && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 p-4 bg-gray-100 dark:bg-gray-800 rounded-lg">
          <div className="text-center">
            <div className="text-xs text-gray-600 dark:text-gray-400">RMSE</div>
            <div className="text-lg font-semibold text-gray-900 dark:text-white">
              {metrics.rmse.toFixed(2)}
            </div>
          </div>
          <div className="text-center">
            <div className="text-xs text-gray-600 dark:text-gray-400">MAE</div>
            <div className="text-lg font-semibold text-gray-900 dark:text-white">
              {metrics.mae.toFixed(2)}
            </div>
          </div>
          <div className="text-center">
            <div className="text-xs text-gray-600 dark:text-gray-400">MAPE</div>
            <div className="text-lg font-semibold text-gray-900 dark:text-white">
              {metrics.mape.toFixed(2)}%
            </div>
          </div>
          <div className="text-center">
            <div className="text-xs text-gray-600 dark:text-gray-400">R²</div>
            <div className="text-lg font-semibold text-gray-900 dark:text-white">
              {metrics.r_squared.toFixed(3)}
            </div>
          </div>
          <div className="text-center">
            <div className="text-xs text-gray-600 dark:text-gray-400">最大誤差</div>
            <div className="text-lg font-semibold text-gray-900 dark:text-white">
              {metrics.max_error.toFixed(2)}
            </div>
          </div>
          <div className="text-center">
            <div className="text-xs text-gray-600 dark:text-gray-400">最大誤差月</div>
            <div className="text-lg font-semibold text-gray-900 dark:text-white">
              {metrics.max_error_month}月
            </div>
          </div>
        </div>
      )}

      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg">
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis
              dataKey="month"
              stroke="#9CA3AF"
              style={{ fontSize: '14px' }}
            />
            <YAxis stroke="#9CA3AF" style={{ fontSize: '14px' }} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1F2937',
                border: '1px solid #374151',
                borderRadius: '0.5rem',
              }}
              labelStyle={{ color: '#F3F4F6' }}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="シミュレーション"
              stroke="#3B82F6"
              strokeWidth={2}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
            />
            <Line
              type="monotone"
              dataKey="実測"
              stroke="#EF4444"
              strokeWidth={2}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
              connectNulls={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="text-sm text-gray-600 dark:text-gray-400">
        <p>
          <strong>RMSE</strong> (Root Mean Square Error): 二乗平均平方根誤差
          <br />
          <strong>MAE</strong> (Mean Absolute Error): 平均絶対誤差
          <br />
          <strong>MAPE</strong> (Mean Absolute Percentage Error): 平均絶対パーセント誤差
          <br />
          <strong>R²</strong> (Coefficient of Determination): 決定係数（1に近いほど良い）
        </p>
      </div>
    </div>
  );
}
