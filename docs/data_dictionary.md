# FloodLens — Data Dictionary

This document details the expected attribute schemas, data types, and definitions for datasets across raw and processed states.

---

## 1. Raw Layers Schema

### A. Flood Incident Locations (`data/raw/flood_locations/`)
- **Geometry:** Point / MultiPoint
- **Typical Fields:**
  - `id` (String): Unique identifier / serial number
  - `name` / `location` (String): Landmark, ward name, or underpass name
  - `year` (Integer): Recorded incident year
  - `severity` (String / Integer): Qualitative or quantitative inundation level (Low, Medium, High)
  - `source` (String): Reporting agency (BBMP, Traffic Police, Citizen reports)

### B. Low-Lying Geographical Areas (`data/raw/low_lying_areas/`)
- **Geometry:** Polygon / MultiPolygon
- **Typical Fields:**
  - `area_name` (String): Ward or valley designation
  - `zone_id` (String / Integer): BBMP administrative zone
  - `type` (String): Valley depression, lakebed buffer, or underpass catchment

### C. Stormwater Drainage Network (`data/raw/drainage/`)
- **Geometry:** LineString / MultiLineString
- **Typical Fields:**
  - `drain_id` (String): Unique rajakaluve identifier
  - `drain_type` (String): `Primary`, `Secondary`, or `Tertiary`
  - `length_m` (Float): Segment length in meters
  - `width_m` (Float, optional): Average drain width

### D. Water Bodies (`data/raw/water_bodies/`)
- **Geometry:** Polygon / MultiPolygon
- **Typical Fields:**
  - `lake_name` (String): Lake / kere name (e.g., Bellandur, Varthur, Hebbal)
  - `area_acres` / `area_sqm` (Float): Surface area of water body
  - `status` (String): Active, degraded, or dried

### E. Digital Elevation Model (`data/raw/elevation/`)
- **Representation:** Single-band GeoTIFF raster
- **Pixel Value:** Elevation in meters above sea level (ASL, float32)
- **Spatial Resolution:** 30m grid (Copernicus DEM GLO-30)

---

## 2. Processed & Derived Layers (`data/processed/`)

### A. Processed Road Network Segments (`data/processed/roads/`)
- **Geometry:** LineString (EPSG:4326 for GeoJSON, EPSG:32643 for analysis)
- **Attributes:**
  - `edge_id` (String): Unique directed graph edge identifier
  - `length_m` (Float): Metric length in meters
  - `highway_type` (String): OSM classification (`primary`, `secondary`, `residential`)
  - `dist_to_drain_m` (Float): Minimum Euclidean distance to closest stormwater drain
  - `dist_to_lake_m` (Float): Minimum Euclidean distance to closest water body
  - `dist_to_flood_point_m` (Float): Distance to nearest recorded flood hotspot
  - `cluster_member` (Integer): DBSCAN cluster ID (-1 if isolated)
  - `mean_elevation_m` (Float): Mean elevation of road segment sampled from DEM
  - `slope_pct` (Float): Gradient / slope of road segment
  - `vulnerability_score` (Float): Normalized composite score between 0.0 (safest) and 1.0 (most vulnerable)
  - `risk_tier` (String): `Low` (0.0 - 0.33), `Medium` (0.34 - 0.66), `High` (0.67 - 1.0)
