import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import type { SimulationResult } from '../types';

interface ResultsChartProps {
  results: SimulationResult[];
}

export default function ResultsChart({ results }: ResultsChartProps) {
  const monthNames = [
    '1月', '2月', '3月', '4月', '5月', '6月',
    '7月', '8月', '9月', '10月', '11月', '12月'
  ];

  const chartData = results.map((result) => ({
    month: monthNames[result.month - 1],
    全館空調: Math.round(result.central_total_kWh),
    個別空調: Math.round(result.local_total_kWh),
    総負荷: Math.round(result.total_load_kW),
    外気温: result.outdoor_temp,
  }));

  return (
    <div className="space-y-8">
      {/* Energy Consumption Chart */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <h3 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white">
          月別エネルギー消費量
        </h3>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" className="dark:opacity-20" />
            <XAxis
              dataKey="month"
              className="text-sm"
              stroke="#666"
            />
            <YAxis
              label={{ value: 'エネルギー消費量 (kWh)', angle: -90, position: 'insideLeft' }}
              stroke="#666"
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#fff',
                border: '1px solid #ccc',
                borderRadius: '8px',
              }}
            />
            <Legend />
            <Bar dataKey="全館空調" fill="#6366f1" />
            <Bar dataKey="個別空調" fill="#10b981" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Load and Temperature Chart */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <h3 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white">
          月別負荷と外気温
        </h3>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" className="dark:opacity-20" />
            <XAxis
              dataKey="month"
              className="text-sm"
              stroke="#666"
            />
            <YAxis
              yAxisId="left"
              label={{ value: '負荷 (kW)', angle: -90, position: 'insideLeft' }}
              stroke="#666"
            />
            <YAxis
              yAxisId="right"
              orientation="right"
              label={{ value: '温度 (°C)', angle: 90, position: 'insideRight' }}
              stroke="#666"
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#fff',
                border: '1px solid #ccc',
                borderRadius: '8px',
              }}
            />
            <Legend />
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="総負荷"
              stroke="#f59e0b"
              strokeWidth={2}
              dot={{ r: 4 }}
            />
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="外気温"
              stroke="#ef4444"
              strokeWidth={2}
              dot={{ r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Data Table */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 overflow-x-auto">
        <h3 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white">
          月別詳細データ
        </h3>
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead className="bg-gray-50 dark:bg-gray-900">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                月
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                外気温 (°C)
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                総負荷 (kW)
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                全館空調 (kWh)
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                個別空調 (kWh)
              </th>
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            {results.map((result) => (
              <tr key={result.month} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                  {result.month}月
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-900 dark:text-gray-100">
                  {result.outdoor_temp.toFixed(1)}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-900 dark:text-gray-100">
                  {result.total_load_kW.toFixed(1)}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-900 dark:text-gray-100">
                  {result.central_total_kWh.toLocaleString()}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-900 dark:text-gray-100">
                  {result.local_total_kWh.toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
