"""
Spatial and geometric utility functions for FloodLens.
"""

from typing import Tuple
import math

from backend.app.core.config import settings


def is_coordinate_within_bengaluru(lon: float, lat: float) -> bool:
    """
    Check if a given (lon, lat) coordinate falls within the approximate
    sanity envelope for Bengaluru.
    """
    min_lon, min_lat, max_lon, max_lat = settings.BENGALURU_SANITY_BBOX
    return (min_lon <= lon <= max_lon) and (min_lat <= lat <= max_lat)


def haversine_distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """
    Compute great-circle distance between two (lon, lat) points in meters.
    coord1: (lon1, lat1) in degrees
    coord2: (lon2, lat2) in degrees
    """
    lon1, lat1 = coord1
    lon2, lat2 = coord2

    # Earth radius in meters
    r = 6371000.0

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r * c


def transform_bbox_to_geojson_polygon(bbox: Tuple[float, float, float, float]) -> dict:
    """
    Convert a bounding box (minx, miny, maxx, maxy) into a GeoJSON Polygon dictionary.
    """
    minx, miny, maxx, maxy = bbox
    return {
        "type": "Polygon",
        "coordinates": [
            [
                [minx, miny],
                [maxx, miny],
                [maxx, maxy],
                [minx, maxy],
                [minx, miny],
            ]
        ],
    }
