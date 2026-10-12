import React, { useState, useEffect } from 'react';
import { uploadDatasetFile, loadSampleDataset, fetchDatasetPreview, fetchDatasetQuality } from '../services/api';
import { UploadCloud, CheckCircle, AlertTriangle, Table, Sparkles } from 'lucide-react';

export default function DataManagement({ dataset, onDatasetUploaded }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [preview, setPreview] = useState(null);
  const [quality, setQuality] = useState(null);

  const loadDetails = async (id) => {
    try {
      const prevData = await fetchDatasetPreview(id);
      const qualData = await fetchDatasetQuality(id);
      setPreview(prevData);
      setQuality(qualData);
    } catch (err) {
      console.error('Failed to load dataset details:', err);
    }
  };

  useEffect(() => {
    if (dataset?.id) {
      loadDetails(dataset.id);
    }
  }, [dataset?.id]);

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setLoading(true);
    setError(null);
    try {
      const newDataset = await uploadDatasetFile(file);
      onDatasetUploaded(newDataset);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'File upload failed');
    } finally {
      setLoading(false);
    }
  };

  const handleLoadSample = async () => {
    setLoading(true);
    setError(null);
    try {
      // Primary: Direct backend sample seed endpoint
      const newDataset = await loadSampleDataset();
      onDatasetUploaded(newDataset);
    } catch (err) {
      try {
        // Fallback: Static asset upload
        const res = await fetch('/data/sample/microgrid_sample_hourly.csv');
        const text = await res.text();
        const blob = new Blob([text], { type: 'text/csv' });
        const sampleFile = new File([blob], 'microgrid_sample_hourly.csv', { type: 'text/csv' });
        const newDataset = await uploadDatasetFile(sampleFile);
        onDatasetUploaded(newDataset);
      } catch {
        setError(err.response?.data?.detail || err.message || 'Upload sample data failed. Please choose a CSV file directly.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      
      {/* Upload Box & Sample Action */}
      <div className="glass-panel" style={{ padding: '2rem', textAlign: 'center' }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.5rem' }}>
          Micro-Grid Dataset Ingestion & Quality Audit
        </h2>
        <p style={{ color: '#9ca3af', fontSize: '0.85rem', marginBottom: '1.5rem' }}>
          Upload a time-series CSV/Excel dataset containing timestamp and numeric signal columns (e.g. load_kW, solar_generation_kW).
        </p>

        {error && (
          <div style={{ background: 'rgba(244,63,94,0.15)', border: '1px solid rgba(244,63,94,0.3)', color: '#f43f5e', padding: '0.75rem', borderRadius: '8px', fontSize: '0.825rem', marginBottom: '1rem' }}>
            <AlertTriangle size={16} style={{ display: 'inline', marginRight: '0.4rem' }} />
            {error}
          </div>
        )}

        <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          <label className="btn-primary" style={{ cursor: 'pointer' }}>
            <UploadCloud size={18} />
            {loading ? 'Processing Upload...' : 'Choose CSV / Excel File'}
            <input type="file" accept=".csv,.xlsx" onChange={handleFileUpload} style={{ display: 'none' }} disabled={loading} />
          </label>

          <button onClick={handleLoadSample} className="btn-secondary" disabled={loading}>
            <Sparkles size={18} color="#fbbf24" /> Load Sample Micro-Grid Dataset
          </button>
        </div>
      </div>

      {/* Quality Audit Summary */}
      {quality && (
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <CheckCircle size={20} color="#34d399" /> Data Quality Audit Summary
              </h3>
              <p style={{ fontSize: '0.75rem', color: '#9ca3af' }}>
                Automated validation of timestamps, intervals, duplicates, missing values, and signal bounds.
              </p>
            </div>
            <div className={`badge ${quality.quality_score >= 90 ? 'badge-emerald' : 'badge-amber'}`} style={{ fontSize: '0.9rem', padding: '0.4rem 0.8rem' }}>
              Quality Score: {quality.quality_score}%
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
            <div style={{ background: 'rgba(0,0,0,0.2)', padding: '0.85rem', borderRadius: '10px' }}>
              <span style={{ fontSize: '0.75rem', color: '#9ca3af' }}>Sampling Frequency</span>
              <p style={{ fontSize: '1rem', fontWeight: 700, color: '#38bdf8' }}>{quality.detected_frequency}</p>
            </div>
            <div style={{ background: 'rgba(0,0,0,0.2)', padding: '0.85rem', borderRadius: '10px' }}>
              <span style={{ fontSize: '0.75rem', color: '#9ca3af' }}>Missing Values</span>
              <p style={{ fontSize: '1rem', fontWeight: 700, color: quality.missing_values_count === 0 ? '#34d399' : '#fbbf24' }}>
                {quality.missing_values_count} cells ({quality.missing_values_pct}%)
              </p>
            </div>
            <div style={{ background: 'rgba(0,0,0,0.2)', padding: '0.85rem', borderRadius: '10px' }}>
              <span style={{ fontSize: '0.75rem', color: '#9ca3af' }}>Duplicate Timestamps</span>
              <p style={{ fontSize: '1rem', fontWeight: 700, color: quality.duplicate_timestamps === 0 ? '#34d399' : '#f43f5e' }}>
                {quality.duplicate_timestamps}
              </p>
            </div>
            <div style={{ background: 'rgba(0,0,0,0.2)', padding: '0.85rem', borderRadius: '10px' }}>
              <span style={{ fontSize: '0.75rem', color: '#9ca3af' }}>Numeric Signal Columns</span>
              <p style={{ fontSize: '1rem', fontWeight: 700, color: '#a78bfa' }}>{quality.numeric_columns?.length || 0} signals</p>
            </div>
          </div>

          {/* Validation Warnings */}
          {quality.warnings && quality.warnings.length > 0 && (
            <div style={{ background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.2)', borderRadius: '10px', padding: '1rem', marginBottom: '1rem' }}>
              <h4 style={{ fontSize: '0.85rem', fontWeight: 600, color: '#fbbf24', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <AlertTriangle size={16} /> Validation Audit Notes & Warnings:
              </h4>
              <ul style={{ paddingLeft: '1.2rem', fontSize: '0.8rem', color: '#d1d5db' }}>
                {quality.warnings.map((w, idx) => (
                  <li key={idx} style={{ marginBottom: '0.25rem' }}>{w}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Column Summary Statistics Table */}
          {quality.column_stats && (
            <div>
              <h4 style={{ fontSize: '0.85rem', fontWeight: 600, color: '#9ca3af', marginBottom: '0.5rem' }}>Signal Statistics:</h4>
              <table style={{ width: '100%', fontSize: '0.8rem', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ background: 'rgba(0,0,0,0.3)', color: '#9ca3af', textAlign: 'left' }}>
                    <th style={{ padding: '0.5rem' }}>Signal Column</th>
                    <th style={{ padding: '0.5rem' }}>Missing Count</th>
                    <th style={{ padding: '0.5rem' }}>Min Value</th>
                    <th style={{ padding: '0.5rem' }}>Mean Value</th>
                    <th style={{ padding: '0.5rem' }}>Max Value</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(quality.column_stats).map(([col, stats]) => (
                    <tr key={col} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                      <td style={{ padding: '0.5rem', fontWeight: 600, color: '#f9fafb' }}>{col}</td>
                      <td style={{ padding: '0.5rem', color: stats.missing_count > 0 ? '#fbbf24' : '#6b7280' }}>{stats.missing_count}</td>
                      <td style={{ padding: '0.5rem', color: '#38bdf8' }}>{stats.min}</td>
                      <td style={{ padding: '0.5rem', color: '#34d399' }}>{stats.mean}</td>
                      <td style={{ padding: '0.5rem', color: '#a78bfa' }}>{stats.max}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Dataset Preview Table */}
      {preview && preview.preview && (
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Table size={18} color="#38bdf8" /> Dataset Record Preview (First 50 Rows)
          </h3>
          <div style={{ overflowX: 'auto', maxHeight: '350px' }}>
            <table style={{ width: '100%', fontSize: '0.775rem', borderCollapse: 'collapse', whiteSpace: 'nowrap' }}>
              <thead>
                <tr style={{ background: 'rgba(0,0,0,0.4)', color: '#9ca3af', position: 'sticky', top: 0 }}>
                  {preview.columns?.map(c => (
                    <th key={c} style={{ padding: '0.5rem 0.75rem', textAlign: 'left' }}>{c}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {preview.preview.map((row, idx) => (
                  <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.03)', background: idx % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.01)' }}>
                    {preview.columns?.map(c => (
                      <td key={c} style={{ padding: '0.45rem 0.75rem' }}>{row[c]}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

    </div>
  );
}
