"""
Endpoints for flood incident data, low-lying zones, and DBSCAN clusters.
"""

from typing import Any, Dict, List
from fastapi import APIRouter
from backend.app.schemas.flood import FloodClusterSchema, FloodLayerResponse
from backend.app.services.flood_service import flood_service

router = APIRouter(prefix="/floods", tags=["Floods"])


@router.get("/points", response_model=FloodLayerResponse)
def get_flood_points():
    """
    Retrieve historical flood incident locations as a GeoJSON FeatureCollection.
    """
    geojson_data = flood_service.get_historical_flood_points()
    return FloodLayerResponse(
        layer_name="bbmp_historical_flood_points",
        feature_count=len(geojson_data.get("features", [])),
        geojson=geojson_data,
    )


@router.get("/clusters", response_model=List[FloodClusterSchema])
def get_flood_clusters(eps_meters: float = 300.0, min_samples: int = 3):
    """
    Retrieve DBSCAN spatial clusters computed from historical flood data.
    """
    clusters = flood_service.run_dbscan_clustering(eps_meters=eps_meters, min_samples=min_samples)
    return clusters
