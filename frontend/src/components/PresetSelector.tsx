import type { PresetInfo } from '../types';

interface PresetSelectorProps {
  presets: PresetInfo[];
  selectedPreset: string;
  onSelect: (presetId: string) => void;
}

export default function PresetSelector({
  presets,
  selectedPreset,
  onSelect,
}: PresetSelectorProps) {
  return (
    <div>
      <label
        htmlFor="preset-select"
        className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
      >
        プリセット設定
      </label>
      <select
        id="preset-select"
        value={selectedPreset}
        onChange={(e) => onSelect(e.target.value)}
        className="w-full px-4 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
      >
        {presets.map((preset) => (
          <option key={preset.id} value={preset.id}>
            {preset.name} - {preset.description}
          </option>
        ))}
      </select>
    </div>
  );
}
