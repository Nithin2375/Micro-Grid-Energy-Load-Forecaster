import React, { useState } from 'react';
import { createForecastRun } from '../services/api';
import { Cpu, Play, AlertTriangle, Layers, Sliders } from 'lucide-react';

export default function ModelTraining({ dataset, runs, onRunCreated, activeRun, setActiveRun }) {
  const [targetColumn, setTargetColumn] = useState(dataset?.timestamp_column === 'timestamp' && dataset?.columns?.includes('load_kW') ? 'load_kW' : (dataset?.columns?.[1] || ''));
  const [modelName, setModelName] = useState('RandomForest');
  const [horizon, setHorizon] = useState(24);
  const [imputeMissing, setImputeMissing] = useState(true);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  if (!dataset) {
    return (
      <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center' }}>
        <Cpu size={40} color="#a78bfa" style={{ marginBottom: '1rem' }} />
        <h2>No Active Dataset Loaded</h2>
        <p style={{ color: '#9ca3af' }}>Please load or upload a dataset first in the "Data & Quality" tab.</p>
      </div>
    );
  }

  const numericCols = dataset.columns?.filter(c => c !== dataset.timestamp_column) || [];

  const handleTrain = async (e) => {
    e.preventDefault();
    if (!targetColumn) {
      setError('Please select a target signal column.');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const payload = {
        dataset_id: dataset.id,
        target_column: targetColumn,
        model_name: modelName,
        horizon: Number(horizon),
        impute_missing: imputeMissing
      };
      const newRun = await createForecastRun(payload);
      onRunCreated(newRun);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to start forecast run');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      
      {/* Configure & Run Form */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
          <Sliders size={20} color="#34d399" />
          <h2 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Configure & Execute Time-Series Forecast Run</h2>
        </div>

        {error && (
          <div style={{ background: 'rgba(244,63,94,0.15)', border: '1px solid rgba(244,63,94,0.3)', color: '#f43f5e', padding: '0.75rem', borderRadius: '8px', fontSize: '0.825rem', marginBottom: '1rem' }}>
            <AlertTriangle size={16} style={{ display: 'inline', marginRight: '0.4rem' }} />
            {error}
          </div>
        )}

        <form onSubmit={handleTrain} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.25rem', alignItems: 'end' }}>
          
          <div>
            <label style={{ display: 'block', fontSize: '0.775rem', color: '#9ca3af', marginBottom: '0.35rem', fontWeight: 600 }}>
              Target Power Signal:
            </label>
            <select
              value={targetColumn}
              onChange={e => setTargetColumn(e.target.value)}
              className="form-select"
            >
              {numericCols.map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.775rem', color: '#9ca3af', marginBottom: '0.35rem', fontWeight: 600 }}>
              Forecasting Model Algorithm:
            </label>
            <select
              value={modelName}
              onChange={e => setModelName(e.target.value)}
              className="form-select"
            >
              <option value="RandomForest">Random Forest / Gradient Boosted Trees (ML)</option>
              <option value="LinearRegression">Ridge Linear Regression (Supervised Lags)</option>
              <option value="GradientBoosting">Pure Boosting Ensemble (Non-linear)</option>
              <option value="HoltWinters">Holt-Winters Exponential Smoothing</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.775rem', color: '#9ca3af', marginBottom: '0.35rem', fontWeight: 600 }}>
              Forecast Horizon (Steps):
            </label>
            <select
              value={horizon}
              onChange={e => setHorizon(e.target.value)}
              className="form-select"
            >
              <option value={12}>12 Hours (Half-Day)</option>
              <option value={24}>24 Hours (Next Day Peak Load)</option>
              <option value={48}>48 Hours (2-Day Multi-Horizon)</option>
              <option value={168}>168 Hours (7-Day Weekly Cycle)</option>
            </select>
          </div>

          <div>
            <div style={{ marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <input
                id="impute-checkbox"
                type="checkbox"
                checked={imputeMissing}
                onChange={e => setImputeMissing(e.target.checked)}
                style={{ cursor: 'pointer', accentColor: '#10b981' }}
              />
              <label htmlFor="impute-checkbox" style={{ fontSize: '0.75rem', color: '#d1d5db', cursor: 'pointer', userSelect: 'none' }}>
                Auto-Impute Missing Lags
              </label>
            </div>
            <button
              type="submit"
              className="btn-primary"
              disabled={loading}
              style={{ width: '100%', justifyContent: 'center' }}
            >
              <Play size={16} />
              {loading ? 'Training Model & Forecasting...' : 'Execute Forecast Pipeline'}
            </button>
          </div>

        </form>
      </div>

      {/* Model Performance Comparison Table */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Layers size={18} color="#38bdf8" /> Model Execution History & Performance Comparison Matrix
        </h3>
        <p style={{ fontSize: '0.75rem', color: '#9ca3af', marginBottom: '1rem' }}>
          Chronological holdout evaluation metrics comparing candidate models against seasonal naive baselines.
        </p>

        {runs && runs.length > 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', fontSize: '0.8rem', borderCollapse: 'collapse', whiteSpace: 'nowrap' }}>
              <thead>
                <tr style={{ background: 'rgba(0,0,0,0.3)', color: '#9ca3af', textAlign: 'left' }}>
                  <th style={{ padding: '0.6rem' }}>Run ID</th>
                  <th style={{ padding: '0.6rem' }}>Target Signal</th>
                  <th style={{ padding: '0.6rem' }}>Algorithm</th>
                  <th style={{ padding: '0.6rem' }}>Horizon</th>
                  <th style={{ padding: '0.6rem' }}>MAE (kW)</th>
                  <th style={{ padding: '0.6rem' }}>RMSE (kW)</th>
                  <th style={{ padding: '0.6rem' }}>sMAPE</th>
                  <th style={{ padding: '0.6rem' }}>WAPE</th>
                  <th style={{ padding: '0.6rem' }}>Baseline Imp.</th>
                  <th style={{ padding: '0.6rem' }}>Status</th>
                  <th style={{ padding: '0.6rem', textAlign: 'center' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {runs.map(run => {
                  const m = run.metrics || {};
                  const isActive = activeRun?.id === run.id;
                  return (
                    <tr key={run.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)', background: isActive ? 'rgba(16,185,129,0.08)' : 'transparent' }}>
                      <td style={{ padding: '0.55rem', fontWeight: 600 }}>#{run.id}</td>
                      <td style={{ padding: '0.55rem', color: '#38bdf8' }}>{run.target_column}</td>
                      <td style={{ padding: '0.55rem', fontWeight: 600, color: '#f9fafb' }}>{run.model_name}</td>
                      <td style={{ padding: '0.55rem' }}>{run.horizon} steps</td>
                      <td style={{ padding: '0.55rem', color: '#34d399', fontWeight: 700 }}>{m.mae !== undefined ? `${m.mae} kW` : 'N/A'}</td>
                      <td style={{ padding: '0.55rem', color: '#a78bfa' }}>{m.rmse !== undefined ? `${m.rmse} kW` : 'N/A'}</td>
                      <td style={{ padding: '0.55rem' }}>{m.smape !== undefined ? `${m.smape}%` : 'N/A'}</td>
                      <td style={{ padding: '0.55rem' }}>{m.wape !== undefined ? `${m.wape}%` : 'N/A'}</td>
                      <td style={{ padding: '0.55rem' }}>
                        {m.improvement_over_baseline_pct !== undefined ? (
                          <span className={`badge ${m.improvement_over_baseline_pct > 0 ? 'badge-emerald' : 'badge-amber'}`}>
                            {m.improvement_over_baseline_pct > 0 ? `+${m.improvement_over_baseline_pct}%` : `${m.improvement_over_baseline_pct}%`}
                          </span>
                        ) : 'N/A'}
                      </td>
                      <td style={{ padding: '0.55rem' }}>
                        <span className={`badge ${run.status === 'COMPLETED' ? 'badge-emerald' : 'badge-amber'}`}>
                          {run.status}
                        </span>
                      </td>
                      <td style={{ padding: '0.55rem', textAlign: 'center' }}>
                        <button
                          onClick={() => setActiveRun(run)}
                          className={isActive ? 'btn-primary' : 'btn-secondary'}
                          style={{ padding: '0.25rem 0.6rem', fontSize: '0.725rem' }}
                        >
                          {isActive ? 'Active Model' : 'View Forecasts'}
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <p style={{ color: '#9ca3af', textAlign: 'center', padding: '1.5rem' }}>
            No forecast runs created for this dataset yet. Use the form above to run your first model.
          </p>
        )}
      </div>

    </div>
  );
}
