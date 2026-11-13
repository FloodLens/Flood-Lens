import React, { useState } from 'react';

export default function RouteComparison() {
  const [origin, setOrigin] = useState('');
  const [destination, setDestination] = useState('');

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 className="card-title">Risk-Aware Routing</h2>
        <span className="badge badge-person-b">Person B Module</span>
      </div>

      <p style={{ fontSize: '0.8rem', color: '#94a3b8', marginBottom: '1rem' }}>
        Compare standard shortest-distance path against lower-exposure alternatives.
      </p>

      {/* Informative Pending / Unavailable State */}
      <div style={{
        padding: '0.75rem',
        borderRadius: '6px',
        backgroundColor: 'rgba(245, 158, 11, 0.1)',
        border: '1px solid rgba(245, 158, 11, 0.3)',
        fontSize: '0.75rem',
        color: '#fde68a',
        marginBottom: '1rem',
        lineHeight: '1.4'
      }}>
        <strong>Status: Pending Integration</strong>
        <p style={{ marginTop: '0.25rem', color: '#fef3c7' }}>
          Routing engine is offline awaiting road network graph ingestion (OSMnx) and multi-criteria vulnerability scoring. Route comparisons will activate once network layers are placed in Phase 1.
        </p>
      </div>

      <form onSubmit={(e) => e.preventDefault()} style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        <div>
          <label style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block', marginBottom: '0.25rem' }}>
            Origin:
          </label>
          <input
            type="text"
            value={origin}
            onChange={(e) => setOrigin(e.target.value)}
            placeholder="Enter origin location..."
            disabled
            style={{
              width: '100%',
              padding: '0.5rem 0.75rem',
              backgroundColor: '#1e293b',
              border: '1px solid #334155',
              borderRadius: '6px',
              color: '#64748b',
              fontSize: '0.85rem',
              cursor: 'not-allowed'
            }}
          />
        </div>

        <div>
          <label style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block', marginBottom: '0.25rem' }}>
            Destination:
          </label>
          <input
            type="text"
            value={destination}
            onChange={(e) => setDestination(e.target.value)}
            placeholder="Enter destination location..."
            disabled
            style={{
              width: '100%',
              padding: '0.5rem 0.75rem',
              backgroundColor: '#1e293b',
              border: '1px solid #334155',
              borderRadius: '6px',
              color: '#64748b',
              fontSize: '0.85rem',
              cursor: 'not-allowed'
            }}
          />
        </div>

        <button
          type="button"
          disabled
          style={{
            backgroundColor: '#334155',
            color: '#94a3b8',
            border: 'none',
            padding: '0.6rem 1rem',
            fontSize: '0.85rem',
            fontWeight: 600,
            marginTop: '0.25rem',
            cursor: 'not-allowed'
          }}
        >
          Routing Unavailable (Awaiting Data)
        </button>
      </form>
    </div>
  );
}
