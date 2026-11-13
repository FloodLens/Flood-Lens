# FloodLens 🌊🗺️

> **Bengaluru-focused GeoAI Platform for Urban Flood Vulnerability Assessment & Risk-Aware Route Comparison**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18-61dafb.svg)](https://react.dev/)
[![Leaflet](https://img.shields.io/badge/Leaflet-1.9.4-199900.svg)](https://leafletjs.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 📌 Project Overview

Rapid urbanisation, altered natural drainage channels (*rajakaluves*), and interconnected lake networks (*keres*) make Bengaluru prone to seasonal urban flooding. **FloodLens** is an open GeoAI platform engineered to:

1. **Visualise historical flood-prone hotspots** across Bengaluru.
2. **Analyse natural low-lying depressions** and valley corridors.
3. **Harmonise infrastructure layers** including roads, stormwater drains, and lakes.
4. **Extract topographic profiles** from 30m Digital Elevation Models (DEM).
5. **Apply DBSCAN spatial clustering** to discover chronic inundation clusters.
6. **Formulate explainable multi-criteria vulnerability scores** for roads and urban grids.
7. **Compare shortest-distance vs lower-exposure routes** to aid safe mobility.
8. **Provide an interactive cartographic dashboard** for urban researchers and citizens.

> ⚠️ **Important Scope Clarification:** FloodLens is an **urban vulnerability assessment platform**, not a real-time hydrodynamic flood prediction or early-warning system. It assesses mapped historical vulnerability and topography.

---

## 👥 Two-Person Team Collaboration Matrix

To allow independent development without git conflicts, the project is divided between Person A and Person B:

```
┌──────────────────────────────────────────────┬──────────────────────────────────────────────┐
│           Person A Responsibility            │           Person B Responsibility            │
├──────────────────────────────────────────────┼──────────────────────────────────────────────┤
│ • Overall System Architecture                │ • Requirements & Data Dictionary Docs        │
│ • Flood & Historical Inundation Datasets     │ • Road, Drainage & Water Body Datasets       │
│ • Historical Exposure Feature Engineering   │ • Terrain & Infrastructure Features (DEM)    │
│ • DBSCAN Spatial Clustering (EPSG:32643)    │ • Multi-Criteria Vulnerability Scoring       │
│ • Road Network Graph Construction (OSMnx)    │ • Risk-Aware Route Optimisation (NetworkX)   │
│ • Main Interactive Leaflet Map Visualisation │ • Analytical Dashboard & Metrics Panel       │
└──────────────────────────────────────────────┴──────────────────────────────────────────────┘
```

---

## 🗂️ Project Directory Structure

```text
Flood-Lens/
│
├── data/                                 # Spatial datasets (raw data is gitignored)
│   ├── raw/                              # Original source files (never modified)
│   │   ├── flood_locations/              # BBMP historical flood points (Person A)
│   │   ├── low_lying_areas/              # Low-lying polygons / valleys (Person A)
│   │   ├── roads/                        # Road network layers (Person A)
│   │   ├── drainage/                     # Stormwater drainage / Rajakaluves (Person B)
│   │   ├── water_bodies/                 # Lakes / Keres (Person B)
│   │   ├── elevation/                    # Copernicus DEM GLO-30 raster (Person B)
│   │   ├── rainfall/                     # Optional NASA GPM precipitation (Person B)
│   │   └── land_cover/                   # Optional Google Dynamic World (Person B)
│   │
│   ├── processed/                        # Cleaned, harmonised, projected datasets
│   └── metadata/                         # Data registries and inspection logs
│       ├── data_sources.csv              # Source metadata and ownership mapping
│       └── data_inventory.csv            # Automatically updated inspection log
│
├── notebooks/                            # Exploratory Jupyter Notebooks
│   ├── 01_data_exploration.ipynb         # Raw data inspection & visual distribution
│   ├── 02_data_cleaning.ipynb            # Reprojection & geometry validation
│   ├── 03_spatial_analysis.ipynb         # Buffering, drainage & DEM distance joins
│   └── 04_geoai_analysis.ipynb           # DBSCAN clustering & routing comparison
│
├── scripts/                              # Command-line pipelines & utilities
│   ├── inspect_datasets.py               # Inspects, validates & logs all raw datasets
│   ├── validate_geometries.py            # Checks & repairs vector topologies
│   ├── preprocess_data.py                # Preprocessing & standardisation pipeline
│   └── generate_features.py              # Spatial feature extraction engine
│
├── backend/                              # FastAPI Backend Service
│   ├── app/
│   │   ├── main.py                       # FastAPI application entrypoint
│   │   ├── api/
│   │   │   └── routers/                  # REST endpoints (/health, /floods, /routes)
│   │   ├── core/
│   │   │   └── config.py                 # Central Bengaluru CRS & data configuration
│   │   ├── models/                       # Data models
│   │   ├── schemas/                      # Pydantic input/output schemas
│   │   ├── services/                     # Business logic (Person A & Person B split)
│   │   └── utils/                        # Spatial helpers, haversine & logging
│   └── requirements.txt                  # Backend-specific dependencies
│
├── frontend/                             # React + Vite + Leaflet Web Application
│   ├── src/
│   │   ├── components/
│   │   │   ├── Map/                      # Leaflet map & layer toggles (Person A)
│   │   │   ├── Dashboard/                # Vulnerability & route panel (Person B)
│   │   │   └── Common/                   # Global header & branding
│   │   ├── services/api.js               # Backend API fetch client
│   │   ├── App.jsx                       # Master UI layout
│   │   └── main.jsx                      # React mounting
│   ├── package.json                      # Frontend dependencies
│   └── vite.config.js                    # Vite server configuration & API proxy
│
├── tests/                                # Automated Test Suite
│   ├── test_data_validation.py           # BBox, metadata & CRS integrity tests
│   └── test_spatial_analysis.py          # Coordinates, distance & polygon tests
│
├── docs/                                 # Comprehensive Documentation
│   ├── architecture.md                   # System design & collaboration rules
│   ├── api_contract.md                   # Complete REST API specification
│   ├── data_sources.md                   # Dataset registry & download guide
│   ├── data_dictionary.md                # Attribute schemas & units
│   ├── methodology.md                    # DBSCAN & vulnerability scoring formulas
│   └── limitations.md                    # Scope limits, resolution & safety notices
│
├── .gitignore                            # Protects raw data, caches & node_modules
├── requirements.txt                      # Root Python dependencies
└── README.md                             # Project documentation (this file)
```

---

## 🧭 Spatial Configuration

- **Study Area:** Bengaluru, Karnataka, India
- **Web Interchange CRS (`EPSG:4326`):** WGS 84 geographic coordinates (latitude, longitude) used for GeoJSON and Leaflet display.
- **Metric Processing CRS (`EPSG:32643`):** WGS 84 / UTM Zone 43N projected planar coordinates (meters) used for metric distances, drainage buffers, DEM slopes, and DBSCAN clustering radius (`eps`).
- **Administrative Boundary:** Configured in `backend/app/core/config.py` as ready for a verified boundary vector file (e.g., BBMP ward boundary).

---

## 🚀 Quickstart Guide for Beginners

### 1. Python Environment Setup

Clone the repository and set up a virtual environment:

```bash
# 1. Create a virtual environment
python -m venv venv

# 2. Activate the virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On macOS / Linux:
source venv/bin/activate

# 3. Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Inspecting Downloaded Datasets

Once you download your raw datasets, place them in their respective subdirectories under `data/raw/` (see [Dataset Placement Guide](docs/data_sources.md)).

Run the inspection utility:
```bash
python scripts/inspect_datasets.py
```
This tool:
- Scans all files (`.shp`, `.geojson`, `.kml`, `.kmz`, `.gpkg`, `.tif`).
- Records CRS, geometry types, and feature counts.
- Verifies that data bounds overlap Bengaluru.
- Flags invalid geometries.
- Automatically updates `data/metadata/data_inventory.csv`.

### 3. Running the Backend Service

```bash
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```
- API Root: `http://127.0.0.1:8000`
- Interactive Swagger Documentation: `http://127.0.0.1:8000/docs`
- Health Endpoint: `http://127.0.0.1:8000/api/v1/health`

### 4. Running the Frontend Dashboard

In a separate terminal window:
```bash
cd frontend
npm install
npm run dev
```
Open your browser at `http://localhost:5173`.

### 5. Running the Automated Tests

```bash
python -m pytest tests -v
```

---

## 🌿 Git Collaboration Rules

To protect each team member's work:

1. **Never work or push directly to `main`.**
2. Work on your dedicated feature branch:
   - Person A: `git checkout -b feature/person-a-<feature-name>`
   - Person B: `git checkout -b feature/person-b-<feature-name>`
3. **Never commit raw spatial datasets** (`.shp`, `.tif`, `.geojson`, `.kml`, etc.). The `.gitignore` is pre-configured to keep data directories clean while tracking code, documentation, and metadata CSVs.
4. Review your changes before committing:
   ```bash
   git status
   git diff
   ```

---

## 📄 License & Attribution

- Built with OpenStreetMap data © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright).
- Terrain elevation derived from Copernicus DEM GLO-30 © [European Space Agency (ESA)](https://spacedata.copernicus.eu/).
- Water bodies curated with reference to [ATREE](https://www.atree.org/) and [OpenCity Bengaluru](https://opencity.in/).
- Licensed under the [MIT License](LICENSE).
