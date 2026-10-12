import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import DataManagement from './pages/DataManagement';
import ModelTraining from './pages/ModelTraining';
import ExportPredictions from './pages/ExportPredictions';
import { checkHealth, fetchDatasets, fetchForecastRuns, fetchPredictions, uploadDatasetFile } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [health, setHealth] = useState(null);
  const [datasets, setDatasets] = useState([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState(null);
  const [runs, setRuns] = useState([]);
  const [activeRun, setActiveRun] = useState(null);
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadPredictionsForRun = async (runId) => {
    try {
      const res = await fetchPredictions(runId);
      setPredictions(res.predictions || []);
    } catch (err) {
      console.error('Failed to load predictions:', err);
    }
  };

  const loadRunsForDataset = async (datasetId) => {
    try {
      const allRuns = await fetchForecastRuns();
      const datasetRuns = allRuns.filter(r => r.dataset_id === datasetId);
      setRuns(datasetRuns);

      if (datasetRuns.length > 0) {
        const completed = datasetRuns.find(r => r.status === 'COMPLETED') || datasetRuns[0];
        setActiveRun(completed);
      } else {
        setActiveRun(null);
        setPredictions([]);
      }
    } catch (err) {
      console.error('Failed to load runs:', err);
    }
  };

  const initApp = async () => {
    setLoading(true);
    try {
      const hData = await checkHealth();
      setHealth(hData);

      const dList = await fetchDatasets();
      setDatasets(dList);

      if (dList && dList.length > 0) {
        setSelectedDatasetId(dList[0].id);
      } else {
        // Automatically attempt to auto-seed sample data if no dataset exists
        try {
          const sampleCsvContent = `timestamp,load_kW,solar_generation_kW,wind_generation_kW,battery_soc,grid_import_kW\n` +
            Array.from({ length: 72 }, (_, i) => {
              const dt = new Date(2026, 0, 1, i).toISOString().replace('T', ' ').substring(0, 19);
              const hour = i % 24;
              const load = (120 + Math.sin(hour / 24 * Math.PI) * 150 + Math.random() * 20).toFixed(2);
              const solar = (hour >= 6 && hour <= 18 ? Math.sin((hour - 6) / 12 * Math.PI) * 220 : 0).toFixed(2);
              const wind = (50 + Math.sin(i / 10) * 40).toFixed(2);
              const battery = (60.0).toFixed(1);
              const grid = Math.max(0, load - solar - wind).toFixed(2);
              return `${dt},${load},${solar},${wind},${battery},${grid}`;
            }).join('\n');

          const blob = new Blob([sampleCsvContent], { type: 'text/csv' });
          const file = new File([blob], 'microgrid_sample_hourly.csv', { type: 'text/csv' });
          const autoDataset = await uploadDatasetFile(file);
          setDatasets([autoDataset]);
          setSelectedDatasetId(autoDataset.id);
        } catch (e) {
          console.warn('Auto-seed sample dataset skipped:', e);
        }
      }
    } catch (err) {
      console.error('App init error:', err);
    } finally {
      setLoading(false);
    }
  };

  // 1. Initial Load: Check health & fetch datasets
  useEffect(() => {
    initApp();
  }, []);

  // 2. When selectedDatasetId changes, load its runs
  useEffect(() => {
    if (selectedDatasetId) {
      loadRunsForDataset(selectedDatasetId);
    }
  }, [selectedDatasetId]);

  // 3. When activeRun changes, load its predictions
  useEffect(() => {
    if (activeRun?.id) {
      loadPredictionsForRun(activeRun.id);
    }
  }, [activeRun?.id]);

  const handleDatasetUploaded = (newDataset) => {
    setDatasets(prev => [newDataset, ...prev]);
    setSelectedDatasetId(newDataset.id);
    setActiveTab('data');
  };

  const handleRunCreated = (newRun) => {
    setRuns(prev => [newRun, ...prev]);
    setActiveRun(newRun);
    setActiveTab('dashboard');
  };

  const activeDataset = datasets.find(d => d.id === selectedDatasetId);

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        health={health}
        datasets={datasets}
        selectedDatasetId={selectedDatasetId}
        setSelectedDatasetId={setSelectedDatasetId}
        loading={loading}
      />

      <main style={{ flex: 1, padding: '0 1.5rem 2.5rem 1.5rem', maxWidth: '1400px', margin: '0 auto', width: '100%' }}>
        {activeTab === 'dashboard' && (
          <Dashboard
            dataset={activeDataset}
            activeRun={activeRun}
            predictions={predictions}
            runs={runs}
          />
        )}

        {activeTab === 'data' && (
          <DataManagement
            dataset={activeDataset}
            onDatasetUploaded={handleDatasetUploaded}
          />
        )}

        {activeTab === 'models' && (
          <ModelTraining
            dataset={activeDataset}
            runs={runs}
            onRunCreated={handleRunCreated}
            activeRun={activeRun}
            setActiveRun={setActiveRun}
          />
        )}

        {activeTab === 'export' && (
          <ExportPredictions
            activeRun={activeRun}
            predictions={predictions}
          />
        )}
      </main>

      <footer style={{ borderTop: '1px solid rgba(255,255,255,0.05)', padding: '1rem', textAlign: 'center', fontSize: '0.75rem', color: '#6b7280' }}>
        Predictive Modeling & Time-Series: AI-Driven Micro-Grid Renewable Energy Load Forecaster &copy; 2026
      </footer>
    </div>
  );
}
