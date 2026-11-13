"""
FloodLens — Geometry Validation and Repair Utility.

Checks vector layers for topological and geometric errors:
- Unclosed rings, self-intersections, slivers
- Null or empty geometries
- Disjoint parts in Multi-geometries
Offers automated repair using Shapely's `make_valid` without altering original raw files.

Usage:
    python scripts/validate_geometries.py --input data/raw/flood_locations/points.geojson
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app.core.config import settings


def validate_geometries(input_path: Path, repair: bool = False, output_path: Path = None):
    """
    Validate geometries in a vector dataset.
    """
    try:
        import geopandas as gpd
        from shapely.validation import explain_validity, make_valid
    except ImportError:
        print("[!] GeoPandas / Shapely not found. Please run: pip install -r requirements.txt")
        return

    if not input_path.exists():
        print(f"[!] Input file does not exist: {input_path}")
        return

    print(f"[*] Validating geometries for: {input_path}")
    gdf = gpd.read_file(input_path)

    total_count = len(gdf)
    null_count = gdf.geometry.isna().sum() + gdf.geometry.is_empty.sum()
    invalid_mask = ~gdf.geometry.is_valid
    invalid_count = invalid_mask.sum()

    print(f"    - Total features: {total_count}")
    print(f"    - Null / Empty geometries: {null_count}")
    print(f"    - Invalid geometries: {invalid_count}")

    if invalid_count > 0:
        print("\n[*] Sample invalid geometry reasons:")
        for idx in gdf[invalid_mask].index[:5]:
            reason = explain_validity(gdf.loc[idx, "geometry"])
            print(f"    - Feature ID {idx}: {reason}")

    if repair and invalid_count > 0:
        print("[*] Applying shapely.make_valid() to repair invalid geometries...")
        gdf["geometry"] = gdf["geometry"].apply(lambda g: make_valid(g) if g is not None else None)
        still_invalid = (~gdf.geometry.is_valid).sum()
        print(f"    - Post-repair invalid count: {still_invalid}")

        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            gdf.to_file(output_path, driver="GeoJSON")
            print(f"[+] Repaired geometries written to: {output_path}")
        else:
            print("[!] No output path provided; repaired data was not written to disk.")
    elif invalid_count == 0:
        print("[+] All geometries are topologically valid!")


def main():
    parser = argparse.ArgumentParser(description="Validate and repair spatial geometries")
    parser.add_argument("--input", type=Path, required=True, help="Input vector file path")
    parser.add_argument("--repair", action="store_true", help="Attempt automated repair via make_valid")
    parser.add_argument("--output", type=Path, help="Output destination for repaired dataset")
    args = parser.parse_args()

    validate_geometries(args.input, repair=args.repair, output_path=args.output)


if __name__ == "__main__":
    main()
