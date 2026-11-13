/**
 * FloodLens Frontend API Client
 * Interfaces with FastAPI endpoints.
 */

const API_BASE = '/api/v1';

export async function fetchHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error('Failed to fetch backend health status:', err);
    return null;
  }
}

export async function fetchFloodPoints() {
  try {
    const res = await fetch(`${API_BASE}/floods/points`);
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error('Failed to fetch flood points:', err);
    return { features: [] };
  }
}

export async function compareRoutes(origin, destination) {
  try {
    const res = await fetch(`${API_BASE}/routes/compare`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ origin, destination, profile: 'compare' }),
    });
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error('Failed to compare routes:', err);
    return null;
  }
}
