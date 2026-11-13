# FloodLens — System Architecture & Collaboration Framework

## 1. Executive Overview

**FloodLens** is a Bengaluru-focused GeoAI platform engineered to assess urban flood vulnerability and perform risk-aware route comparison. The platform equips urban planners, emergency responders, and citizens with explainable spatial intelligence to understand flood exposure across Bengaluru's complex terrain and infrastructure.

> **Crucial System Boundary:** FloodLens is an **urban vulnerability assessment platform**, not a real-time hydrodynamic flood prediction or early-warning system. It models static and historical exposure, topological depression, and infrastructural proximity.

---

## 2. Person A & Person B Ownership Matrix

To ensure independent parallel development without git conflicts, the codebase is partitioned strictly between Person A and Person B:

| Domain | Module / Artifact | Lead Owner | Secondary Reviewer |
| :--- | :--- | :--- | :--- |
| **System Architecture** | Project structure, config, baseline standards | Person A | Person B |
| **Requirements** | Requirements specs, documentation templates | Person B | Person A |
| **Flood Ingestion** | `data/raw/flood_locations/`, `data/raw/low_lying_areas/` | Person A | Person B |
| **Infrastructure Data** | `data/raw/roads/`, `data/raw/drainage/`, `data/raw/water_bodies/` | Person B | Person A |
| **Terrain & DEM** | `data/raw/elevation/`, Copernicus DEM GLO-30 | Person B | Person A |
| **Spatial Features** | Flood exposure density, historical cluster features | Person A | Person B |
| **Terrain Features** | Drainage proximity, water body buffers, slope/elevation | Person B | Person A |
| **GeoAI / Clustering** | DBSCAN spatial clustering in EPSG:32643 | Person A | Person B |
| **Vulnerability Scoring** | Explainable multi-criteria weighting index | Person B | Person A |
| **Road Graph** | OSMnx base graph extraction & topology building | Person A | Person B |
| **Route Optimisation** | Dijkstra / A* risk-weighted exposure comparison | Person B | Person A |
| **Interactive Map** | Leaflet container, layer toggles, cluster visualizer | Person A | Person B |
| **Dashboard UI** | Vulnerability cards, route comparison inputs & metrics | Person B | Person A |

---

## 3. Technology Stack

- **Python Core:** Python 3.10+ / 3.14 compatible
- **GIS & Spatial Analysis:**
  - `GeoPandas` & `Fiona`: Vector geometry I/O and spatial joins
  - `Shapely 2.0+`: Planar geometric operations and automated validation (`make_valid`)
  - `Rasterio`: Digital Elevation Model (DEM) and raster querying
  - `Pyproj`: Accurate cartographic reprojections
- **Graph & Machine Learning:**
  - `OSMnx`: OpenStreetMap road network retrieval and graph construction
  - `NetworkX`: Graph algorithms, shortest-path calculation, impedance weighting
  - `Scikit-learn`: DBSCAN unsupervised spatial density clustering
- **Backend Service:**
  - `FastAPI`: High-performance asynchronous REST API
  - `Uvicorn`: ASGI application server
  - `Pydantic v2`: Schema validation and settings management
- **Frontend Dashboard:**
  - `React 18` + `Vite`: High-performance reactive client
  - `Leaflet` & `React-Leaflet`: Interactive cartographic visualization
- **Quality Assurance:**
  - `Pytest`: Automated unit and integration testing

---

## 4. Coordinate Reference Systems (CRS)

1. **Web Interchange & Visualisation (`EPSG:4326` — WGS 84):**
   - Standard latitude and longitude in decimal degrees.
   - Exclusively used for GeoJSON payload interchange, frontend Leaflet display, and API communication.
2. **Metric Spatial Processing (`EPSG:32643` — UTM Zone 43N):**
   - Planar metric projection appropriate for Bengaluru, Karnataka.
   - Exclusively used for:
     - Buffer calculations (e.g. 50m drainage buffer).
     - DBSCAN clustering radius (`eps` in meters).
     - Euclidean distance to water bodies and flood hotspots.
     - Accurate road segment length calculations.

---

## 5. High-Level Data Flow

```
[Raw Datasets in data/raw/]
   │
   ├── Person A: Flood Locations, Low-Lying Areas, OSM Roads
   └── Person B: Stormwater Drains (SWD), Lakes (ATREE), Copernicus DEM
   │
   ▼
[Inspection & Validation: scripts/inspect_datasets.py]
   │  (Generates data/metadata/data_inventory.csv)
   ▼
[Preprocessing & Reprojection to EPSG:32643 & EPSG:4326]
   │
   ├── Person A: DBSCAN Clustering & Flood Exposure Features
   └── Person B: Proximity Calculations & Elevation Profiling
   │
   ▼
[Vulnerability Engine: Weighted Multi-Criteria Integration]
   │
   ▼
[Routable Road Graph: OSMnx + NetworkX Weighted Impedance]
   │
   ▼
[FastAPI Backend: /api/v1/floods, /api/v1/routes]
   │
   ▼
[React + Vite + Leaflet Frontend Dashboard]
```

---

## 6. Git Workflow & Conflict Prevention Rules

To safeguard against accidental overwrites and merge collisions:
1. **Never commit directly to `main`.**
2. Feature branches must strictly reflect ownership:
   - Person A: `feature/person-a-<task-name>` (e.g. `feature/person-a-dbscan-clustering`)
   - Person B: `feature/person-b-<task-name>` (e.g. `feature/person-b-drainage-buffers`)
3. **Large Datasets Never Enter Git:**
   - All spatial binaries (`.shp`, `.geojson`, `.tif`, `.kml`, `.kmz`, `.gpkg`) in `data/raw/` and `data/processed/` are gitignored.
   - Only code, documentation, test scripts, and metadata CSVs are committed.
