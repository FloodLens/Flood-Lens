import React from 'react';

export default function Header({ health }) {
  return (
    <header style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0.75rem 1.5rem',
      backgroundColor: '#1e293b',
      borderBottom: '1px solid #334155',
      zIndex: 1010,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <div style={{
          width: '32px',
          height: '32px',
          borderRadius: '8px',
          backgroundColor: '#0284c7',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontWeight: 'bold',
          color: '#fff',
          fontSize: '1.1rem'
        }}>
          FL
        </div>
        <div>
          <h1 style={{ fontSize: '1.15rem', fontWeight: 700, letterSpacing: '-0.02em', color: '#f8fafc' }}>
            FloodLens
          </h1>
          <p style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
            Bengaluru Urban Flood Vulnerability &amp; Risk-Aware Route Comparison
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '0.8rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <span style={{ color: '#94a3b8' }}>Study Area:</span>
          <span style={{ color: '#38bdf8', fontWeight: 600 }}>Bengaluru (EPSG:4326 / EPSG:32643)</span>
        </div>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.35rem',
          padding: '0.25rem 0.6rem',
          borderRadius: '9999px',
          backgroundColor: health ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
          color: health ? '#10b981' : '#ef4444',
          fontWeight: 500,
          fontSize: '0.75rem'
        }}>
          <span style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: health ? '#10b981' : '#ef4444'
          }} />
          {health ? 'Backend Connected' : 'Backend Offline'}
        </div>
      </div>
    </header>
  );
}
