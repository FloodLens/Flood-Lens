# FloodLens — Data Dictionary Specification

> **Document Status:** Phase 0 Baseline  
> **Lead Owner:** Person B (Requirements & Data Analytics Lead)  
> **Secondary Reviewer:** Person A (System Architecture & GeoAI Lead)  
> **Reference Systems:**  
> - Web Interchange & Visualization: `EPSG:4326` (WGS 84, Latitude/Longitude in decimal degrees)  
> - Metric Spatial Processing: `EPSG:32643` (WGS 84 / UTM Zone 43N, Metric units)  

---

## 1. Architectural Entity Overview

The FloodLens data architecture is partitioned into three distinct operational categories to ensure strict data provenance, reproducibility, and separation of raw records from analytical derivations:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. RAW DATASETS (data/raw/)                                                 │
│    • Historical Flood Observations (Person A)                               │
│    • Low-Lying Geographical Areas (Person A)                                │
│    • Digital Elevation Model (DEM) (Person A Acquisition / Person B Usage)  │
│    • Road Network Segments (Person B Acquisition / Person A Graph)          │
│    • Stormwater Drains / Rajakaluves (Person B)                             │
│    • Lakes & Streams / Keres (Person B)                                     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Preprocessing & Reprojection (EPSG:32643)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. DERIVED SPATIAL FEATURES (data/processed/)                               │
│    • Terrain Features (Elevation, Slope %, Depression) (Person B)           │
│    • Flood Exposure Features (Cluster Distances, Proximity) (Person A)      │
│    • Composite Vulnerability Scores (Multi-Criteria Index) (Person B)       │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Graph Impedance & Model Execution
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. GEOAI & ANALYTICAL MODEL OUTPUTS                                         │
│    • DBSCAN Cluster Information (Person A)                                  │
│    • Route Comparison Results (Person B)                                    │
│    • Community Incident Reports (Person B UI & Supporting API)              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Raw Datasets (`data/raw/`)

### 2.1 Historical Flood Observations
- **Target Directory:** `data/raw/flood_locations/`
- **Lead Owner:** Person A
- **Primary Source:** Bruhat Bengaluru Mahanagara Palike (BBMP) Disaster Management Cell / Karnataka State Natural Disaster Monitoring Centre (KSNDMC) / OpenCity Bengaluru.
- **Expected Geometry:** `Point` or `MultiPoint`
- **Reference CRS:** Ingested in native format (typically `EPSG:4326`); reprojected to `EPSG:32643` for metric analysis.

| Field Name | Data Type | Units | Geometry Type | Mandatory? | Source / Stage | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `incident_id` | String | None | Point | Yes | Raw Source / BBMP | Unique serial identifier for the recorded flood incident (e.g., `BBMP_FLD_2022_041`). |
| `location_name` | String | None | Point | Yes | Raw Source / BBMP | Descriptive landmark, junction, ward name, or underpass (e.g., "Koramangala 80ft Road", "Silk Board Junction"). |
| `latitude` | Float | Decimal Degrees | Point | Yes | Raw Source / BBMP | Latitude coordinate in WGS 84 (`EPSG:4326`). Must fall within $[12.75, 13.20]$. |
| `longitude` | Float | Decimal Degrees | Point | Yes | Raw Source / BBMP | Longitude coordinate in WGS 84 (`EPSG:4326`). Must fall within $[77.40, 77.85]$. |
| `incident_year` | Integer | Year (YYYY) | Point | Optional | Raw Source / BBMP | Calendar year during which the inundation event occurred (e.g., `2022`). |
| `severity` | String | None | Point | Optional | Raw Source / BBMP | Qualitative severity classification reported by municipal agency (`Low`, `Medium`, `High`, `Critical`). |
| `ward_id` | Integer / String | None | Point | Optional | Raw Source / BBMP | Administrative BBMP ward number (1 to 198 / 243). |
| `source_agency` | String | None | Point | Yes | Raw Source / BBMP | Originating agency or data publisher (e.g., `BBMP`, `KSNDMC`, `Traffic_Police`). |

---

### 2.2 Low-Lying Geographical Areas
- **Target Directory:** `data/raw/low_lying_areas/`
- **Lead Owner:** Person A
- **Primary Source:** BBMP Stormwater Drainage Master Plan / OpenCity Bengaluru.
- **Expected Geometry:** `Polygon` or `MultiPolygon`
- **Reference CRS:** Ingested in native format; converted to `EPSG:4326` for visualization and `EPSG:32643` for spatial intersection.

| Field Name | Data Type | Units | Geometry Type | Mandatory? | Source / Stage | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `area_id` | String | None | Polygon | Yes | Raw Source / BBMP | Unique identifier for the low-lying zone polygon. |
| `area_name` | String | None | Polygon | Yes | Raw Source / BBMP | Name of the valley, depression basin, or localized catchment (e.g., "Challaghatta Valley Basin", "Hebbal Catchment"). |
| `zone_name` | String | None | Polygon | Optional | Raw Source / BBMP | BBMP administrative zone (e.g., "Mahadevapura", "Bommanahalli", "East"). |
| `depression_type`| String | None | Polygon | Optional | Raw Source / BBMP | Category of depression: `Natural Valley`, `Lakebed Buffer`, `Underpass Basin`, `Drainage Sink`. |
| `geometry` | Polygon / MultiPolygon | Coordinates | Polygon | Yes | Raw Source / BBMP | Planar vector boundary enclosing the low-lying depression. Must pass `make_valid`. |

---

### 2.3 Digital Elevation Model (DEM)
- **Target Directory:** `data/raw/elevation/`
- **Lead Owner:** Person A (Acquisition) / Person B (Feature Extraction & Profiling)
- **Primary Source:** European Space Agency (ESA) Copernicus DEM GLO-30 / OpenTopography.
- **Representation:** Single-band GeoTIFF raster (`.tif`).
- **Spatial Resolution:** 30m grid spacing.
- **Reference CRS:** Native `EPSG:4326` (geographic ellipsoidal height) or projected `EPSG:32643` (metric orthometric height).

| Field / Band | Data Type | Units | Geometry Type | Mandatory? | Source / Stage | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `band_1` | Float32 | Meters (m) | Raster Pixel Grid | Yes | Raw Raster / ESA | Orthometric surface elevation above mean sea level (MSL) in meters. |
| `pixel_width` | Float | Meters / Degrees | Raster Header | Yes | GeoTIFF Header | Spatial resolution in X direction (approx 30m or ~0.0002778°). |
| `pixel_height` | Float | Meters / Degrees | Raster Header | Yes | GeoTIFF Header | Spatial resolution in Y direction (approx 30m or ~0.0002778°). |
| `nodata_value` | Float32 | None | Raster Header | Yes | GeoTIFF Header | Sentinel flag indicating voids or ocean boundaries (typically `-9999.0` or `None`). |

---

### 2.4 Road Network Segments (Raw)
- **Target Directory:** `data/raw/roads/`
- **Lead Owner:** Person B (Acquisition & Cleaning) / Person A (Graph Construction)
- **Primary Source:** OpenStreetMap (OSM via Geofabrik / OSMnx) / BBMP Major Roads Department.
- **Expected Geometry:** `LineString` or `MultiLineString`
- **Reference CRS:** Ingested in `EPSG:4326`; projected to `EPSG:32643` for topological graph analysis.

| Field Name | Data Type | Units | Geometry Type | Mandatory? | Source / Stage | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `osm_id` | String / Integer | None | LineString | Yes | Raw Source / OSM | Unique OpenStreetMap way or segment identifier. |
| `name` | String | None | LineString | Optional | Raw Source / OSM | Official street or highway name (e.g., "Outer Ring Road", "Hosur Road"). |
| `highway` | String | None | LineString | Yes | Raw Source / OSM | Functional highway classification (`primary`, `secondary`, `tertiary`, `residential`, `trunk`). |
| `oneway` | Boolean / String | None | LineString | Optional | Raw Source / OSM | Directional restriction indicator (`yes`, `no`, `true`, `false`). |
| `maxspeed` | Integer / String | km/h | LineString | Optional | Raw Source / OSM | Legal posted speed limit in kilometers per hour. |
| `lanes` | Integer | Count | LineString | Optional | Raw Source / OSM | Number of vehicular travel lanes. |
| `bridge` | String | None | LineString | Optional | Raw Source / OSM | Elevated structure tag (`yes`, `viaduct`, `flyover`) indicating road elevation above ground. |
| `tunnel` | String | None | LineString | Optional | Raw Source / OSM | Subsurface structure tag (`yes`, `underpass`, `subway`) indicating road depression below ground. |
| `geometry` | LineString | Coordinates | LineString | Yes | Raw Source / OSM | Centerline geometry of the road segment. |

---

### 2.5 Stormwater Drains (Rajakaluves)
- **Target Directory:** `data/raw/drainage/`
- **Lead Owner:** Person B
- **Primary Source:** BBMP Stormwater Drainage (SWD) Department / OpenCity Bengaluru.
- **Expected Geometry:** `LineString` or `MultiLineString`
- **Reference CRS:** Ingested in native vector format; projected to `EPSG:32643` for metric buffer calculations.

| Field Name | Data Type | Units | Geometry Type | Mandatory? | Source / Stage | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `drain_id` | String | None | LineString | Yes | Raw Source / BBMP | Unique identifier for the stormwater drain channel segment. |
| `drain_name` | String | None | LineString | Optional | Raw Source / BBMP | Common name of the canal or rajakaluve (e.g., "K-100 Citizen's Waterway", "Challaghatta Main Drain"). |
| `drain_type` | String | None | LineString | Yes | Raw Source / BBMP | Hierarchical drainage classification: `Primary` (Major arterial rajakaluve), `Secondary` (Collector feeder), `Tertiary` (Local roadside drain). |
| `status` | String | None | LineString | Optional | Raw Source / BBMP | Structural status: `Open`, `Covered Box Drain`, `Encroached`, `Remodeled`. |
| `width_m` | Float | Meters (m) | LineString | Optional | Raw Source / BBMP | Estimated average channel top width in meters. |
| `length_m` | Float | Meters (m) | LineString | Optional | Raw Source / BBMP | Recorded linear segment length in meters. |
| `geometry` | LineString | Coordinates | LineString | Yes | Raw Source / BBMP | Polyline vector tracking the channel alignment. |

---

### 2.6 Lakes and Streams (Keres)
- **Target Directory:** `data/raw/water_bodies/`
- **Lead Owner:** Person B
- **Primary Source:** Ashoka Trust for Research in Ecology and the Environment (ATREE) / OpenCity Bengaluru / KLCDA (Karnataka Lake Conservation and Development Authority).
- **Expected Geometry:** `Polygon` or `MultiPolygon`
- **Reference CRS:** Ingested in native vector format; projected to `EPSG:32643` for perimeter buffer calculation.

| Field Name | Data Type | Units | Geometry Type | Mandatory? | Source / Stage | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `lake_id` | String | None | Polygon | Yes | Raw Source / ATREE | Unique identifier for the water body polygon. |
| `lake_name` | String | None | Polygon | Yes | Raw Source / ATREE | Common lake name (e.g., "Bellandur Kere", "Varthur Lake", "Ulsoor Lake", "Hebbal Lake"). |
| `series_name` | String | None | Polygon | Optional | Raw Source / ATREE | Hydrological cascading lake chain (e.g., "Koramangala-Challaghatta Series", "Vrishabhavathi Series", "Hebbal Series"). |
| `area_sqm` | Float | Square Meters ($m^2$) | Polygon | Optional | Raw Source / ATREE | Total surface area of water body polygon in square meters. |
| `status` | String | None | Polygon | Optional | Raw Source / ATREE | Ecological and physical condition: `Live Lake`, `Degraded`, `Encroached Lakebed`, `Seasonal Wetland`. |
| `geometry` | Polygon / MultiPolygon | Coordinates | Polygon | Yes | Raw Source / ATREE | Boundary polygon defining the full tank level (FTL) or mapped water boundary. |

---

## 3. Derived Spatial Features (`data/processed/`)

Derived spatial features are generated through metric geometric joins, raster sampling, and spatial analysis executed in `EPSG:32643` (UTM Zone 43N).

### 3.1 Terrain Features
- **Lead Owner:** Person B
- **Processing Module:** `backend/app/services/terrain_service.py` / `scripts/generate_features.py`
- **Derived From:** Copernicus DEM GLO-30 raster and road segment geometries.

| Field Name | Data Type | Units | Geometry Type | Mandatory? | Source / Stage | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `mean_elevation_m` | Float | Meters (m) | LineString | Yes | Derived (Person B) | Mean ground elevation sampled from Copernicus DEM along the road segment centerline. |
| `min_elevation_m` | Float | Meters (m) | LineString | Yes | Derived (Person B) | Minimum sampled ground elevation along the segment (captures localized dips). |
| `max_elevation_m` | Float | Meters (m) | LineString | Yes | Derived (Person B) | Maximum sampled ground elevation along the segment. |
| `slope_pct` | Float | Percent (%) | LineString | Yes | Derived (Person B) | Topographical slope gradient calculated as $\frac{|\Delta \text{Elevation}|}{\text{Segment Length}} \times 100\%$. |
| `relative_depression_m`| Float | Meters (m) | LineString | Yes | Derived (Person B) | Elevation difference between the segment mean elevation and the 500m moving average neighborhood baseline ($E_{\text{baseline}} - E_{\text{segment}}$). Positive values indicate topographical sinks. |
| `depression_score` | Float | Normalized [0, 1] | LineString | Yes | Derived (Person B) | Min-max scaled index representing topographic depression severity ($E_e$). Higher values denote deep sinks. |

---

### 3.2 Flood Exposure Features
- **Lead Owner:** Person A
- **Processing Module:** `backend/app/services/flood_service.py` / `scripts/generate_features.py`
- **Derived From:** Historical flood points, low-lying polygons, and DBSCAN cluster centroids.

| Field Name | Data Type | Units | Geometry Type | Mandatory? | Source / Stage | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `dist_to_flood_point_m` | Float | Meters (m) | LineString | Yes | Derived (Person A) | Minimum Euclidean distance from road segment to the nearest historical flood incident point in `EPSG:32643`. |
| `dist_to_cluster_m` | Float | Meters (m) | LineString | Yes | Derived (Person A) | Minimum Euclidean distance from road segment to the nearest DBSCAN core cluster centroid in `EPSG:32643`. |
| `nearest_cluster_id` | Integer | None | LineString | Yes | Derived (Person A) | Identifier of the nearest DBSCAN cluster (-1 indicates nearest incident was categorized as spatial noise). |
| `in_low_lying_polygon`| Boolean | True / False | LineString | Yes | Derived (Person A) | Binary flag indicating whether the road segment intersects a BBMP low-lying geographical area polygon. |
| `cluster_exposure_score`| Float | Normalized [0, 1] | LineString | Yes | Derived (Person A) | Inverse-distance decay score representing proximity to chronic flood clusters: $F_e = \exp(-\lambda \cdot \text{dist\_to\_cluster\_m})$. |

---

### 3.3 Infrastructure Proximity Features
- **Lead Owner:** Person B
- **Processing Module:** `backend/app/services/vulnerability_service.py` / `scripts/generate_features.py`
- **Derived From:** BBMP Stormwater Drains and ATREE Water Bodies.

| Field Name | Data Type | Units | Geometry Type | Mandatory? | Source / Stage | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `dist_to_drain_m` | Float | Meters (m) | LineString | Yes | Derived (Person B) | Minimum Euclidean distance from road segment to nearest stormwater drain centerline in `EPSG:32643`. |
| `in_drain_buffer_30m` | Boolean | True / False | LineString | Yes | Derived (Person B) | Flag indicating whether the road segment falls within the high-hazard 30m rajakaluve corridor. |
| `drainage_score` | Float | Normalized [0, 1] | LineString | Yes | Derived (Person B) | Scaled hazard score based on drain proximity ($D_e$): $1.0$ if $\le 30\text{m}$, decaying to $0.0$ at $>150\text{m}$. |
| `dist_to_lake_m` | Float | Meters (m) | LineString | Yes | Derived (Person B) | Minimum Euclidean distance from road segment to nearest mapped lake boundary polygon. |
| `in_lake_buffer_50m` | Boolean | True / False | LineString | Yes | Derived (Person B) | Flag indicating whether the road segment falls within the 50m lake periphery buffer. |
| `lake_score` | Float | Normalized [0, 1] | LineString | Yes | Derived (Person B) | Scaled hazard score based on water body proximity ($L_e$): $1.0$ if $\le 50\text{m}$, decaying to $0.0$ at $>200\text{m}$. |

---

### 3.4 Composite Vulnerability Scores
- **Lead Owner:** Person B
- **Processing Module:** `backend/app/services/vulnerability_service.py`
- **Target Output:** Attributed road network edges stored in `data/processed/roads/road_vulnerability_edges.geojson`.

| Field Name | Data Type | Units | Geometry Type | Mandatory? | Source / Stage | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `edge_id` | String | None | LineString | Yes | Derived (Person B) | Unique directed edge identifier formatted as `"u_v_key"` matching NetworkX graph topology. |
| `length_m` | Float | Meters (m) | LineString | Yes | Derived (Person B) | Physical edge length in meters computed in `EPSG:32643`. |
| `vulnerability_score` | Float | Normalized [0, 1] | LineString | Yes | Model Output (Person B) | Composite multi-criteria vulnerability index $V_e = w_f \cdot F_e + w_d \cdot D_e + w_l \cdot L_e + w_e \cdot E_e$. |
| `risk_tier` | String | None | LineString | Yes | Model Output (Person B) | Categorical tier: `Low` ($V_e \in [0.0, 0.33]$), `Medium` ($V_e \in (0.33, 0.66]$), `High` ($V_e \in (0.66, 1.0]$). |
| `impedance_weight` | Float | Weighted Cost | LineString | Yes | Model Output (Person B) | Routing cost used for risk-weighted Dijkstra: $w_e = \text{length\_m} \cdot (1.0 + \alpha \cdot V_e^\beta)$. |
| `dominant_factor` | String | None | LineString | Yes | Model Output (Person B) | Primary driver contributing the highest weighted share to $V_e$ (`Drainage Proximity`, `Historical Flood Hotspot`, `Topographical Sink`, `Lake Buffer`). |

---

## 4. GeoAI & Analytical Model Outputs

### 4.1 DBSCAN Spatial Cluster Information
- **Lead Owner:** Person A
- **Endpoint:** `GET /api/v1/floods/clusters`
- **Underlying Schema:** `backend/app/schemas/flood.py` (`FloodClusterSchema`)
- **Processing Stage:** Unsupervised density clustering executed in `scikit-learn` over projected incident coordinates in `EPSG:32643`.

| Field Name | Data Type | Units | Mandatory? | Source / Stage | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `cluster_id` | Integer | None | Yes | GeoAI Model (Person A) | Cluster index assigned by DBSCAN. Core clusters $\ge 0$; spatial noise points designated as $-1$. |
| `center_latitude` | Float | Decimal Degrees | Yes | GeoAI Model (Person A) | Geographic centroid latitude of the cluster core in `EPSG:4326`. |
| `center_longitude`| Float | Decimal Degrees | Yes | GeoAI Model (Person A) | Geographic centroid longitude of the cluster core in `EPSG:4326`. |
| `point_count` | Integer | Count | Yes | GeoAI Model (Person A) | Number of historical flood incidents contained within the dense cluster core ($n \ge \text{min\_samples}$). |
| `radius_meters` | Float | Meters (m) | Yes | GeoAI Model (Person A) | Maximum distance from the centroid to member incidents, representing spatial footprint spread. |

---

### 4.2 Route Comparison Results
- **Lead Owner:** Person B
- **Endpoint:** `POST /api/v1/routes/compare`
- **Underlying Schema:** `backend/app/schemas/route.py` (`RouteComparisonResponse`, `RouteResult`)
- **Processing Stage:** Dual Dijkstra / A* graph optimization executed on NetworkX graph.

| Field Name | Data Type | Units | Mandatory? | Source / Stage | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `origin` | LatLng Object | Coordinates | Yes | Client Input | User-selected origin coordinates `{"latitude": float, "longitude": float}`. |
| `destination` | LatLng Object | Coordinates | Yes | Client Input | User-selected destination coordinates `{"latitude": float, "longitude": float}`. |
| `status` | String | None | Yes | API Status (Person B) | Execution status flag: `"completed"`, `"pending_road_network"`, `"no_path_found"`, `"out_of_bounds"`. |
| `message` | String | None | Optional | API Status (Person B) | Informative system message explaining status or data prerequisites. |
| `shortest_route` | RouteResult Object| Complex | Optional | Model Output (Person B) | Standard minimum-distance path result (null if graph offline). |
| `shortest_route.route_type` | Literal String | None | Yes | Model Output (Person B) | Fixed value `"shortest"`. |
| `shortest_route.distance_meters` | Float | Meters (m) | Yes | Model Output (Person B) | Total cumulative length of the shortest path. |
| `shortest_route.exposure_score` | Float | Normalized [0, 1] | Yes | Model Output (Person B) | Distance-weighted average vulnerability score along the shortest path: $\bar{V} = \frac{\sum V_e \cdot l_e}{\sum l_e}$. |
| `shortest_route.exposure_tier` | Literal String | None | Yes | Model Output (Person B) | Categorical tier for the route: `"Low"`, `"Medium"`, or `"High"`. |
| `shortest_route.coordinates` | Array of [Lon, Lat]| Decimal Degrees | Yes | Model Output (Person B) | Ordered sequence of coordinate pairs forming the LineString geometry in `EPSG:4326`. |
| `shortest_route.explanation` | String | None | Optional | Model Output (Person B) | Textual explanation of route exposure characteristics and identified choke points. |
| `risk_aware_route` | RouteResult Object| Complex | Optional | Model Output (Person B) | Exposure-penalized path result (null if graph offline). |
| `risk_aware_route.route_type` | Literal String | None | Yes | Model Output (Person B) | Fixed value `"risk_aware"`. |
| `risk_aware_route.distance_meters` | Float | Meters (m) | Yes | Model Output (Person B) | Total cumulative length of the risk-averse path. |
| `risk_aware_route.exposure_score` | Float | Normalized [0, 1] | Yes | Model Output (Person B) | Distance-weighted average vulnerability score along the risk-averse path. |
| `risk_aware_route.exposure_tier` | Literal String | None | Yes | Model Output (Person B) | Categorical tier for the route: `"Low"`, `"Medium"`, or `"High"`. |
| `risk_aware_route.coordinates` | Array of [Lon, Lat]| Decimal Degrees | Yes | Model Output (Person B) | Ordered sequence of coordinate pairs forming the LineString geometry in `EPSG:4326`. |
| `risk_aware_route.explanation` | String | None | Optional | Model Output (Person B) | Textual explanation detailing how the route detours away from vulnerable segments. |
| `delta_distance_meters` | Float | Meters (m) | Optional | Model Output (Person B) | Physical distance difference: $\text{Distance}_{\text{risk-aware}} - \text{Distance}_{\text{shortest}}$. |
| `delta_exposure_percentage` | Float | Percent (%) | Optional | Model Output (Person B) | Percentage reduction in flood exposure: $\frac{\text{Exp}_{\text{shortest}} - \text{Exp}_{\text{risk}}}{\text{Exp}_{\text{shortest}}} \times 100\%$. |

---

### 4.3 Community Flood Incident Reports
- **Lead Owner:** Person B (UI & Supporting API Endpoint)
- **Target Endpoint:** `POST /api/v1/reports/incidents`
- **Data Store:** In-memory store / `data/processed/reports/community_reports.json`
- **Processing Stage:** Citizen crowdsourcing ingestion with Pydantic validation.

| Field Name | Data Type | Units | Geometry Type | Mandatory? | Source / Stage | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `report_id` | String | None | Point | Yes | System Generated | Unique submission UUID (e.g., `REP_20261113_A8F2`). |
| `latitude` | Float | Decimal Degrees | Point | Yes | Citizen Input | Incident latitude coordinate in WGS 84 (`EPSG:4326`). Must fall within $[12.75, 13.20]$. |
| `longitude` | Float | Decimal Degrees | Point | Yes | Citizen Input | Incident longitude coordinate in WGS 84 (`EPSG:4326`). Must fall within $[77.40, 77.85]$. |
| `category` | String | None | Point | Yes | Citizen Input | Incident category: `Street Inundation`, `Underpass Waterlogging`, `Storm Drain Overflow`, `Lakebed Backflow`, `Traffic Disruption`. |
| `severity` | String | None | Point | Yes | Citizen Input | Qualitative severity: `Low` (Ankle deep / passable), `Medium` (Knee deep / passenger cars halted), `High` (Waist deep / impassable). |
| `description` | String | None | Point | Optional | Citizen Input | Anonymized landmark or event description (max 250 characters; PII stripped). |
| `submitted_at` | String (ISO 8601)| UTC Timestamp | Point | Yes | System Generated | ISO 8601 formatted timestamp of submission (e.g., `2026-11-13T19:30:00Z`). |
| `verification_status`| String | None | Point | Yes | System Default | Verification lifecycle flag: `Unverified` (default), `Community Corroborated`, `Official Confirmed`. |

---

## 5. Summary Attribute Matrix

| Entity Category | Entity Name | Primary Owner | Storage Format | Coordinate CRS | Target Directory / Endpoint |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Raw Dataset** | Historical Flood Points | Person A | GeoJSON / SHP / KML | `EPSG:4326` | `data/raw/flood_locations/` |
| **Raw Dataset** | Low-Lying Geographical Areas | Person A | GeoJSON / Shapefile | `EPSG:4326` | `data/raw/low_lying_areas/` |
| **Raw Dataset** | Digital Elevation Model (DEM) | Person A (acq) / B | GeoTIFF (`.tif`) | `EPSG:4326` / `EPSG:32643` | `data/raw/elevation/` |
| **Raw Dataset** | Road Network Segments | Person B (acq) / A | GeoJSON / Shapefile | `EPSG:4326` | `data/raw/roads/` |
| **Raw Dataset** | Stormwater Drains (SWD) | Person B | GeoJSON / Shapefile | `EPSG:4326` | `data/raw/drainage/` |
| **Raw Dataset** | Lakes & Streams (Keres) | Person B | GeoJSON / Shapefile | `EPSG:4326` | `data/raw/water_bodies/` |
| **Derived Feature** | Terrain Features | Person B | Parquet / GeoJSON | `EPSG:32643` | `data/processed/terrain/` |
| **Derived Feature** | Flood Exposure Features | Person A | Parquet / GeoJSON | `EPSG:32643` | `data/processed/flood/` |
| **Derived Feature** | Vulnerability Scores | Person B | GeoJSON / Parquet | `EPSG:4326` & `EPSG:32643` | `data/processed/roads/` |
| **Model Output** | DBSCAN Clusters | Person A | JSON / GeoJSON | `EPSG:4326` | `GET /api/v1/floods/clusters` |
| **Model Output** | Route Comparison Results | Person B | JSON / GeoJSON | `EPSG:4326` | `POST /api/v1/routes/compare` |
| **Model Output** | Community Incident Reports | Person B | JSON / GeoJSON | `EPSG:4326` | `POST /api/v1/reports/incidents` |
