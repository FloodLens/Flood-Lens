import React, { useState, useEffect } from 'react';
import Header from './components/Common/Header';
import FloodMap from './components/Map/FloodMap';
import VulnerabilityPanel from './components/Dashboard/VulnerabilityPanel';
import RouteComparison from './components/Dashboard/RouteComparison';
import { fetchHealth, fetchFloodPoints } from './services/api';
import './App.css';

export default function App() {
  const [health, setHealth] = useState(null);
  const [floodData, setFloodData] = useState({ features: [] });

  useEffect(() => {
    // Check backend health on startup
    fetchHealth().then((data) => setHealth(data));
    fetchFloodPoints().then((data) => setFloodData(data));
  }, []);

  return (
    <div className="app-container">
      <Header health={health} />
      <div className="main-content">
        <FloodMap floodData={floodData} />
        <aside className="sidebar-panel">
          <VulnerabilityPanel />
          <RouteComparison />
        </aside>
      </div>
    </div>
  );
}
