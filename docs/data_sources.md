# FloodLens — Data Sources & File Placement Guide

This document lists all datasets required for the FloodLens platform, their source agencies, supported file formats, and exact placement directories.

---

## 1. Dataset Registry

| ID | Dataset Name | Source / Provider | Target Directory | Supported Formats | Owner | Required? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `bbmp_hist_floods` | Historical Flood Locations | BBMP Disaster Management / KSDMA | `data/raw/flood_locations/` | `.geojson`, `.shp`, `.kml`, `.kmz`, `.gpkg` | Person A | Yes |
| `bbmp_flood_prone` | Flood-Prone Vulnerability Points | BBMP / OpenCity Bengaluru | `data/raw/flood_locations/` | `.geojson`, `.shp`, `.kml`, `.kmz`, `.gpkg` | Person A | Yes |
| `bbmp_low_lying` | BBMP Low-Lying Geographical Areas | BBMP Engineering / OpenCity | `data/raw/low_lying_areas/` | `.geojson`, `.shp`, `.kml`, `.kmz` | Person A | Yes |
| `osm_roads` | Bengaluru Road Network | OpenStreetMap (via Geofabrik / OSMnx) | `data/raw/roads/` | `.geojson`, `.shp`, `.gpkg`, `.osm` | Person A | Yes |
| `bbmp_drainage` | Stormwater Drainage Network (SWD) | BBMP SWD Dept / OpenCity | `data/raw/drainage/` | `.geojson`, `.shp`, `.kml`, `.kmz` | Person B | Yes |
| `atree_water_bodies`| Bengaluru Lakes & Streams | ATREE Bengaluru / OpenCity | `data/raw/water_bodies/` | `.geojson`, `.shp`, `.gpkg` | Person B | Yes |
| `copernicus_dem` | Copernicus DEM GLO-30 | ESA Copernicus Open Access Hub | `data/raw/elevation/` | `.tif`, `.tiff` (GeoTIFF) | Person B | Yes |
| `nasa_gpm_rainfall`| NASA GPM IMERG Precipitation | NASA Earthdata / Giovanni | `data/raw/rainfall/` | `.tif`, `.nc` (GeoTIFF / NetCDF) | Person B | Optional |
| `dynamic_world_lc` | Google Dynamic World Land Cover | WRI / Google Earth Engine | `data/raw/land_cover/` | `.tif`, `.tiff` (GeoTIFF) | Person B | Optional |

---

## 2. Where to Download Each Dataset

1. **BBMP Historical Flood & Flood-Prone Locations:**
   - Source: OpenCity Bengaluru ([opencity.in](https://opencity.in)) / Karnataka State Natural Disaster Monitoring Centre (KSNDMC).
   - Format: KML, GeoJSON, or Shapefile.
2. **BBMP Low-Lying Geographical Areas:**
   - Source: OpenCity Bengaluru or BBMP Disaster Management cell records.
   - Format: Polygon shapefiles or GeoJSON boundaries.
3. **OpenStreetMap Roads:**
   - Source: Geofabrik India extract ([download.geofabrik.de/asia/india.html](https://download.geofabrik.de/asia/india.html)) or automated download via `osmnx` for "Bengaluru, Karnataka, India".
4. **Stormwater Drainage Network (Rajakaluves):**
   - Source: OpenCity Bengaluru SWD layers or BBMP GIS portal.
   - Format: Polyline Shapefile / GeoJSON / KML.
5. **ATREE Lakes and Streams (Keres):**
   - Source: ATREE Bangalore Lakes Project / OpenCity water bodies layer.
   - Format: Polygon Shapefile or GeoJSON.
6. **Copernicus DEM GLO-30 (30m Elevation):**
   - Source: Copernicus Open Access Hub or OpenTopography ([opentopography.org](https://opentopography.org)).
   - Extent: Bounding box covering approx 77.40°E to 77.85°E and 12.75°N to 13.20°N.
   - Format: 32-bit float GeoTIFF (`.tif`).

---

## 3. How to Place Downloaded Files

1. **Shapefiles (`.shp`):**
   - A shapefile consists of multiple companion files (`.shp`, `.shx`, `.dbf`, `.prj`). Place **all** companion files together in the target subdirectory.
2. **KMZ Files (`.kmz`):**
   - Place the `.kmz` file directly into the target subdirectory; the inspection script will automatically unpack and validate the internal KML.
3. **GeoTIFF Files (`.tif`):**
   - Place the uncompressed `.tif` file directly into `data/raw/elevation/`.
4. **Never modify or rename internal attributes manually:**
   - Keep the original files unaltered to ensure raw data provenance.

---

## 4. Validating Uploaded Datasets

Immediately after dropping files into `data/raw/`, run:
```bash
python scripts/inspect_datasets.py
```
This utility will:
- Detect all newly added files.
- Report feature counts, geometry types, and coordinate reference systems.
- Validate that the dataset falls within Bengaluru's geographical envelope.
- Flag any null or topologically invalid geometries.
- Automatically update `data/metadata/data_inventory.csv`.
