"""
FloodLens — Dataset Inspection Utility.

Scans the data/raw/ directories for geographic datasets (Shapefiles, GeoJSON,
KML, KMZ, GeoPackage, GeoTIFF), records metadata, validates geometries,
checks coverage against the Bengaluru study area, and updates
data/metadata/data_inventory.csv without modifying any raw files.

Usage:
    python scripts/inspect_datasets.py
    python scripts/inspect_datasets.py --category flood_locations
    python scripts/inspect_datasets.py --file data/raw/roads/roads.geojson
"""

import argparse
import csv
import json
import os
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add repository root to path for imports
BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app.core.config import settings

# Attempt optional GIS imports with friendly fallback flags
HAS_GEOPANDAS = False
HAS_PYOGRIO = False
HAS_SHAPELY = False
HAS_RASTERIO = False
HAS_PYPROJ = False

try:
    import geopandas as gpd
    HAS_GEOPANDAS = True
except ImportError:
    gpd = None

try:
    import pyogrio
    HAS_PYOGRIO = True
except ImportError:
    pyogrio = None

try:
    import shapely
    from shapely.geometry import shape
    HAS_SHAPELY = True
except ImportError:
    shapely = None
    shape = None

try:
    import rasterio
    from rasterio.warp import transform_bounds
    HAS_RASTERIO = True
except ImportError:
    rasterio = None

try:
    import pyproj
    HAS_PYPROJ = True
except ImportError:
    pyproj = None


SUPPORTED_EXTENSIONS = {
    ".geojson": "GeoJSON",
    ".json": "GeoJSON/JSON",
    ".shp": "Shapefile",
    ".gpkg": "GeoPackage",
    ".kml": "KML",
    ".kmz": "KMZ",
    ".tif": "GeoTIFF",
    ".tiff": "GeoTIFF",
}


def check_bbox_overlap(
    bounds: Tuple[float, float, float, float],
    study_bbox: Tuple[float, float, float, float]
) -> bool:
    """
    Check if bounding box (minx, miny, maxx, maxy) overlaps with study area envelope.
    """
    b_minx, b_miny, b_maxx, b_maxy = bounds
    s_minx, s_miny, s_maxx, s_maxy = study_bbox

    # Non-overlapping if one is strictly to the left, right, top, or bottom
    if b_maxx < s_minx or b_minx > s_maxx or b_maxy < s_miny or b_miny > s_maxy:
        return False
    return True


def inspect_vector_geopandas(file_path: Path, category: str) -> Dict[str, Any]:
    """Inspect vector dataset using GeoPandas."""
    size_kb = round(file_path.stat().st_size / 1024, 2)
    ext = file_path.suffix.lower()
    file_format = SUPPORTED_EXTENSIONS.get(ext, ext.upper().replace(".", ""))

    target_path = file_path
    temp_dir_obj = None

    # Handle KMZ archives by extracting internal KML
    if ext == ".kmz":
        try:
            temp_dir_obj = tempfile.TemporaryDirectory()
            with zipfile.ZipFile(file_path, "r") as z:
                kml_files = [f for f in z.namelist() if f.lower().endswith(".kml")]
                if not kml_files:
                    return {
                        "file_name": file_path.name,
                        "category": category,
                        "file_format": file_format,
                        "file_size_kb": size_kb,
                        "crs": "Unknown",
                        "geometry_type": "Unknown",
                        "feature_count": 0,
                        "bounds_minx": "",
                        "bounds_miny": "",
                        "bounds_maxx": "",
                        "bounds_maxy": "",
                        "invalid_geometry_count": 0,
                        "null_geometry_count": 0,
                        "covers_study_area": False,
                        "inspection_status": "ERROR",
                        "inspection_notes": "KMZ archive contains no .kml files",
                    }
                extracted_path = z.extract(kml_files[0], temp_dir_obj.name)
                target_path = Path(extracted_path)
        except Exception as e:
            return {
                "file_name": file_path.name,
                "category": category,
                "file_format": file_format,
                "file_size_kb": size_kb,
                "crs": "Unknown",
                "geometry_type": "Unknown",
                "feature_count": 0,
                "bounds_minx": "",
                "bounds_miny": "",
                "bounds_maxx": "",
                "bounds_maxy": "",
                "invalid_geometry_count": 0,
                "null_geometry_count": 0,
                "covers_study_area": False,
                "inspection_status": "ERROR",
                "inspection_notes": f"Failed to extract KMZ: {str(e)}",
            }

    try:
        gdf = gpd.read_file(target_path)
    except Exception as e:
        return {
            "file_name": file_path.name,
            "category": category,
            "file_format": file_format,
            "file_size_kb": size_kb,
            "crs": "Unknown",
            "geometry_type": "Unknown",
            "feature_count": 0,
            "bounds_minx": "",
            "bounds_miny": "",
            "bounds_maxx": "",
            "bounds_maxy": "",
            "invalid_geometry_count": 0,
            "null_geometry_count": 0,
            "covers_study_area": False,
            "inspection_status": "ERROR",
            "inspection_notes": f"Error reading file with GeoPandas: {str(e)}",
        }
    finally:
        if temp_dir_obj is not None:
            temp_dir_obj.cleanup()

    feature_count = len(gdf)
    crs_str = str(gdf.crs) if gdf.crs else "Unspecified"

    # Geometry types
    geom_types = list(gdf.geometry.geom_type.dropna().unique())
    geom_type_str = ", ".join(geom_types) if geom_types else "None"

    # Count null / empty geometries
    null_count = int(gdf.geometry.isna().sum() + gdf.geometry.is_empty.sum())

    # Count invalid geometries
    valid_mask = gdf.geometry.is_valid
    invalid_count = int((~valid_mask).sum())

    # Bounds
    if not gdf.empty and not gdf.geometry.dropna().empty:
        total_bounds = gdf.total_bounds  # [minx, miny, maxx, maxy]
        minx, miny, maxx, maxy = (
            round(total_bounds[0], 6),
            round(total_bounds[1], 6),
            round(total_bounds[2], 6),
            round(total_bounds[3], 6),
        )

        # Re-project bounds to EPSG:4326 for study area check if in projected CRS
        bounds_4326 = (minx, miny, maxx, maxy)
        if gdf.crs and gdf.crs.to_epsg() != 4326:
            try:
                gdf_4326 = gdf.to_crs(epsg=4326)
                tb = gdf_4326.total_bounds
                bounds_4326 = (tb[0], tb[1], tb[2], tb[3])
            except Exception:
                bounds_4326 = (minx, miny, maxx, maxy)

        covers_area = check_bbox_overlap(bounds_4326, settings.BENGALURU_SANITY_BBOX)
    else:
        minx, miny, maxx, maxy = "", "", "", ""
        covers_area = False

    status = "OK"
    notes = []
    if feature_count == 0:
        status = "EMPTY"
        notes.append("Dataset contains 0 features")
    if crs_str == "Unspecified":
        status = "WARNING"
        notes.append("CRS missing/unspecified")
    if invalid_count > 0:
        status = "WARNING"
        notes.append(f"{invalid_count} invalid geometries detected")
    if null_count > 0:
        status = "WARNING"
        notes.append(f"{null_count} null or empty geometries detected")
    if not covers_area and feature_count > 0:
        status = "WARNING"
        notes.append("Bounding box outside Bengaluru sanity bounds")

    return {
        "file_name": file_path.name,
        "category": category,
        "file_format": file_format,
        "file_size_kb": size_kb,
        "crs": crs_str,
        "geometry_type": geom_type_str,
        "feature_count": feature_count,
        "bounds_minx": minx,
        "bounds_miny": miny,
        "bounds_maxx": maxx,
        "bounds_maxy": maxy,
        "invalid_geometry_count": invalid_count,
        "null_geometry_count": null_count,
        "covers_study_area": covers_area,
        "inspection_status": status,
        "inspection_notes": "; ".join(notes) if notes else "Inspection passed",
    }


def inspect_raster_rasterio(file_path: Path, category: str) -> Dict[str, Any]:
    """Inspect raster (GeoTIFF) using Rasterio."""
    size_kb = round(file_path.stat().st_size / 1024, 2)
    ext = file_path.suffix.lower()
    file_format = SUPPORTED_EXTENSIONS.get(ext, "GeoTIFF")

    try:
        with rasterio.open(file_path) as src:
            crs_str = str(src.crs) if src.crs else "Unspecified"
            bounds = src.bounds
            minx = round(bounds.left, 6)
            miny = round(bounds.bottom, 6)
            maxx = round(bounds.right, 6)
            maxy = round(bounds.top, 6)

            # Check study area coverage
            bounds_4326 = (minx, miny, maxx, maxy)
            if src.crs and src.crs.to_epsg() != 4326:
                try:
                    tb = transform_bounds(src.crs, "EPSG:4326", bounds.left, bounds.bottom, bounds.right, bounds.top)
                    bounds_4326 = (tb[0], tb[1], tb[2], tb[3])
                except Exception:
                    bounds_4326 = (minx, miny, maxx, maxy)

            covers_area = check_bbox_overlap(bounds_4326, settings.BENGALURU_SANITY_BBOX)
            feature_desc = f"Grid {src.width}x{src.height}, Bands: {src.count}"

            status = "OK"
            notes = []
            if crs_str == "Unspecified":
                status = "WARNING"
                notes.append("CRS missing/unspecified")
            if not covers_area:
                status = "WARNING"
                notes.append("Raster bounds do not overlap Bengaluru sanity envelope")

            return {
                "file_name": file_path.name,
                "category": category,
                "file_format": file_format,
                "file_size_kb": size_kb,
                "crs": crs_str,
                "geometry_type": f"Raster ({feature_desc})",
                "feature_count": src.width * src.height,
                "bounds_minx": minx,
                "bounds_miny": miny,
                "bounds_maxx": maxx,
                "bounds_maxy": maxy,
                "invalid_geometry_count": 0,
                "null_geometry_count": 0,
                "covers_study_area": covers_area,
                "inspection_status": status,
                "inspection_notes": "; ".join(notes) if notes else "Inspection passed",
            }
    except Exception as e:
        return {
            "file_name": file_path.name,
            "category": category,
            "file_format": file_format,
            "file_size_kb": size_kb,
            "crs": "Unknown",
            "geometry_type": "Raster",
            "feature_count": 0,
            "bounds_minx": "",
            "bounds_miny": "",
            "bounds_maxx": "",
            "bounds_maxy": "",
            "invalid_geometry_count": 0,
            "null_geometry_count": 0,
            "covers_study_area": False,
            "inspection_status": "ERROR",
            "inspection_notes": f"Error inspecting GeoTIFF: {str(e)}",
        }


def inspect_vector_fallback(file_path: Path, category: str) -> Dict[str, Any]:
    """Fallback inspector when GeoPandas is not installed (supports GeoJSON via standard library)."""
    size_kb = round(file_path.stat().st_size / 1024, 2)
    ext = file_path.suffix.lower()
    file_format = SUPPORTED_EXTENSIONS.get(ext, ext.upper().replace(".", ""))

    if ext in [".geojson", ".json"]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            features = data.get("features", [])
            feature_count = len(features)
            geom_types = set()
            null_count = 0
            all_coords = []

            for feat in features:
                geom = feat.get("geometry")
                if not geom or not geom.get("coordinates"):
                    null_count += 1
                else:
                    gtype = geom.get("type", "Unknown")
                    geom_types.add(gtype)
                    # Extract raw coordinates for approximate bounds if Point/Polygon
                    coords = geom.get("coordinates")
                    # Flatten coordinates helper
                    def extract_pts(c: Any) -> List[Tuple[float, float]]:
                        pts = []
                        if isinstance(c, (list, tuple)):
                            if len(c) >= 2 and isinstance(c[0], (int, float)) and isinstance(c[1], (int, float)):
                                pts.append((float(c[0]), float(c[1])))
                            else:
                                for item in c:
                                    pts.extend(extract_pts(item))
                        return pts

                    all_coords.extend(extract_pts(coords))

            geom_type_str = ", ".join(geom_types) if geom_types else "None"

            if all_coords:
                xs = [pt[0] for pt in all_coords]
                ys = [pt[1] for pt in all_coords]
                minx, miny, maxx, maxy = round(min(xs), 6), round(min(ys), 6), round(max(xs), 6), round(max(ys), 6)
                covers_area = check_bbox_overlap((minx, miny, maxx, maxy), settings.BENGALURU_SANITY_BBOX)
            else:
                minx, miny, maxx, maxy = "", "", "", ""
                covers_area = False

            crs_info = data.get("crs", {}).get("properties", {}).get("name", "EPSG:4326 (Default GeoJSON)")

            return {
                "file_name": file_path.name,
                "category": category,
                "file_format": file_format,
                "file_size_kb": size_kb,
                "crs": crs_info,
                "geometry_type": geom_type_str,
                "feature_count": feature_count,
                "bounds_minx": minx,
                "bounds_miny": miny,
                "bounds_maxx": maxx,
                "bounds_maxy": maxy,
                "invalid_geometry_count": 0,
                "null_geometry_count": null_count,
                "covers_study_area": covers_area,
                "inspection_status": "OK (Fallback Parser)",
                "inspection_notes": "Inspected using standard JSON. Install geopandas for advanced geometric validation.",
            }
        except Exception as e:
            return {
                "file_name": file_path.name,
                "category": category,
                "file_format": file_format,
                "file_size_kb": size_kb,
                "crs": "Unknown",
                "geometry_type": "Unknown",
                "feature_count": 0,
                "bounds_minx": "",
                "bounds_miny": "",
                "bounds_maxx": "",
                "bounds_maxy": "",
                "invalid_geometry_count": 0,
                "null_geometry_count": 0,
                "covers_study_area": False,
                "inspection_status": "ERROR",
                "inspection_notes": f"Fallback parser error: {str(e)}",
            }

    # For binary formats (.shp, .gpkg, .tif, .kmz) when GIS libraries aren't yet installed
    return {
        "file_name": file_path.name,
        "category": category,
        "file_format": file_format,
        "file_size_kb": size_kb,
        "crs": "Requires geopandas/rasterio",
        "geometry_type": "Requires geopandas/rasterio",
        "feature_count": 0,
        "bounds_minx": "",
        "bounds_miny": "",
        "bounds_maxx": "",
        "bounds_maxy": "",
        "invalid_geometry_count": 0,
        "null_geometry_count": 0,
        "covers_study_area": False,
        "inspection_status": "PENDING_DEPENDENCY",
        "inspection_notes": f"Please install geopandas/rasterio to inspect {file_format} files (run: pip install -r requirements.txt)",
    }


def inspect_file(file_path: Path, category: str) -> Optional[Dict[str, Any]]:
    """Route file to appropriate inspector based on extension and available libraries."""
    ext = file_path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return None

    if ext in [".tif", ".tiff"]:
        if HAS_RASTERIO:
            return inspect_raster_rasterio(file_path, category)
        else:
            return inspect_vector_fallback(file_path, category)

    if HAS_GEOPANDAS:
        return inspect_vector_geopandas(file_path, category)
    else:
        return inspect_vector_fallback(file_path, category)


def scan_datasets(target_category: Optional[str] = None, target_file: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Scan raw dataset directories and return inspection records."""
    records = []
    settings.ensure_data_dirs()

    if target_file:
        if not target_file.exists():
            print(f"Error: Specified file does not exist: {target_file}")
            return []
        category = target_file.parent.name
        record = inspect_file(target_file, category)
        if record:
            records.append(record)
        return records

    categories_to_scan = [target_category] if target_category else list(settings.RAW_DATASETS.keys())

    for cat in categories_to_scan:
        cat_dir = settings.get_raw_dir(cat)
        if not cat_dir.exists():
            continue

        found_files = False
        for root, _, files in os.walk(cat_dir):
            for file in files:
                if file.startswith(".") or file == ".gitkeep":
                    continue
                file_path = Path(root) / file
                ext = file_path.suffix.lower()
                if ext in SUPPORTED_EXTENSIONS:
                    found_files = True
                    rec = inspect_file(file_path, cat)
                    if rec:
                        records.append(rec)

    return records


def write_inventory_csv(records: List[Dict[str, Any]]) -> None:
    """Save inspection records to data/metadata/data_inventory.csv preserving schema."""
    fieldnames = [
        "file_name",
        "category",
        "file_format",
        "file_size_kb",
        "crs",
        "geometry_type",
        "feature_count",
        "bounds_minx",
        "bounds_miny",
        "bounds_maxx",
        "bounds_maxy",
        "invalid_geometry_count",
        "null_geometry_count",
        "covers_study_area",
        "inspection_status",
        "inspection_notes",
    ]

    settings.METADATA_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = settings.DATA_INVENTORY_CSV

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            writer.writerow(r)


def print_summary_table(records: List[Dict[str, Any]]) -> None:
    """Print readable inspection report table to console."""
    print("\n" + "=" * 90)
    print(f"FLOODLENS DATASET INSPECTION REPORT — Study Area: {settings.STUDY_AREA_NAME}")
    print("=" * 90)

    if not records:
        print("\n[!] No spatial data files found in data/raw/ directories yet.")
        print("    Place your downloaded Shapefiles, GeoJSON, KML, KMZ, or GeoTIFF files inside:")
        for cat, path in settings.RAW_DATASETS.items():
            print(f"      - data/raw/{cat}/")
        print("\n    Then run: python scripts/inspect_datasets.py\n")
        print("=" * 90)
        return

    print(f"\nFound {len(records)} dataset(s):\n")
    header = f"{'File Name':<28} | {'Category':<16} | {'Format':<10} | {'Count':<7} | {'CRS':<14} | {'Status'}"
    print(header)
    print("-" * 90)

    for r in records:
        f_name = (r["file_name"][:25] + "...") if len(r["file_name"]) > 28 else r["file_name"]
        cat = r["category"][:15]
        fmt = r["file_format"][:9]
        cnt = str(r["feature_count"])[:6]
        crs = str(r["crs"])[:13]
        status = r["inspection_status"]
        print(f"{f_name:<28} | {cat:<16} | {fmt:<10} | {cnt:<7} | {crs:<14} | {status}")
        if r["inspection_notes"] and r["inspection_notes"] != "Inspection passed":
            print(f"   ↳ Notes: {r['inspection_notes']}")

    print("\n" + "-" * 90)
    print(f"Detailed inventory saved to: {settings.DATA_INVENTORY_CSV}")
    print("=" * 90 + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="FloodLens Dataset Inspection Utility")
    parser.add_argument("--category", type=str, help="Specific category in data/raw to inspect")
    parser.add_argument("--file", type=Path, help="Specific file path to inspect")
    args = parser.parse_args()

    records = scan_datasets(target_category=args.category, target_file=args.file)
    write_inventory_csv(records)
    print_summary_table(records)


if __name__ == "__main__":
    main()
