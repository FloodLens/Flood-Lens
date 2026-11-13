import React from 'react';

export default function MapLegend() {
  const items = [
    { label: 'High Exposure Zone', color: '#ef4444' },
    { label: 'Moderate Vulnerability', color: '#f59e0b' },
    { label: 'Low Vulnerability', color: '#10b981' },
    { label: 'Historical Flood Incident', color: '#38bdf8' },
    { label: 'Stormwater Drain (SWD)', color: '#6366f1' },
    { label: 'Water Body (Kere)', color: '#0284c7' },
  ];

  return (
    <div style={{
      position: 'absolute',
      bottom: '24px',
      left: '24px',
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      backdropFilter: 'blur(4px)',
      border: '1px solid #334155',
      borderRadius: '8px',
      padding: '0.75rem 1rem',
      zIndex: 900,
      fontSize: '0.75rem',
      color: '#e2e8f0',
      minWidth: '180px'
    }}>
      <div style={{ fontWeight: 600, marginBottom: '0.5rem', color: '#94a3b8', textTransform: 'uppercase' }}>
        Map Layers &amp; Risk Tiers
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
        {items.map((item, idx) => (
          <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{
              width: '12px',
              height: '12px',
              borderRadius: '2px',
              backgroundColor: item.color,
              display: 'inline-block'
            }} />
            <span>{item.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
