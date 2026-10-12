import React from 'react';
import MetricCard from '../components/MetricCard';
import ForecastChart from '../components/ForecastChart';
import { Activity, Zap, TrendingUp, CheckCircle, Clock, ShieldCheck, Sun, Wind, BatteryCharging } from 'lucide-react';

export default function Dashboard({ dataset, activeRun, predictions, runs }) {
  if (!dataset) {
    return (
      <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center' }}>
        <Zap size={40} color="#10b981" style={{ marginBottom: '1rem' }} />
        <h2>No Dataset Selected</h2>
        <p style={{ color: '#9ca3af', marginTop: '0.5rem' }}>
          Please upload a CSV dataset or click "Load Sample Data" in the <strong>Data & Quality</strong> tab to get started.
        </p>
      </div>
    );
  }

  const metrics = activeRun?.metrics || {};
  const quality = dataset.quality || {};

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      
      {/* KPI Row */}
      <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
        <MetricCard
          title="Dataset Coverage"
          value={`${dataset.row_count} Records`}
          subtext={`${dataset.start_time || 'N/A'} to ${dataset.end_time || 'N/A'}`}
          icon={Clock}
          badgeText={dataset.time_interval || 'Hourly'}
          badgeColor="emerald"
        />

        <MetricCard
          title="Data Quality Audit"
          value={`${quality.quality_score || 95}%`}
          subtext={`${quality.missing_values_count || 0} missing cells detected`}
          icon={ShieldCheck}
          badgeText={quality.quality_score >= 90 ? 'Excellent' : 'Needs Review'}
          badgeColor={quality.quality_score >= 90 ? 'emerald' : 'amber'}
        />

        <MetricCard
          title="Active Model MAE"
          value={metrics.mae !== undefined ? `${metrics.mae} kW` : 'N/A'}
          subtext={`Mean Absolute Error on Holdout Test Set`}
          icon={TrendingUp}
          badgeText={metrics.improvement_over_baseline_pct !== undefined ? `+${metrics.improvement_over_baseline_pct}% vs Baseline` : 'Active'}
          badgeColor="cyan"
        />

        <MetricCard
          title="Forecast Horizon"
          value={`${activeRun?.horizon || 24} Steps`}
          subtext={`Model: ${activeRun?.model_name || 'RandomForest'}${runs && runs.length > 0 ? ` (${runs.length} runs)` : ''}`}
          icon={Activity}
          badgeText={activeRun?.target_column || 'load_kW'}
          badgeColor="violet"
        />
      </div>

      {/* Main Interactive Forecast Chart */}
      <ForecastChart
        predictions={predictions}
        targetSignal={activeRun?.target_column || 'load_kW'}
        horizon={activeRun?.horizon || 24}
        modelName={activeRun?.model_name || 'RandomForest'}
      />

      {/* Bottom Summary Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
        
        {/* Model Evaluation Summary */}
        <div className="glass-panel" style={{ padding: '1.25rem' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <CheckCircle size={18} color="#34d399" /> Holdout Evaluation Metrics
          </h3>
          <table style={{ width: '100%', fontSize: '0.825rem', borderCollapse: 'collapse' }}>
            <tbody>
              <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                <td style={{ padding: '0.5rem 0', color: '#9ca3af' }}>Mean Absolute Error (MAE)</td>
                <td style={{ textAlign: 'right', fontWeight: 700, color: '#f9fafb' }}>{metrics.mae !== undefined ? `${metrics.mae} kW` : 'N/A'}</td>
              </tr>
              <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                <td style={{ padding: '0.5rem 0', color: '#9ca3af' }}>Root Mean Squared Error (RMSE)</td>
                <td style={{ textAlign: 'right', fontWeight: 700, color: '#f9fafb' }}>{metrics.rmse !== undefined ? `${metrics.rmse} kW` : 'N/A'}</td>
              </tr>
              <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                <td style={{ padding: '0.5rem 0', color: '#9ca3af' }}>Symmetric MAPE (sMAPE)</td>
                <td style={{ textAlign: 'right', fontWeight: 700, color: '#f9fafb' }}>{metrics.smape !== undefined ? `${metrics.smape}%` : 'N/A'}</td>
              </tr>
              <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                <td style={{ padding: '0.5rem 0', color: '#9ca3af' }}>Weighted APE (WAPE)</td>
                <td style={{ textAlign: 'right', fontWeight: 700, color: '#f9fafb' }}>{metrics.wape !== undefined ? `${metrics.wape}%` : 'N/A'}</td>
              </tr>
              <tr>
                <td style={{ padding: '0.5rem 0', color: '#9ca3af' }}>Baseline Seasonal MAE</td>
                <td style={{ textAlign: 'right', fontWeight: 700, color: '#fbbf24' }}>{metrics.baseline_mae !== undefined ? `${metrics.baseline_mae} kW` : 'N/A'}</td>
              </tr>
            </tbody>
          </table>
        </div>

        {/* Micro-Grid Energy Signals Status */}
        <div className="glass-panel" style={{ padding: '1.25rem' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Zap size={18} color="#38bdf8" /> Micro-Grid Signals Summary
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.5rem 0.75rem', background: 'rgba(0,0,0,0.2)', borderRadius: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.825rem' }}>
                <Zap size={16} color="#34d399" /> <span>Target Power Signal:</span>
              </div>
              <span className="badge badge-emerald">{activeRun?.target_column || 'load_kW'}</span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.5rem 0.75rem', background: 'rgba(0,0,0,0.2)', borderRadius: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.825rem' }}>
                <Sun size={16} color="#fbbf24" /> <span>Solar Generation:</span>
              </div>
              <span className="badge badge-amber">{dataset.columns?.includes('solar_generation_kW') ? 'Available' : 'N/A'}</span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.5rem 0.75rem', background: 'rgba(0,0,0,0.2)', borderRadius: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.825rem' }}>
                <Wind size={16} color="#38bdf8" /> <span>Wind Generation:</span>
              </div>
              <span className="badge badge-cyan">{dataset.columns?.includes('wind_generation_kW') ? 'Available' : 'N/A'}</span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.5rem 0.75rem', background: 'rgba(0,0,0,0.2)', borderRadius: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.825rem' }}>
                <BatteryCharging size={16} color="#a78bfa" /> <span>Battery State of Charge:</span>
              </div>
              <span className="badge badge-violet">{dataset.columns?.includes('battery_soc') ? 'Available' : 'N/A'}</span>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
