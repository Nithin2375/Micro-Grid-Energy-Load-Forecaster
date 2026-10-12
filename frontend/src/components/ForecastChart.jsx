import React, { useState } from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid
} from 'recharts';

export default function ForecastChart({ predictions, targetSignal = 'load_kW', horizon = 24, modelName = 'Model' }) {
  const [showConfidence, setShowConfidence] = useState(true);
  const [showActuals, setShowActuals] = useState(true);

  if (!predictions || predictions.length === 0) {
    return (
      <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center', color: '#9ca3af' }}>
        <p>No forecast predictions loaded yet. Run a model from the "Model Training" tab to view chart visualizations.</p>
      </div>
    );
  }

  // Format data for Recharts
  const chartData = predictions.map(p => {
    const isFuture = p.is_future;
    return {
      timestamp: p.timestamp ? p.timestamp.replace('2026-', '') : '',
      actual: isFuture ? null : p.actual_value,
      predicted: p.predicted_value,
      lowerBound: (isFuture && showConfidence) ? p.lower_bound : null,
      upperBound: (isFuture && showConfidence) ? p.upper_bound : null,
      bounds: (isFuture && showConfidence) ? [p.lower_bound, p.upper_bound] : [null, null],
      isFuture
    };
  });

  return (
    <div className="glass-panel" style={{ padding: '1.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.75rem' }}>
        <div>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#f9fafb' }}>
            Time-Series Load & Forecast Visualization
          </h3>
          <p style={{ fontSize: '0.75rem', color: '#9ca3af' }}>
            Historical actuals vs {modelName} holdout test predictions and {horizon}-step future forecast horizon.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <label style={{ fontSize: '0.75rem', color: '#d1d5db', display: 'flex', alignItems: 'center', gap: '0.4rem', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={showActuals}
              onChange={e => setShowActuals(e.target.checked)}
            />
            Show Actuals
          </label>
          <label style={{ fontSize: '0.75rem', color: '#d1d5db', display: 'flex', alignItems: 'center', gap: '0.4rem', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={showConfidence}
              onChange={e => setShowConfidence(e.target.checked)}
            />
            Show 95% Confidence Band
          </label>
        </div>
      </div>

      <div style={{ width: '100%', height: 420 }}>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 10, right: 30, left: 10, bottom: 25 }}>
            <defs>
              <linearGradient id="futureGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.0} />
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
            <XAxis dataKey="timestamp" stroke="#6b7280" tick={{ fontSize: 11 }} angle={-25} textAnchor="end" />
            <YAxis stroke="#6b7280" tick={{ fontSize: 11 }} unit=" kW" domain={['auto', 'auto']} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#111827',
                borderColor: '#374151',
                borderRadius: '10px',
                color: '#ffffff',
                fontSize: '0.8rem'
              }}
              formatter={(val, name) => {
                if (val === null || val === undefined) return ['N/A', name];
                if (Array.isArray(val)) return [`[${val[0]}, ${val[1]}] kW`, '95% Bounds'];
                return [`${val} kW`, name];
              }}
            />
            <Legend wrapperStyle={{ fontSize: '0.8rem', paddingTop: '10px' }} />

            {/* Historical Actuals */}
            {showActuals && (
              <Line
                type="monotone"
                dataKey="actual"
                name={`Actual ${targetSignal}`}
                stroke="#10b981"
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 5 }}
              />
            )}

            {/* Model Predictions */}
            <Line
              type="monotone"
              dataKey="predicted"
              name={`${modelName} Predictions & Forecast`}
              stroke="#8b5cf6"
              strokeWidth={2.5}
              strokeDasharray="4 2"
              dot={false}
              activeDot={{ r: 6 }}
            />

            {/* Confidence Interval Area */}
            {showConfidence && (
              <Area
                type="monotone"
                dataKey="bounds"
                name="95% Forecast Interval"
                stroke="#a78bfa"
                fill="url(#futureGradient)"
              />
            )}
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      <div style={{ display: 'flex', justifyContent: 'center', gap: '1.5rem', marginTop: '1rem', fontSize: '0.75rem', color: '#9ca3af' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <span style={{ width: 12, height: 3, background: '#10b981', borderRadius: 2 }}></span> Measured Telemetry / Actuals
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <span style={{ width: 12, height: 3, background: '#8b5cf6', borderRadius: 2 }}></span> Holdout Test / Model Prediction
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <span style={{ width: 12, height: 12, background: 'rgba(139, 92, 246, 0.3)', border: '1px stroke #a78bfa', borderRadius: 2 }}></span> 95% Confidence Interval
        </div>
      </div>
    </div>
  );
}
