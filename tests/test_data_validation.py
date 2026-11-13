"""
Tests for dataset validation, metadata structures, and bounding box checks.
"""

import csv
import sys
from pathlib import Path

# Add project root
BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app.core.config import settings
from scripts.inspect_datasets import check_bbox_overlap


def test_study_area_configuration():
    """Verify that Bengaluru study area and CRS settings are correctly initialized."""
    assert "Bengaluru" in settings.STUDY_AREA_NAME
    assert settings.CRS_INTERCHANGE == "EPSG:4326"
    assert settings.CRS_PROJECTED == "EPSG:32643"
    assert len(settings.BENGALURU_SANITY_BBOX) == 4
    min_lon, min_lat, max_lon, max_lat = settings.BENGALURU_SANITY_BBOX
    assert min_lon < max_lon
    assert min_lat < max_lat


def test_bbox_overlap_detection():
    """Verify that check_bbox_overlap correctly flags inside and outside bounds."""
    # A box centered inside Bengaluru (e.g. Majestic / MG Road area: ~77.59, 12.97)
    inside_bbox = (77.58, 12.96, 77.60, 12.98)
    assert check_bbox_overlap(inside_bbox, settings.BENGALURU_SANITY_BBOX) is True

    # A box completely outside Bengaluru (e.g., Delhi: 77.10, 28.60)
    delhi_bbox = (77.05, 28.55, 77.25, 28.70)
    assert check_bbox_overlap(delhi_bbox, settings.BENGALURU_SANITY_BBOX) is False

    # A box in London (-0.12, 51.50)
    london_bbox = (-0.20, 51.40, -0.05, 51.60)
    assert check_bbox_overlap(london_bbox, settings.BENGALURU_SANITY_BBOX) is False


def test_data_sources_csv_integrity():
    """Verify that data_sources.csv exists, is readable, and contains expected datasets."""
    csv_path = settings.DATA_SOURCES_CSV
    assert csv_path.exists(), f"Missing metadata file: {csv_path}"

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    assert len(reader) >= 7, "data_sources.csv should list all primary datasets"
    dataset_ids = [row["dataset_id"] for row in reader]
    assert "bbmp_hist_floods" in dataset_ids
    assert "osm_roads" in dataset_ids
    assert "copernicus_dem" in dataset_ids
    assert "bbmp_drainage" in dataset_ids


def test_data_directories_structure():
    """Verify that all raw category directories exist or are created."""
    settings.ensure_data_dirs()
    for cat, path in settings.RAW_DATASETS.items():
        assert path.exists(), f"Directory for {cat} must exist: {path}"
