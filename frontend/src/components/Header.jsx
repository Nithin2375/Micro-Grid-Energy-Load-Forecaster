import React from 'react';
import { Zap, Activity, Database, Cpu, Download, ShieldCheck, AlertCircle } from 'lucide-react';

export default function Header({ activeTab, setActiveTab, health, datasets, selectedDatasetId, setSelectedDatasetId, loading }) {
  const isHealthy = health?.status === 'healthy';

  return (
    <header className="glass-panel" style={{ borderRadius: 0, borderTop: 0, borderLeft: 0, borderRight: 0, marginBottom: '1.5rem', padding: '0.85rem 1.5rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        
        {/* Title & Brand */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            background: 'linear-gradient(135deg, #10b981 0%, #06b6d4 100%)',
            padding: '0.55rem',
            borderRadius: '12px',
            display: 'flex',
            boxShadow: '0 0 15px rgba(16, 185, 129, 0.4)'
          }}>
            <Zap size={22} color="#ffffff" />
          </div>
          <div>
            <h1 style={{ fontSize: '1.15rem', fontWeight: 700, background: 'linear-gradient(90deg, #ffffff 0%, #9ca3af 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              Micro-Grid Energy Load Forecaster
            </h1>
            <p style={{ fontSize: '0.75rem', color: '#9ca3af' }}>AI Predictive Modeling & Decision Support System</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav style={{ display: 'flex', gap: '0.5rem', background: 'rgba(0,0,0,0.2)', padding: '0.25rem', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.05)' }}>
          <button
            onClick={() => setActiveTab('dashboard')}
            className={activeTab === 'dashboard' ? 'btn-primary' : 'btn-secondary'}
            style={{ padding: '0.45rem 0.9rem', fontSize: '0.825rem' }}
          >
            <Activity size={16} /> Overview & Forecasts
          </button>
          <button
            onClick={() => setActiveTab('data')}
            className={activeTab === 'data' ? 'btn-primary' : 'btn-secondary'}
            style={{ padding: '0.45rem 0.9rem', fontSize: '0.825rem' }}
          >
            <Database size={16} /> Data & Quality
          </button>
          <button
            onClick={() => setActiveTab('models')}
            className={activeTab === 'models' ? 'btn-primary' : 'btn-secondary'}
            style={{ padding: '0.45rem 0.9rem', fontSize: '0.825rem' }}
          >
            <Cpu size={16} /> Model Training
          </button>
          <button
            onClick={() => setActiveTab('export')}
            className={activeTab === 'export' ? 'btn-primary' : 'btn-secondary'}
            style={{ padding: '0.45rem 0.9rem', fontSize: '0.825rem' }}
          >
            <Download size={16} /> Export Results
          </button>
        </nav>

        {/* Dataset Selector & API Health */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {datasets && datasets.length > 0 && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ fontSize: '0.75rem', color: '#9ca3af' }}>Active Dataset:</span>
              <select
                value={selectedDatasetId || ''}
                onChange={(e) => setSelectedDatasetId(Number(e.target.value))}
                className="form-select"
                style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem', minWidth: '160px' }}
              >
                {datasets.map(d => (
                  <option key={d.id} value={d.id}>
                    {d.original_filename} ({d.row_count} rows)
                  </option>
                ))}
              </select>
            </div>
          )}

          <div className={`badge ${loading ? 'badge-cyan' : (isHealthy ? 'badge-emerald' : 'badge-amber')}`}>
            {isHealthy ? <ShieldCheck size={14} /> : <AlertCircle size={14} />}
            {loading ? 'Syncing...' : (isHealthy ? 'API Active' : 'API Connecting...')}
          </div>
        </div>

      </div>
    </header>
  );
}
