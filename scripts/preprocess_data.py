"""
FloodLens — Data Preprocessing Scaffolding.

Performs standard preprocessing on raw spatial datasets:
- Standardises CRS to EPSG:4326 (web display) and EPSG:32643 (metric analysis)
- Standardises attribute field naming conventions
- Removes null / empty geometries
- Clips datasets to the verified study area boundary (when available)
- Saves standardized artifacts into data/processed/

Usage:
    python scripts/preprocess_data.py --category flood_locations
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app.core.config import settings


def preprocess_category(category: str):
    """
    Scaffold for preprocessing raw layers within a category.
    Actual business logic will be customized once raw data files are uploaded.
    """
    try:
        import geopandas as gpd
    except ImportError:
        print("[!] GeoPandas not installed. Please run: pip install -r requirements.txt")
        return

    raw_dir = settings.get_raw_dir(category)
    processed_dir = settings.PROCESSED_DATA_DIR / category
    processed_dir.mkdir(parents=True, exist_ok=True)

    print(f"[*] Preprocessing raw category: '{category}' from {raw_dir}")
    print(f"    - Target output directory: {processed_dir}")
    print("    - Ready for data ingestion once raw files are placed.")


def main():
    parser = argparse.ArgumentParser(description="FloodLens Data Preprocessing Pipeline")
    parser.add_argument("--category", type=str, default="all", help="Dataset category to preprocess or 'all'")
    args = parser.parse_args()

    categories = list(settings.RAW_DATASETS.keys()) if args.category == "all" else [args.category]
    for cat in categories:
        preprocess_category(cat)


if __name__ == "__main__":
    main()
