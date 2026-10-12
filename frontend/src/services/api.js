import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
});

export const checkHealth = async () => {
  try {
    const res = await api.get('/health');
    return res.data;
  } catch (err) {
    return { status: 'unreachable', error: err.message };
  }
};

export const fetchDatasets = async () => {
  const res = await api.get('/datasets');
  return res.data;
};

export const uploadDatasetFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const res = await api.post('/datasets/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
};

export const loadSampleDataset = async () => {
  const res = await api.post('/datasets/sample');
  return res.data;
};

export const fetchDatasetPreview = async (id, limit = 50) => {
  const res = await api.get(`/datasets/${id}/preview?limit=${limit}`);
  return res.data;
};

export const fetchDatasetQuality = async (id) => {
  const res = await api.get(`/datasets/${id}/quality`);
  return res.data;
};

export const fetchForecastRuns = async () => {
  const res = await api.get('/forecast-runs');
  return res.data;
};

export const createForecastRun = async (payload) => {
  const res = await api.post('/forecast-runs', payload);
  return res.data;
};

export const fetchPredictions = async (runId) => {
  const res = await api.get(`/forecast-runs/${runId}/predictions`);
  return res.data;
};

export const getExportUrl = (runId) => `${API_BASE_URL}/forecast-runs/${runId}/export`;

export default api;
