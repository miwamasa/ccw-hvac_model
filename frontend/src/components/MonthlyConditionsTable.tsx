import type { MonthlyCondition } from '../types';

interface MonthlyConditionsTableProps {
  conditions: MonthlyCondition[];
  onChange: (index: number, field: keyof MonthlyCondition, value: string) => void;
}

export default function MonthlyConditionsTable({
  conditions,
  onChange,
}: MonthlyConditionsTableProps) {
  const monthNames = [
    '1月', '2月', '3月', '4月', '5月', '6月',
    '7月', '8月', '9月', '10月', '11月', '12月'
  ];

  const handleChange = (index: number, field: keyof MonthlyCondition, value: string) => {
    onChange(index, field, value);
  };

  return (
    <div className="overflow-x-auto">
      <h3 className="text-lg font-semibold mb-3 text-gray-800 dark:text-white">
        月別運用条件
      </h3>
      <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead className="bg-gray-50 dark:bg-gray-900">
          <tr>
            <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
              月
            </th>
            <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
              外気温<br/>(°C)
            </th>
            <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
              外気湿度<br/>(%)
            </th>
            <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
              室温設定<br/>(°C)
            </th>
            <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
              室内湿度<br/>設定(%)
            </th>
            <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
              給気温度<br/>(°C)
            </th>
            <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
              居住者数<br/>(人)
            </th>
            <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
              利用率
            </th>
            <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
              運転時間<br/>(h)
            </th>
          </tr>
        </thead>
        <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
          {conditions.map((condition, index) => (
            <tr key={condition.month} className="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td className="px-3 py-2 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-gray-100">
                {monthNames[index]}
              </td>
              <td className="px-3 py-2 whitespace-nowrap">
                <input
                  type="number"
                  value={condition.outdoor_temp}
                  onChange={(e) => handleChange(index, 'outdoor_temp', e.target.value)}
                  className="w-20 px-2 py-1 text-sm text-right border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  step="0.1"
                />
              </td>
              <td className="px-3 py-2 whitespace-nowrap">
                <input
                  type="number"
                  value={condition.outdoor_humidity}
                  onChange={(e) => handleChange(index, 'outdoor_humidity', e.target.value)}
                  className="w-20 px-2 py-1 text-sm text-right border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  step="1"
                />
              </td>
              <td className="px-3 py-2 whitespace-nowrap">
                <input
                  type="number"
                  value={condition.indoor_temp_setpoint}
                  onChange={(e) => handleChange(index, 'indoor_temp_setpoint', e.target.value)}
                  className="w-20 px-2 py-1 text-sm text-right border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  step="0.1"
                />
              </td>
              <td className="px-3 py-2 whitespace-nowrap">
                <input
                  type="number"
                  value={condition.indoor_humidity_setpoint}
                  onChange={(e) => handleChange(index, 'indoor_humidity_setpoint', e.target.value)}
                  className="w-20 px-2 py-1 text-sm text-right border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  step="1"
                />
              </td>
              <td className="px-3 py-2 whitespace-nowrap">
                <input
                  type="number"
                  value={condition.supply_air_temp}
                  onChange={(e) => handleChange(index, 'supply_air_temp', e.target.value)}
                  className="w-20 px-2 py-1 text-sm text-right border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  step="0.1"
                />
              </td>
              <td className="px-3 py-2 whitespace-nowrap">
                <input
                  type="number"
                  value={condition.occupancy}
                  onChange={(e) => handleChange(index, 'occupancy', e.target.value)}
                  className="w-20 px-2 py-1 text-sm text-right border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  step="1"
                />
              </td>
              <td className="px-3 py-2 whitespace-nowrap">
                <input
                  type="number"
                  value={condition.occupancy_rate}
                  onChange={(e) => handleChange(index, 'occupancy_rate', e.target.value)}
                  className="w-20 px-2 py-1 text-sm text-right border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  step="0.01"
                />
              </td>
              <td className="px-3 py-2 whitespace-nowrap">
                <input
                  type="number"
                  value={condition.operation_hours}
                  onChange={(e) => handleChange(index, 'operation_hours', e.target.value)}
                  className="w-20 px-2 py-1 text-sm text-right border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  step="1"
                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
