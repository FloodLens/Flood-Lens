# FloodLens — Requirements Specification

> **Document Status:** Phase 0 Baseline  
> **Lead Author:** Person B (Requirements & Spatial Analytics Lead)  
> **Reviewer:** Person A (System Architecture & GeoAI Lead)  
> **Study Area:** Bengaluru Metropolitan Region, Karnataka, India  
> **Platform Baseline:** Urban Flood Vulnerability Assessment & Risk-Aware Route Comparison  

---

## 1. Executive Summary & Purpose

**FloodLens** is an open GeoAI platform engineered to assess urban flood vulnerability and perform comparative, risk-aware route evaluation across the Bengaluru metropolitan region. Due to rapid, unplanned urbanization, alteration of natural drainage channels (*rajakaluves*), encroachment of cascading lake systems (*keres*), and micro-topographical valley depressions, Bengaluru suffers frequent localized flooding during seasonal monsoon and cloudburst events.

This document establishes the functional requirements (FR), non-functional requirements (NFR), system boundaries, and delivery roadmap for the FloodLens platform.

### Core System Scope Boundary
> [!IMPORTANT]
> **FloodLens is an urban flood vulnerability assessment platform, NOT a real-time hydrodynamic forecast or emergency evacuation clearance system.**  
> It evaluates spatial exposure by integrating static topographical depressions, proximity to hydrological networks, and historical inundation clusters. It does not model transient hydrodynamic pipe pressures, turbulent flow velocities, or dynamic stormwater pump station telemetry. All routing recommendations are **comparative risk evaluations based on mapped indicators** and are not guaranteed to be flood-free or navigable during active storm events.

---

## 2. User Personas & Use Cases

| Persona | Primary Needs & Objectives | Core System Interaction |
| :--- | :--- | :--- |
| **Citizen / Commuter** | Identify flood-prone corridors along routine commutes; compare traditional shortest paths with lower-exposure alternatives; report localized flooding or drain blockages. | Interactive map exploration, route origin/destination input, community incident reporting form. |
| **Urban Planner / BBMP Official** | Visualize chronic flood hotspots, evaluate topographical depression zones, and understand infrastructure proximity drivers across wards. | Multi-layer cartographic toggles, road segment vulnerability breakdowns, DBSCAN cluster inspection. |
| **Emergency Responder / Dispatcher** | Assess relative flood vulnerability across transit corridors to prioritize resilient routing and identify vulnerable low-lying choke points. | Route comparison metrics ($\Delta\text{Distance}$ vs $\Delta\text{Exposure}$), risk tier classifications (Low, Medium, High). |

---

## 3. Functional Requirements (FR)

### FR-1: Interactive Geographical Map
- **Purpose:** Provide a responsive, browser-based cartographic interface centered over Bengaluru for seamless spatial exploration of flood, terrain, and infrastructure layers.
- **Required Inputs:** 
  - Standard web tile layer (OpenStreetMap / CartoDB Dark/Positron base tiles).
  - User pan, zoom, and click interactions.
  - GeoJSON spatial feature payloads served from backend endpoints (`EPSG:4326`).
- **Expected Outputs:** 
  - Rendered Leaflet map viewport centered at Bengaluru ([12.9716° N, 77.5946° E], zoom level 12).
  - Smooth vector rendering of points, lines, and polygons.
  - Interactive marker tooltips and feature inspection popups.
- **Dependencies:** Leaflet 1.9+, React-Leaflet, OpenStreetMap tile servers, backend `/api/v1/health` and `/api/v1/floods/points`.
- **Delivery Scope:** **MVP** (Core map framework owned by Person A).
- **Implementation Status:** Phase 0 scaffold deployed; full data layer bindings scheduled for Phase 1.

---

### FR-2: Historical Flood Hotspot Visualisation
- **Purpose:** Display officially recorded historical flood incident locations and chronic inundation hotspots across Bengaluru wards to highlight empirical flood vulnerability.
- **Required Inputs:** 
  - Historical flood point datasets (`data/raw/flood_locations/`) ingested from BBMP / KSNDMC.
  - Coordinate attributes reprojected to `EPSG:4326`.
- **Expected Outputs:** 
  - High-visibility circular point markers on the map canvas.
  - Popups displaying incident metadata: Location name/landmark, recorded year, reporting agency, and cluster assignment.
  - Density-aware clustering representation (DBSCAN output layer).
- **Dependencies:** Person A flood dataset acquisition, backend `/api/v1/floods/points` and `/api/v1/floods/clusters`.
- **Delivery Scope:** **MVP** (Person A).
- **Implementation Status:** Phase 0 API endpoint returns empty FeatureCollection with status `awaiting_raw_dataset_upload`; dataset placement and rendering planned for Phase 1.

---

### FR-3: Low-Lying Area Visualisation
- **Purpose:** Delineate topographical depressions, valley basins, and natural low-lying catchments prone to stormwater pooling.
- **Required Inputs:** 
  - BBMP low-lying geographical area polygon vectors (`data/raw/low_lying_areas/`).
- **Expected Outputs:** 
  - Semi-transparent polygon overlays colored to distinguish valley zones and depression corridors from surrounding topography.
  - Feature inspection popups displaying zone name, administrative ward, and depression classification.
- **Dependencies:** Person A low-lying vector ingestion, GeoJSON serialization in `EPSG:4326`.
- **Delivery Scope:** **MVP** (Person A).
- **Implementation Status:** Phase 0 directory scaffolded; data ingestion and polygon rendering scheduled for Phase 1.

---

### FR-4: Terrain and Elevation Indicators
- **Purpose:** Provide continuous topographical elevation and slope indicators derived from Digital Elevation Models (DEM) to evaluate relative depression depths and gravity runoff potential.
- **Required Inputs:** 
  - 30-meter Copernicus DEM GLO-30 raster (`data/raw/elevation/`).
  - Spatial intersection coordinates of road edges and urban points.
- **Expected Outputs:** 
  - Elevation in meters above sea level (ASL) for sampled coordinates or road segment midpoints.
  - Derived terrain slope percentage (`slope_pct`) indicating gradient steepness.
  - Relative elevation depression metrics identifying road segments lower than their local neighborhood baseline.
- **Dependencies:** Person A DEM acquisition; Person B raster extraction and slope profiling engine (`backend/app/services/terrain_service.py`, `Rasterio`).
- **Delivery Scope:** 
  - **MVP:** Elevation sampling and segment slope extraction from Copernicus 30m DEM.
  - **Later Enhancement:** High-resolution LIDAR micro-topography (1m–5m), hydrologic Topographic Wetness Index (TWI), and depression sink depth calculation.
- **Implementation Status:** Phase 0 architecture configured; DEM ingestion and raster sampling pipeline scheduled for Phase 1.

---

### FR-5: Road Network, Drainage, and Water-Body Layers
- **Purpose:** Harmonize and display structural urban infrastructure that influences stormwater conveyance and commuter mobility.
- **Required Inputs:** 
  - OpenStreetMap road network extracts / BBMP road centrelines (`data/raw/roads/`).
  - BBMP stormwater drains / rajakaluves (`data/raw/drainage/`).
  - ATREE lake and stream boundaries (`data/raw/water_bodies/`).
- **Expected Outputs:** 
  - Navigable vector street network colored by functional road hierarchy (`primary`, `secondary`, `tertiary`, `residential`).
  - Blue linear vectors delineating primary and secondary stormwater drains (*rajakaluves*).
  - Distinct polygon fills identifying active and historical water bodies (*keres*).
  - Metric buffer zones (e.g., 30m/50m drainage corridors) computed in `EPSG:32643`.
- **Dependencies:** Person B infrastructure dataset acquisition and cleaning; Person A road graph construction; metric spatial processing in GeoPandas/Shapely.
- **Delivery Scope:** **MVP** (Person B infrastructure acquisition; Person A road graph extraction).
- **Implementation Status:** Phase 0 directory structures and inspection scripts initialized; vector processing scheduled for Phase 1.

---

### FR-6: Explainable Geographical Vulnerability Assessment
- **Purpose:** Formulate an objective, transparent, and interpretable multi-criteria vulnerability score ($V_e \in [0.0, 1.0]$) for every road segment without relying on opaque black-box deep learning models.
- **Required Inputs:** 
  - Distance to nearest stormwater drain ($D_e$, meters).
  - Distance to nearest lake/water body ($L_e$, meters).
  - Distance to nearest historical flood cluster centroid ($F_e$, meters).
  - Topographical depression score ($E_e$) derived from DEM elevation and slope.
  - Normalized multi-criteria weighting coefficients ($\sum w_i = 1.0$).
- **Expected Outputs:** 
  - Continuous vulnerability index $V_e \in [0.0, 1.0]$ associated with each road segment.
  - Categorical risk tier assignment: `Low` ($0.0 \le V_e \le 0.33$), `Medium` ($0.34 \le V_e \le 0.66$), `High` ($0.67 \le V_e \le 1.0$).
  - Segment-level explanatory breakdown detailing the primary contributing vulnerability factors.
- **Dependencies:** Person B vulnerability service (`backend/app/services/vulnerability_service.py`), Person A DBSCAN cluster centroids, Person B spatial proximity joins.
- **Delivery Scope:** **MVP** (Person B).
- **Implementation Status:** Phase 0 mathematical formula defined in documentation; computational feature pipeline scheduled for Phase 1.

---

### FR-7: Shortest-Distance and Risk-Weighted Route Comparison
- **Purpose:** Calculate and contrast a standard shortest-distance route against a risk-weighted path that penalizes road segments with high flood vulnerability, giving commuters an informed mobility choice.
- **Required Inputs:** 
  - Origin coordinates (`latitude`, `longitude` in `EPSG:4326`).
  - Destination coordinates (`latitude`, `longitude` in `EPSG:4326`).
  - Routing profile request (`compare`, `shortest`, or `risk_aware`).
  - Routable NetworkX graph built from OSMnx with pre-computed edge lengths and vulnerability impedance weights:
    $$w_e = \text{length}_e \cdot (1.0 + \alpha \cdot V_e^\beta)$$
- **Expected Outputs:** 
  - GeoJSON LineStrings for both the shortest path and the risk-aware path.
  - Comparative distance metric: Shortest distance, risk-aware distance, and distance delta ($\Delta\text{Distance} = \text{Distance}_{\text{risk-aware}} - \text{Distance}_{\text{shortest}}$).
  - Comparative exposure metric: Aggregate exposure score and percentage exposure reduction ($\Delta\text{Exposure} = \frac{\text{Exposure}_{\text{shortest}} - \text{Exposure}_{\text{risk-aware}}}{\text{Exposure}_{\text{shortest}}} \times 100\%$).
  - Qualitative risk tier badges and human-readable tradeoff explanations.
  - Prominent navigational safety advisory banner.
- **Dependencies:** Person A road graph construction (`backend/app/services/road_graph_service.py`); Person B routing optimization engine (`backend/app/services/routing_service.py`); backend endpoint `POST /api/v1/routes/compare`.
- **Delivery Scope:** **MVP** (Person B routing engine & comparison UI).
- **Implementation Status:** Phase 0 endpoint returns `status: "pending_road_network"` awaiting graph ingestion in Phase 1.

---

### FR-8: Community Flood Incident Reporting
- **Purpose:** Empower citizens and local observers to submit crowdsourced flood incident reports, water stagnation points, and drain overflow observations to augment institutional records.
- **Required Inputs:** 
  - Incident geographic coordinates (selected via map pin click or GPS lookup).
  - Incident category: `Street Inundation`, `Underpass Waterlogging`, `Storm Drain Overflow`, `Lakebed Backflow`, `Traffic Disruption`.
  - Severity level: `Low` (Ankle deep / passable), `Medium` (Knee deep / passenger cars halted), `High` (Waist deep / impassable).
  - Optional brief text description / landmarks.
  - Submission timestamp (ISO 8601).
- **Expected Outputs:** 
  - Immediate visual feedback on client interface confirming report reception.
  - Temporary client-side incident marker displayed with "Community Report (Unverified)" badge.
  - JSON response payload from supporting API endpoint with unique `report_id` and submission status.
- **Dependencies:** Person B reporting interface modal (`frontend/src/components/Dashboard/CommunityReportModal.jsx`); Person B supporting backend endpoint (`POST /api/v1/reports/incidents`).
- **Delivery Scope:** 
  - **MVP:** In-memory / JSON-based submission logging, frontend submission modal, coordinate picker, and unverified marker display.
  - **Later Enhancement:** Geotagged photo upload, BBMP Sahaaya citizen portal integration, automated spatial clustering with official alerts.
- **Implementation Status:** Phase 0 architecture specified; endpoint and frontend submission component scheduled for Phase 1.

---

### FR-9: Dashboard Summaries and Map-Based Interaction
- **Purpose:** Present an interactive analytical panel alongside the map to display system diagnostics, active layer statistics, selected entity vulnerability metrics, and route comparison summaries.
- **Required Inputs:** 
  - Backend `/api/v1/health` diagnostic payload.
  - Active layer toggle states from frontend state management.
  - Selected road edge or geographical point event data.
  - Response payloads from route comparison endpoint.
- **Expected Outputs:** 
  - Real-time system health badge (Service version, active CRS, boundary status).
  - Interactive layer controller to toggle historical points, low-lying zones, drains, lakes, and DBSCAN clusters.
  - Vulnerability inspection card showing multi-criteria breakdown for clicked road segments.
  - Dual-metric route summary cards showing distance vs. exposure tradeoff bars.
  - Disclaimer and navigational advisory banner.
- **Dependencies:** Person B Dashboard UI components (`frontend/src/components/Dashboard/`); Person A map interaction events.
- **Delivery Scope:** **MVP** (Person B).
- **Implementation Status:** Phase 0 UI layout and placeholder cards active; dynamic data integration scheduled for Phase 1.

---

## 4. Non-Functional Requirements (NFR)

### NFR-1: Cartographic & Coordinate Reference System (CRS) Integrity
- The system must strictly segregate web display and metric computation projections:
  - **Web Interchange & Visualization (`EPSG:4326` — WGS 84):** All GeoJSON payloads, REST API requests/responses, and Leaflet map rendering must operate in decimal degrees latitude/longitude.
  - **Metric Planar Analysis (`EPSG:32643` — UTM Zone 43N):** All spatial buffering (drainage corridors), Euclidean distance calculations, slope computations, and DBSCAN search radii ($\epsilon$) must be performed strictly in projected metric units (meters) to eliminate planar distortion over Bengaluru.
- Automated geometry validation (`make_valid`) must execute on all vector ingestions to prevent planar topology errors (self-intersections, slivers, unclosed rings).

### NFR-2: Performance & Response Latencies
- **Health Check (`GET /api/v1/health`):** Response latency $\le 50\text{ ms}$.
- **Pre-computed Spatial Layers (`GET /api/v1/floods/points`):** Response latency $\le 300\text{ ms}$ for typical ward-level queries.
- **DBSCAN Cluster Generation (`GET /api/v1/floods/clusters`):** Execution time $\le 1500\text{ ms}$ on historical incident sets up to 10,000 points.
- **Route Comparison (`POST /api/v1/routes/compare`):** Calculation latency $\le 1000\text{ ms}$ for origin-destination pairs within the Bengaluru metropolitan bounding box using indexed NetworkX graphs.
- **Frontend Map Rendering:** Consistent 60 FPS pan and zoom performance; vector rendering optimized via Canvas or SVG for up to 5,000 simultaneous features.

### NFR-3: Graceful Fallbacks & Architectural Transparency
- The system must **never generate synthetic coordinates, mock flood points, or fake routing solutions** when underlying datasets or services are offline.
- When datasets are pending placement, endpoints must return standard HTTP 200 with explicit descriptive statuses (e.g., `status: "pending_road_network"`, `status: "awaiting_raw_dataset_upload"`), accompanied by human-readable guidance.
- Frontend components must gracefully render amber "Pending Integration" informational banners instead of failing or displaying deceptive synthetic data.

### NFR-4: Usability, Symbology & Accessibility
- The user interface must adhere to accessible cartographic color design:
  - **Low Exposure:** Emerald / Teal (`#10b981`)
  - **Medium Exposure:** Amber / Orange (`#f59e0b`)
  - **High Exposure:** Crimson / Red (`#ef4444`)
  - **Stormwater Drains:** Cyan / Royal Blue (`#0284c7`)
  - **Water Bodies:** Deep Azure (`#0369a1`)
  - **Historical Flood Hotspots:** Vivid Purple / Violet (`#a855f7`)
- Visual contrast ratios for all textual UI components must comply with WCAG 2.1 AA standards ($\ge 4.5:1$).
- Responsive sidebar layout allowing full-screen cartographic exploration on desktop and tablet screens.

### NFR-5: Modularity & Collaboration Decoupling
- Strict separation between Person A modules (flood ingestion, DBSCAN, OSM base graph, Leaflet map) and Person B modules (infrastructure ingestion, terrain/proximity feature extraction, vulnerability scoring, routing optimization, dashboard UI).
- Independent service layers with clearly documented interfaces to ensure changes in routing logic do not disrupt map visualization, and vice versa.

### NFR-6: Security, Data Governance & Privacy
- Community incident reports must not collect personally identifiable information (PII) such as citizen phone numbers, street addresses, or IP addresses. Only coordinate pairs, category, severity, and anonymized descriptions shall be stored.
- Backend must validate all incoming payloads using Pydantic v2 schemas with strict coordinate bounds checking against the Bengaluru geographical sanity box ($77.40^\circ\text{E} \le \text{lon} \le 77.85^\circ\text{E}$ and $12.75^\circ\text{N} \le \text{lat} \le 13.20^\circ\text{N}$).
- Cross-Origin Resource Sharing (CORS) strictly constrained to authorized client origins (Vite dev server `http://localhost:5173`).

### NFR-7: Scientific & Navigational Advisory Disclaimer
- The platform must display unambiguous advisory disclaimers on all routing cards and reports:
  > *"Route comparison is an analytical estimate based on historical and topographical exposure indicators. It does not reflect real-time water depths, dynamic flash inundations, or emergency road closures. Never attempt to drive or walk through flooded roadways."*

---

## 5. Requirements Traceability & Delivery Roadmap

| Req ID | Description | Lead Owner | Target Phase | Verification Method |
| :--- | :--- | :--- | :--- | :--- |
| **FR-1** | Interactive Geographical Map | Person A | MVP (Phase 1) | UI test; verify tile loading and pan/zoom response |
| **FR-2** | Historical Flood Hotspot Visualisation | Person A | MVP (Phase 1) | API test `/api/v1/floods/points`; verify marker rendering |
| **FR-3** | Low-Lying Area Visualisation | Person A | MVP (Phase 1) | Visual inspection of polygon geometry overlays |
| **FR-4** | Terrain and Elevation Indicators | Person B | MVP (Phase 1) | Rasterio unit tests; slope calculation accuracy check |
| **FR-5** | Road, Drainage & Water Body Layers | Person B / A | MVP (Phase 1) | GeoPandas spatial join tests; buffer distance validation |
| **FR-6** | Explainable Vulnerability Scoring | Person B | MVP (Phase 1) | Unit tests in `test_spatial_analysis.py`; weight sum check |
| **FR-7** | Shortest vs Risk-Aware Route Comparison | Person B | MVP (Phase 1) | NetworkX test cases; verify $\text{Exposure}_{\text{risk}} < \text{Exposure}_{\text{short}}$ |
| **FR-8** | Community Flood Incident Reporting | Person B | MVP (Phase 1) | Schema validation test; POST `/api/v1/reports/incidents` |
| **FR-9** | Dashboard Summaries & UI Metrics | Person B | MVP (Phase 1) | Frontend end-to-end user workflow test |
| **NFR-1** | CRS Segregation (`EPSG:4326` / `EPSG:32643`) | Person A & B | Phase 0–1 | Automated test `test_data_validation.py` |
| **NFR-2** | Performance & Response Latency | Person A & B | Phase 1–2 | Benchmarking with Locust / pytest-benchmark |
| **NFR-3** | Graceful Fallback & Data Honesty | Person A & B | Phase 0–1 | Integration tests with empty data directories |
| **NFR-7** | Navigational Safety Advisory | Person B | Phase 0–1 | Visual UI inspection across all route components |
