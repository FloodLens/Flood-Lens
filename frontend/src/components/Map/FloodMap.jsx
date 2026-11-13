import React, { useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import MapLegend from './MapLegend';

// Bengaluru Central Coordinates (Vidhana Soudha / MG Road)
const BENGALURU_CENTER = [12.9716, 77.5946];
const DEFAULT_ZOOM = 12;

export default function FloodMap({ floodData }) {
  const [showFloodPoints, setShowFloodPoints] = useState(true);
  const [showLowLying, setShowLowLying] = useState(true);
  const [showDBSCAN, setShowDBSCAN] = useState(false);

  return (
    <div className="map-wrapper">
      {/* Floating Layer Controls (Person A) */}
      <div style={{
        position: 'absolute',
        top: '16px',
        right: '16px',
        backgroundColor: 'rgba(15, 23, 42, 0.9)',
        border: '1px solid #334155',
        borderRadius: '8px',
        padding: '0.75rem 1rem',
        zIndex: 900,
        fontSize: '0.8rem',
        color: '#f8fafc',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.5rem'
      }}>
        <div style={{ fontWeight: 600, color: '#38bdf8' }}>Map Layers (Person A)</div>
        <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={showFloodPoints}
            onChange={(e) => setShowFloodPoints(e.target.checked)}
          />
          Historical Flood Points
        </label>
        <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={showLowLying}
            onChange={(e) => setShowLowLying(e.target.checked)}
          />
          Low-Lying Areas
        </label>
        <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={showDBSCAN}
            onChange={(e) => setShowDBSCAN(e.target.checked)}
          />
          DBSCAN Clusters
        </label>
      </div>

      <MapContainer
        center={BENGALURU_CENTER}
        zoom={DEFAULT_ZOOM}
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
        />

        {/* Informational Center Pin */}
        <Marker position={BENGALURU_CENTER}>
          <Popup>
            <strong>Bengaluru City Center</strong><br />
            Lat: 12.9716, Lon: 77.5946<br />
            CRS: EPSG:4326 / EPSG:32643
          </Popup>
        </Marker>

      </MapContainer>

      <MapLegend />
    </div>
  );
}
