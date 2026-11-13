# FloodLens — Data Sources & Acquisition Registry

> **Document Status:** Phase 0 Baseline  
> **Lead Owner:** Person B (Infrastructure & Feature Engineering Lead)  
> **Secondary Reviewer:** Person A (Flood & Terrain Lead)  
> **Study Area:** Bengaluru Metropolitan Region, Karnataka, India  
> **Bounding Envelope Reference (Sanity Envelope):** $77.40^\circ\text{E} \text{ to } 77.85^\circ\text{E},\; 12.75^\circ\text{N} \text{ to } 13.20^\circ\text{N}$

---

## 1. Overview & Data Governance Principles

The FloodLens platform combines empirical historical flood incident records, topographical elevation rasters, hydrological networks, and transportation graphs. To maintain rigorous scientific provenance:
1. **Raw Data Immutability:** Files placed in `data/raw/` must never be directly modified, overwritten, or manually edited.
2. **Strict Ownership Segregation:** Dataset acquisition, initial format checks, and placement are partitioned strictly between Person A and Person B.
3. **No Speculative Data:** No synthetic flood observations, invented download links, unverified accuracy metrics, or artificial coverage claims are permitted. Any unconfirmed parameter is explicitly flagged as **[Requires Phase 1 On-Ground / Portal Verification]**.
4. **Automated Auditing:** Following dataset placement, all files are programmatically validated using `scripts/inspect_datasets.py` to record Coordinate Reference Systems (CRS), geometry counts, and bounding box overlap into `data/metadata/data_inventory.csv`.

---

## 2. Agreed Team Ownership Allocation

Following the finalized team agreement, dataset acquisition and curation responsibilities are structured as follows:

| Responsible Lead | Domain | Datasets Covered | Target Raw Directory |
| :--- | :--- | :--- | :--- |
| **Person A** | **Flood & Terrain Datasets** | • BBMP Historical Flood Locations<br>• BBMP Flood-Prone Hotspots<br>• BBMP Low-Lying Geographical Areas<br>• Copernicus DEM GLO-30 Raster | `data/raw/flood_locations/`<br>`data/raw/flood_locations/`<br>`data/raw/low_lying_areas/`<br>`data/raw/elevation/` |
| **Person B** | **Infrastructure Datasets** | • BBMP Road Centrelines<br>• OpenStreetMap Navigable Roads<br>• BBMP Stormwater Drains (*Rajakaluves*)<br>• ATREE Lakes & Streams (*Keres*) | `data/raw/roads/`<br>`data/raw/roads/`<br>`data/raw/drainage/`<br>`data/raw/water_bodies/` |

> [!NOTE]
> **Resolution of Architectural Scaffolding Inconsistency:**  
> In early Phase 0 scaffold notes (`docs/architecture.md`), Copernicus DEM had tentatively been tagged under Person B and OSM roads under Person A. Under the finalized Phase 0 agreement reflected in `data/metadata/data_sources.csv` and this document:
> - **Person A** leads raw flood and terrain dataset acquisition (including Copernicus DEM GLO-30 acquisition).
> - **Person B** leads infrastructure dataset acquisition and cleaning (roads, SWD drains, lakes), while performing terrain feature extraction (slopes, relative depressions) from Person A's DEM raster.
> - **Person A** takes Person B's cleaned road network to construct the topological graph in OSMnx/NetworkX.

---

## 3. Person A — Flood and Terrain Datasets

### 3.1 BBMP Historical Flood Locations (`bbmp_hist_floods`)
- **Publisher / Source:** Bruhat Bengaluru Mahanagara Palike (BBMP) Disaster Management Cell / Karnataka State Natural Disaster Monitoring Centre (KSNDMC) / OpenCity Bengaluru portal.
- **Intended Use:** Serves as empirical ground truth for historical inundations; provides primary point inputs for DBSCAN spatial clustering and historical exposure scoring.
- **Expected Format:** `.geojson`, `.shp` (with `.shx`, `.dbf`, `.prj`), `.kml`, or `.kmz`.
- **Geographic Coverage:** Bengaluru municipal administrative wards (198 legacy wards / 243 expanded wards).
- **Coordinate Reference System (CRS):** Typically published in `EPSG:4326` (WGS 84); requires verification during Phase 1 ingestion.
- **Target Directory:** `data/raw/flood_locations/`
- **Responsible Member:** **Person A**
- **Limitations & Quality Considerations:**
  - *Reporting Bias:* Observations are skewed toward densely populated commercial hubs (e.g., Koramangala, Indiranagar, HSR Layout) where citizen smartphones and media coverage are concentrated; peripheral peri-urban wards may be underreported.
  - *Temporal Ambiguity:* Older incident records often specify the year or month without exact timestamps or storm duration context.
  - *Positional Precision:* Coordinates may represent generalized ward centers, traffic junctions, or road intersections rather than the exact micro-depression point of water ponding.
  - *Availability Check:* Availability and completeness of recent monsoon seasons [Requires Phase 1 Verification].

---

### 3.2 BBMP Flood-Prone Hotspots (`bbmp_flood_prone`)
- **Publisher / Source:** BBMP Traffic and Engineering Departments / Karnataka State Police (Traffic Management Centre) / OpenCity Bengaluru.
- **Intended Use:** Identifies chronically vulnerable arterial junctions, railway underpasses, and low-lying transit choke points that experience recurring inundation even during moderate showers.
- **Expected Format:** `.geojson`, `.shp`, `.kml`, or `.kmz`.
- **Geographic Coverage:** Bengaluru Metropolitan Area transit junctions and known underpasses (e.g., Kino Theatre underpass, Okalipuram, Le Méridien underpass, Silk Board).
- **Coordinate Reference System (CRS):** Typically `EPSG:4326` (WGS 84) [Requires Phase 1 Verification].
- **Target Directory:** `data/raw/flood_locations/`
- **Responsible Member:** **Person A**
- **Limitations & Quality Considerations:**
  - Many flood-prone lists published in local portals are text-based tabular PDFs requiring manual geocoding or cross-referencing against verified landmark gazetteers.
  - Point locations do not delineate inundation surface area or ponding depth boundaries.

---

### 3.3 BBMP Low-Lying Geographical Areas (`bbmp_low_lying`)
- **Publisher / Source:** BBMP Stormwater Drainage Master Plan / OpenCity Bengaluru / Department of Town Planning.
- **Intended Use:** Vector polygons delineating natural valley depressions, lake basin buffer limits, and catchment bowls prone to runoff pooling; integrated into spatial exposure feature calculation.
- **Expected Format:** Polygon `.shp`, `.geojson`, or `.kml`.
- **Geographic Coverage:** Major Bengaluru valley catchments (Vrishabhavathi Valley, Koramangala-Challaghatta (K-C) Valley, Hebbal Valley).
- **Coordinate Reference System (CRS):** Often distributed in local projected grids or `EPSG:4326` [Requires Phase 1 CRS Check via `inspect_datasets.py`].
- **Target Directory:** `data/raw/low_lying_areas/`
- **Responsible Member:** **Person A**
- **Limitations & Quality Considerations:**
  - Boundary demarcations may reflect planning estimates rather than surveyed topographical contour bounds.
  - Complex multi-polygon geometries frequently exhibit topology defects (sliver polygons, unclosed rings, self-intersections) requiring automated Shapely `make_valid` remediation.

---

### 3.4 Copernicus DEM GLO-30 (`copernicus_dem`)
- **Publisher / Source:** European Space Agency (ESA) Copernicus Open Access Hub / OpenTopography portal.
- **Intended Use:** Digital Elevation Model providing continuous ground surface elevation (meters ASL) for topographical slope calculation, low-elevation sink identification, and valley basin profiling.
- **Expected Format:** Single-band 32-bit floating point GeoTIFF (`.tif`).
- **Geographic Coverage:** 1-degree geographic tiles covering $77^\circ\text{E} \text{ to } 78^\circ\text{E}$ and $12^\circ\text{N} \text{ to } 14^\circ\text{N}$ (specifically tiles `Copernicus_DSM_COG_10_N12_00_E077_00_DEM` and `Copernicus_DSM_COG_10_N13_00_E077_00_DEM`).
- **Coordinate Reference System (CRS):** Native `EPSG:4326` (WGS 84 geographic coordinates, ellipsoidal/orthometric height).
- **Target Directory:** `data/raw/elevation/`
- **Responsible Member:** **Person A** (Acquisition & Tiling) / **Person B** (Feature Processing)
- **Limitations & Quality Considerations:**
  - *Spatial Resolution (30m):* A 30-meter grid pixel aggregates elevation over a 900 $m^2$ footprint; micro-scale urban features (road curbs, storm drain culverts, flyovers, sub-15m underpasses) are smoothed out.
  - *Digital Surface Model (DSM) Canopy Artifacts:* Copernicus GLO-30 is a surface model and may reflect tree canopies, dense vegetation, or large industrial roof elevations rather than bare ground surface.

---

## 4. Person B — Infrastructure Datasets

### 4.1 BBMP Road Centrelines (`bbmp_road_centrelines`)
- **Publisher / Source:** BBMP Major Roads Department / Karnataka Geographic Information System (KGIS) / OpenCity Bengaluru.
- **Intended Use:** Official municipal centerline geometry for designated arterial, sub-arterial, and ward roads; provides administrative attribution and hierarchy validation.
- **Expected Format:** `.shp`, `.geojson`, or `.gpkg`.
- **Geographic Coverage:** Bruhat Bengaluru Mahanagara Palike administrative limits (~800 $km^2$).
- **Coordinate Reference System (CRS):** Native CRS typically `EPSG:4326` or UTM Zone 43N (`EPSG:32643`) [Requires Phase 1 Verification].
- **Target Directory:** `data/raw/roads/`
- **Responsible Member:** **Person B**
- **Limitations & Quality Considerations:**
  - Completeness varies: Arterial and sub-arterial corridors are well-mapped, but local residential lanes and newly developing outer layouts may be missing or unaligned.
  - Lacks strict routable topological connectivity (frequent dangling nodes, disconnected intersections) making it unsuitable for direct graph traversal without topological rebuilding.

---

### 4.2 OpenStreetMap Roads (`osm_roads`)
- **Publisher / Source:** OpenStreetMap contributors, extracted via Geofabrik India regional extract (`geofabrik.de`) or automated bounding query via `osmnx`.
- **Intended Use:** Serves as the primary routable topological baseline for graph construction (Person A) and comparative shortest vs risk-aware routing (Person B).
- **Expected Format:** `.pbf`, `.osm`, `.geojson`, `.gpkg`, or direct OSMnx graph serialization (`.graphml`).
- **Geographic Coverage:** Greater Bengaluru metropolitan area spanning the full sanity envelope ($77.40^\circ\text{E}$ to $77.85^\circ\text{E}$, $12.75^\circ\text{N}$ to $13.20^\circ\text{N}$).
- **Coordinate Reference System (CRS):** Native `EPSG:4326` (WGS 84).
- **Target Directory:** `data/raw/roads/`
- **Responsible Member:** **Person B** (Acquisition & Raw Cleaning) / **Person A** (Graph Extraction & Routing Topology)
- **Limitations & Quality Considerations:**
  - Tagging inconsistencies across volunteer mappers (e.g., varying usage of `highway=trunk` vs `highway=primary`, incomplete `oneway` tags).
  - High density of non-driveable footways, tracks, and service alleys that must be filtered out during preprocessing to maintain routing graph performance.

---

### 4.3 BBMP Stormwater Drainage Network (`bbmp_drainage`)
- **Publisher / Source:** BBMP Stormwater Drainage (SWD) Department / Karnataka State Remote Sensing Applications Centre (KSRSAC) / OpenCity Bengaluru.
- **Intended Use:** Delineates major arterial canals (*primary rajakaluves*), feeder canals (*secondary rajakaluves*), and roadside collector channels (*tertiary drains*); used to compute metric proximity and buffer vulnerability zones.
- **Expected Format:** Polyline `.shp`, `.geojson`, or `.kml`.
- **Geographic Coverage:** BBMP municipal zones covering the primary valley drainage networks.
- **Coordinate Reference System (CRS):** Ingested in native format [Requires Phase 1 Verification]; reprojected to `EPSG:32643` for metric buffer queries.
- **Target Directory:** `data/raw/drainage/`
- **Responsible Member:** **Person B**
- **Limitations & Quality Considerations:**
  - *Subsurface & Culverted Segments:* Major portions of the urban drainage network are covered by box culverts or enclosed under road intersections; open GIS shapefiles often omit underground drain continuity.
  - *Siltation & Maintenance Status:* Spatial vectors represent channel alignments only, without data on silt accumulation, structural remodeling, debris clogs, or operational capacity.
  - *Positional Offset:* Canal alignments in older digitized maps may deviate by 10 to 30 meters from current satellite basemaps due to urban encroachment.

---

### 4.4 ATREE Lakes and Streams (`atree_water_bodies`)
- **Publisher / Source:** Ashoka Trust for Research in Ecology and the Environment (ATREE) Bangalore Lakes Project / OpenCity Bengaluru / KLCDA.
- **Intended Use:** Identifies inland water bodies (*keres*), historic lake beds, and seasonal inter-connecting streams; used to compute lake proximity risk ($L_e$) and identify flood backwater zones.
- **Expected Format:** Polygon `.shp`, `.geojson`, or `.gpkg`.
- **Geographic Coverage:** Greater Bengaluru Urban and Rural districts (including peripheral cascading chains).
- **Coordinate Reference System (CRS):** Typically `EPSG:4326` (WGS 84) [Requires Phase 1 Verification].
- **Target Directory:** `data/raw/water_bodies/`
- **Responsible Member:** **Person B**
- **Limitations & Quality Considerations:**
  - *Dynamic Water Spread vs Mapped Boundary:* Vector boundaries generally reflect cadastral boundaries or full tank level (FTL), which may differ substantially from dry-season vs monsoon-season water surfaces.
  - *Extinct / Encroached Lakes:* Several historical water bodies have been converted into bus stands, sports stadiums, or residential layouts; spatial layers must be inspected to verify active vs historic status.

---

## 5. Optional Auxiliary Datasets

The platform architecture configures optional directories in `data/raw/` for secondary enrichment:

| Dataset ID | Dataset Name | Source Agency | Intended Use | Format | Owner | Priority |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `nasa_gpm_rainfall` | NASA GPM IMERG Precipitation | NASA Earthdata / Giovanni | Gridded satellite rainfall estimates during severe monsoon episodes. | GeoTIFF (`.tif`) / NetCDF (`.nc`) | Person B | Optional / Post-MVP |
| `dynamic_world_lc` | Dynamic World Land Cover | WRI / Google Earth Engine | High-resolution (10m) impervious surface vs permeable land use layers. | GeoTIFF (`.tif`) | Person B | Optional / Post-MVP |

---

## 6. Dataset Placement & Inspection Protocol

When downloading and staging raw spatial files:

```bash
# 1. Place downloaded files in their dedicated data/raw subdirectories:
#    - data/raw/flood_locations/   (Person A)
#    - data/raw/low_lying_areas/    (Person A)
#    - data/raw/elevation/          (Person A)
#    - data/raw/roads/              (Person B)
#    - data/raw/drainage/           (Person B)
#    - data/raw/water_bodies/       (Person B)

# 2. Run the automated inspection suite:
python scripts/inspect_datasets.py

# 3. Verify results in console and inspect the generated catalog:
cat data/metadata/data_inventory.csv
```

### Verification Criteria Checklist:
- [ ] Multi-part files (Shapefiles `.shp`, `.shx`, `.dbf`, `.prj`) placed intact in the same directory.
- [ ] Bounding box overlaps Bengaluru sanity envelope ($77.40^\circ\text{E} \le \text{lon} \le 77.85^\circ\text{E}$ and $12.75^\circ\text{N} \le \text{lat} \le 13.20^\circ\text{N}$).
- [ ] Coordinate reference system detected and recorded.
- [ ] Zero null or unrecoverable empty geometries detected.
- [ ] No raw spatial binaries committed to git (verified by `.gitignore`).
