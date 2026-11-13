"""
Tests for spatial analysis utilities, coordinate boundary checks, and distances.
"""

import sys
from pathlib import Path

# Add project root
BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app.utils.geo_utils import (
    is_coordinate_within_bengaluru,
    haversine_distance,
    transform_bbox_to_geojson_polygon,
)


def test_is_coordinate_within_bengaluru():
    """Verify coordinate containment logic for Bengaluru landmarks."""
    # Vidhana Soudha, Bengaluru: 77.5908° E, 12.9797° N
    assert is_coordinate_within_bengaluru(77.5908, 12.9797) is True

    # Electronic City, Bengaluru: 77.6784° E, 12.8452° N
    assert is_coordinate_within_bengaluru(77.6784, 12.8452) is True

    # Whitefield, Bengaluru: 77.7499° E, 12.9698° N
    assert is_coordinate_within_bengaluru(77.7499, 12.9698) is True

    # Gateway of India, Mumbai: 72.8347° E, 18.9220° N (outside)
    assert is_coordinate_within_bengaluru(72.8347, 18.9220) is False

    # Marina Beach, Chennai: 80.2824° E, 13.0500° N (outside)
    assert is_coordinate_within_bengaluru(80.2824, 13.0500) is False


def test_haversine_distance():
    """Verify haversine distance calculation."""
    # Distance from point to itself is 0
    p1 = (77.5908, 12.9797)
    assert haversine_distance(p1, p1) == 0.0

    # Distance between Majestic (77.5713, 12.9767) and Indiranagar 100ft Rd (77.6412, 12.9719)
    # Expected distance: ~7.6 km (within 7000 - 8500 meters)
    p_majestic = (77.5713, 12.9767)
    p_indiranagar = (77.6412, 12.9719)
    dist = haversine_distance(p_majestic, p_indiranagar)
    assert 7000.0 < dist < 8500.0


def test_transform_bbox_to_geojson_polygon():
    """Verify bounding box to GeoJSON Polygon conversion."""
    bbox = (77.50, 12.90, 77.70, 13.10)
    poly = transform_bbox_to_geojson_polygon(bbox)

    assert poly["type"] == "Polygon"
    assert len(poly["coordinates"]) == 1
    ring = poly["coordinates"][0]
    assert len(ring) == 5  # 4 corners + closed point
    assert ring[0] == ring[-1]  # Closed polygon ring
    assert ring[0] == [77.50, 12.90]
    assert ring[2] == [77.70, 13.10]
