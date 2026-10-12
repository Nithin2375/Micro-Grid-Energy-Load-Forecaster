import React, { useState } from 'react';
import { getExportUrl } from '../services/api';
import { Download, Table, BookOpen, ShieldAlert } from 'lucide-react';

export default function ExportPredictions({ activeRun, predictions }) {
  const [filterType, setFilterType] = useState('all');

  if (!activeRun || !predictions || predictions.length === 0) {
    return (
      <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center' }}>
        <Download size={40} color="#38bdf8" style={{ marginBottom: '1rem' }} />
        <h2>No Predictions Available for Export</h2>
        <p style={{ color: '#9ca3af' }}>Select or create an active forecast run from the "Model Training" tab to view and export predictions.</p>
      </div>
    );
  }

  const exportUrl = getExportUrl(activeRun.id);

  const filteredPredictions = predictions.filter(p => {
    if (filterType === 'future') return p.is_future;
    if (filterType === 'test') return !p.is_future;
    return true;
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      
      {/* Top Export Banner */}
      <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.15rem', fontWeight: 700 }}>Export Forecast Predictions & Metrics</h2>
          <p style={{ fontSize: '0.8rem', color: '#9ca3af' }}>
            Run #{activeRun.id} | Target: <strong style={{ color: '#38bdf8' }}>{activeRun.target_column}</strong> | Model: <strong style={{ color: '#34d399' }}>{activeRun.model_name}</strong> | Horizon: {activeRun.horizon} steps
          </p>
        </div>

        <a href={exportUrl} download className="btn-primary" style={{ textDecoration: 'none' }}>
          <Download size={18} /> Download CSV Predictions ({predictions.length} Rows)
        </a>
      </div>

      {/* Predictions Table */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.75rem' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Table size={18} color="#a78bfa" /> Generated Predictions & Future Forecast Matrix
          </h3>

          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              onClick={() => setFilterType('all')}
              className={filterType === 'all' ? 'btn-primary' : 'btn-secondary'}
              style={{ padding: '0.3rem 0.75rem', fontSize: '0.75rem' }}
            >
              All Records ({predictions.length})
            </button>
            <button
              onClick={() => setFilterType('test')}
              className={filterType === 'test' ? 'btn-primary' : 'btn-secondary'}
              style={{ padding: '0.3rem 0.75rem', fontSize: '0.75rem' }}
            >
              Test Holdout ({predictions.filter(p => !p.is_future).length})
            </button>
            <button
              onClick={() => setFilterType('future')}
              className={filterType === 'future' ? 'btn-primary' : 'btn-secondary'}
              style={{ padding: '0.3rem 0.75rem', fontSize: '0.75rem' }}
            >
              Future Horizon ({predictions.filter(p => p.is_future).length})
            </button>
          </div>
        </div>

        <div style={{ overflowX: 'auto', maxHeight: '420px' }}>
          <table style={{ width: '100%', fontSize: '0.8rem', borderCollapse: 'collapse', whiteSpace: 'nowrap' }}>
            <thead>
              <tr style={{ background: 'rgba(0,0,0,0.4)', color: '#9ca3af', position: 'sticky', top: 0 }}>
                <th style={{ padding: '0.55rem', textAlign: 'left' }}>Timestamp</th>
                <th style={{ padding: '0.55rem', textAlign: 'left' }}>Record Type</th>
                <th style={{ padding: '0.55rem', textAlign: 'right' }}>Actual ({activeRun.target_column})</th>
                <th style={{ padding: '0.55rem', textAlign: 'right' }}>Predicted ({activeRun.target_column})</th>
                <th style={{ padding: '0.55rem', textAlign: 'right' }}>95% Lower Bound</th>
                <th style={{ padding: '0.55rem', textAlign: 'right' }}>95% Upper Bound</th>
              </tr>
            </thead>
            <tbody>
              {filteredPredictions.map((p, idx) => (
                <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.03)', background: p.is_future ? 'rgba(139,92,246,0.05)' : 'transparent' }}>
                  <td style={{ padding: '0.5rem', fontWeight: 600, color: '#f9fafb' }}>{p.timestamp}</td>
                  <td style={{ padding: '0.5rem' }}>
                    <span className={`badge ${p.is_future ? 'badge-violet' : 'badge-emerald'}`}>
                      {p.is_future ? 'Future Forecast' : 'Historical Test'}
                    </span>
                  </td>
                  <td style={{ padding: '0.5rem', textAlign: 'right', color: p.actual_value !== null ? '#34d399' : '#6b7280' }}>
                    {p.actual_value !== null ? `${p.actual_value} kW` : 'N/A (Future)'}
                  </td>
                  <td style={{ padding: '0.5rem', textAlign: 'right', fontWeight: 700, color: '#a78bfa' }}>
                    {p.predicted_value} kW
                  </td>
                  <td style={{ padding: '0.5rem', textAlign: 'right', color: '#6b7280' }}>
                    {p.lower_bound !== null ? `${p.lower_bound} kW` : '-'}
                  </td>
                  <td style={{ padding: '0.5rem', textAlign: 'right', color: '#6b7280' }}>
                    {p.upper_bound !== null ? `${p.upper_bound} kW` : '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Safety Disclaimer & Viva Quick Ref */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.25rem' }}>
        <div style={{ background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.2)', padding: '1.25rem', borderRadius: '12px' }}>
          <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: '#fbbf24', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <ShieldAlert size={18} /> Operational Safety Disclaimer:
          </h4>
          <p style={{ fontSize: '0.775rem', color: '#d1d5db', lineHeight: 1.5 }}>
            Forecast values are model estimates generated for educational and decision-support purposes only. They must not be used as the sole basis for safety-critical microgrid switching or physical hardware control.
          </p>
        </div>

        <div style={{ background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.2)', padding: '1.25rem', borderRadius: '12px' }}>
          <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: '#34d399', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <BookOpen size={18} /> Student Project Viva Notice:
          </h4>
          <p style={{ fontSize: '0.775rem', color: '#d1d5db', lineHeight: 1.5 }}>
            Comprehensive project viva questions, architecture diagrams, forecasting methodologies, and dataset specifications are documented in the <code>docs/</code> folder of the repository.
          </p>
        </div>
      </div>

    </div>
  );
}
