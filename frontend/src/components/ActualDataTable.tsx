import { Upload } from 'lucide-react';
import type { ActualData } from '../types';

interface ActualDataTableProps {
  actualData: ActualData[];
  onChange: (data: ActualData[]) => void;
  onCSVImport: (event: React.ChangeEvent<HTMLInputElement>) => void;
}

export default function ActualDataTable({
  actualData,
  onChange,
  onCSVImport,
}: ActualDataTableProps) {
  const handleChange = (index: number, field: keyof ActualData, value: string) => {
    const newData = [...actualData];
    const numValue = value === '' ? undefined : parseFloat(value);
    newData[index] = {
      ...newData[index],
      [field]: numValue,
    };
    onChange(newData);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-800 dark:text-white">
          実測データ
        </h3>
        <label className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors duration-200 cursor-pointer">
          <Upload className="w-4 h-4" />
          CSVインポート
          <input
            type="file"
            accept=".csv"
            onChange={onCSVImport}
            className="hidden"
          />
        </label>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full border border-gray-300 dark:border-gray-600">
          <thead className="bg-gray-100 dark:bg-gray-700">
            <tr>
              <th className="px-4 py-2 text-left text-sm font-medium text-gray-700 dark:text-gray-300 border-b border-gray-300 dark:border-gray-600">
                月
              </th>
              <th className="px-4 py-2 text-left text-sm font-medium text-gray-700 dark:text-gray-300 border-b border-gray-300 dark:border-gray-600">
                全館空調 (kWh)
              </th>
              <th className="px-4 py-2 text-left text-sm font-medium text-gray-700 dark:text-gray-300 border-b border-gray-300 dark:border-gray-600">
                個別空調 (kWh)
              </th>
              <th className="px-4 py-2 text-left text-sm font-medium text-gray-700 dark:text-gray-300 border-b border-gray-300 dark:border-gray-600">
                合計 (kWh)
              </th>
            </tr>
          </thead>
          <tbody>
            {actualData.map((data, index) => (
              <tr
                key={data.month}
                className="hover:bg-gray-50 dark:hover:bg-gray-700"
              >
                <td className="px-4 py-2 text-sm text-gray-900 dark:text-gray-100 border-b border-gray-200 dark:border-gray-600">
                  {data.month}月
                </td>
                <td className="px-4 py-2 border-b border-gray-200 dark:border-gray-600">
                  <input
                    type="number"
                    value={data.central_total_kWh ?? ''}
                    onChange={(e) =>
                      handleChange(index, 'central_total_kWh', e.target.value)
                    }
                    className="w-full px-2 py-1 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
                    placeholder="未入力"
                    step="0.1"
                  />
                </td>
                <td className="px-4 py-2 border-b border-gray-200 dark:border-gray-600">
                  <input
                    type="number"
                    value={data.local_total_kWh ?? ''}
                    onChange={(e) =>
                      handleChange(index, 'local_total_kWh', e.target.value)
                    }
                    className="w-full px-2 py-1 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
                    placeholder="未入力"
                    step="0.1"
                  />
                </td>
                <td className="px-4 py-2 border-b border-gray-200 dark:border-gray-600">
                  <input
                    type="number"
                    value={data.total_kWh ?? ''}
                    onChange={(e) =>
                      handleChange(index, 'total_kWh', e.target.value)
                    }
                    className="w-full px-2 py-1 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
                    placeholder="未入力"
                    step="0.1"
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="text-sm text-gray-600 dark:text-gray-400">
        <p>※ CSVファイルは以下の形式で作成してください：</p>
        <code className="block mt-1 p-2 bg-gray-100 dark:bg-gray-700 rounded">
          month,central_total_kWh,local_total_kWh,total_kWh<br />
          1,12000,10000,22000<br />
          2,11000,9000,20000<br />
          ...
        </code>
      </div>
    </div>
  );
}
