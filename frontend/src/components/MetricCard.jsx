import React from 'react';

export default function MetricCard({ title, value, subtext, icon: Icon, badgeText, badgeColor = 'emerald' }) {
  return (
    <div className="glass-panel" style={{ padding: '1.25rem', flex: 1, minWidth: '200px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
        <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#9ca3af', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          {title}
        </span>
        {Icon && (
          <div style={{
            background: 'rgba(255,255,255,0.05)',
            padding: '0.4rem',
            borderRadius: '8px',
            color: badgeColor === 'emerald' ? '#34d399' : badgeColor === 'cyan' ? '#38bdf8' : '#a78bfa'
          }}>
            <Icon size={18} />
          </div>
        )}
      </div>

      <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem', marginBottom: '0.25rem' }}>
        <span style={{ fontSize: '1.6rem', fontWeight: 800, color: '#ffffff' }}>
          {value}
        </span>
        {badgeText && (
          <span className={`badge badge-${badgeColor}`}>
            {badgeText}
          </span>
        )}
      </div>

      {subtext && (
        <p style={{ fontSize: '0.75rem', color: '#6b7280' }}>
          {subtext}
        </p>
      )}
    </div>
  );
}
