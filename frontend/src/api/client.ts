import axios from 'axios';
import type {
  SimulationRequest,
  SimulationResponse,
  PresetResponse,
  PresetInfo,
  ComparisonRequest,
  ComparisonResponse,
  CalibrationRequest,
  CalibrationResponse,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const simulationApi = {
  /**
   * Run simulation with custom settings
   */
  runSimulation: async (request: SimulationRequest): Promise<SimulationResponse> => {
    const response = await apiClient.post<SimulationResponse>('/simulate', request);
    return response.data;
  },

  /**
   * Get modern office preset
   */
  getModernPreset: async (): Promise<PresetResponse> => {
    const response = await apiClient.get<PresetResponse>('/presets/modern');
    return response.data;
  },

  /**
   * Get old office preset
   */
  getOldPreset: async (): Promise<PresetResponse> => {
    const response = await apiClient.get<PresetResponse>('/presets/old');
    return response.data;
  },

  /**
   * List available presets
   */
  listPresets: async (): Promise<{ presets: PresetInfo[] }> => {
    const response = await apiClient.get<{ presets: PresetInfo[] }>('/presets');
    return response.data;
  },

  /**
   * Save configuration as JSON file
   */
  saveConfig: async (config: PresetResponse): Promise<Blob> => {
    const response = await apiClient.post('/config/save', config, {
      responseType: 'blob',
    });
    return response.data;
  },

  /**
   * Save simulation results as CSV file
   */
  saveResults: async (request: SimulationRequest): Promise<Blob> => {
    const response = await apiClient.post('/results/save', request, {
      responseType: 'blob',
    });
    return response.data;
  },

  /**
   * Compare simulation with actual data
   */
  compare: async (request: ComparisonRequest): Promise<ComparisonResponse> => {
    const response = await apiClient.post<ComparisonResponse>('/compare', request);
    return response.data;
  },

  /**
   * Calibrate parameters to match actual data
   */
  calibrate: async (request: CalibrationRequest): Promise<CalibrationResponse> => {
    const response = await apiClient.post<CalibrationResponse>('/calibrate', request);
    return response.data;
  },

  /**
   * Health check
   */
  healthCheck: async (): Promise<{ status: string }> => {
    const response = await apiClient.get<{ status: string }>('/health');
    return response.data;
  },
};

export default apiClient;
