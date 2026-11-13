# FloodLens — API Contract Specification

This document defines the REST API contract for the FloodLens backend service. All endpoints follow REST conventions and return JSON payloads.

> ⚠️ **IMPORTANT SPECIFICATION NOTICE:**
> All sample JSON payloads, feature IDs (e.g., `FLD_001`), coordinates, and numerical metrics shown throughout this document are **illustrative architectural schema examples for documentation purposes only**. They do **not** represent real geographical observations, historical event records, or calibrated model outputs. Real data will be ingested in Phase 1.

- **Base URL:** `http://127.0.0.1:8000`
- **API Prefix:** `/api/v1`
- **Interactive Docs:** `/docs` (Swagger UI) and `/redoc` (ReDoc)

---

## 1. System Health & Metadata

### `GET /api/v1/health`
Retrieves system diagnostics, active study area, and CRS definitions.

**Response `200 OK`:**
```json
{
  "status": "healthy",
  "service": "FloodLens",
  "version": "0.1.0",
  "study_area": "Bengaluru, Karnataka, India",
  "crs": {
    "web_interchange": "EPSG:4326",
    "projected_metric": "EPSG:32643"
  },
  "boundary_configured": false
}
```

---

## 2. Flood Vulnerability & Observations

### `GET /api/v1/floods/points`
Retrieves historical flood observations and chronic flood-prone points as a standard GeoJSON FeatureCollection.

**Query Parameters:**
- None required (filtering by year or severity will be added upon dataset ingestion).

**Current Response (Phase 0 — When raw datasets are awaiting placement):**
```json
{
  "layer_name": "bbmp_historical_flood_points",
  "feature_count": 0,
  "crs": "EPSG:4326",
  "geojson": {
    "type": "FeatureCollection",
    "features": [],
    "metadata": {
      "description": "Historical flood observations (Bengaluru)",
      "status": "awaiting_raw_dataset_upload"
    }
  }
}
```

**Illustrative Target Response Schema (Documentation example only):**
```json
{
  "layer_name": "bbmp_historical_flood_points",
  "feature_count": 1,
  "crs": "EPSG:4326",
  "geojson": {
    "type": "FeatureCollection",
    "features": [
      {
        "type": "Feature",
        "geometry": {
          "type": "Point",
          "coordinates": [77.5946, 12.9716]
        },
        "properties": {
          "id": "EXAMPLE_ID_001",
          "name": "Illustrative Location Name",
          "source": "BBMP",
          "year": 2022,
          "cluster_id": 1
        }
      }
    ]
  }
}
```

---

### `GET /api/v1/floods/clusters`
Retrieves spatial clusters discovered via unsupervised DBSCAN clustering on historical observations.

**Query Parameters:**
- `eps_meters` (float, default: `300.0`): Spatial search radius in meters.
- `min_samples` (int, default: `3`): Minimum points required to form a cluster core.

**Current Response (Phase 0 — Awaiting data placement):**
```json
[]
```

**Illustrative Target Response Schema (Documentation example only):**
```json
[
  {
    "cluster_id": 1,
    "center_latitude": 12.9716,
    "center_longitude": 77.5946,
    "point_count": 5,
    "radius_meters": 250.0
  }
]
```

---

## 3. Risk-Aware Route Comparison

### `POST /api/v1/routes/compare`
Compares the traditional shortest-distance path against an exposure-penalized risk-aware path.

**Request Body Schema:**
```json
{
  "origin": {
    "latitude": 12.9767,
    "longitude": 77.5713
  },
  "destination": {
    "latitude": 12.9719,
    "longitude": 77.6412
  },
  "profile": "compare"
}
```

**Current Response (Phase 0 — When road network graph is not yet constructed):**
```json
{
  "origin": {
    "latitude": 12.9767,
    "longitude": 77.5713
  },
  "destination": {
    "latitude": 12.9719,
    "longitude": 77.6412
  },
  "status": "pending_road_network",
  "message": "Routing engine is currently offline awaiting road network graph construction (OSMnx/NetworkX) from data/raw/roads/ in Phase 1.",
  "shortest_route": null,
  "risk_aware_route": null,
  "delta_distance_meters": null,
  "delta_exposure_percentage": null
}
```

**Illustrative Target Response Schema (Documentation example only):**
```json
{
  "origin": {
    "latitude": 12.9767,
    "longitude": 77.5713
  },
  "destination": {
    "latitude": 12.9719,
    "longitude": 77.6412
  },
  "status": "completed",
  "message": "Route comparison completed successfully.",
  "shortest_route": {
    "route_type": "shortest",
    "distance_meters": 7650.0,
    "exposure_score": 0.74,
    "exposure_tier": "High",
    "coordinates": [
      [77.5713, 12.9767],
      [77.6050, 12.9740],
      [77.6412, 12.9719]
    ],
    "explanation": "Illustrative explanation: path passes through high exposure corridors."
  },
  "risk_aware_route": {
    "route_type": "risk_aware",
    "distance_meters": 8320.0,
    "exposure_score": 0.28,
    "exposure_tier": "Low",
    "coordinates": [
      [77.5713, 12.9767],
      [77.5980, 12.9850],
      [77.6412, 12.9719]
    ],
    "explanation": "Illustrative explanation: detours via lower exposure ridges."
  },
  "delta_distance_meters": 670.0,
  "delta_exposure_percentage": 62.16
}
```
