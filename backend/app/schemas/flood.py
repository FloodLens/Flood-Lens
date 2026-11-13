"""
Pydantic schemas for flood locations, hotspots, and DBSCAN clusters.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class FloodPointSchema(BaseModel):
    """Schema representing an individual flood observation or prone point."""
    id: Optional[str] = Field(None, description="Unique identifier for the flood location")
    name: Optional[str] = Field(None, description="Location name or landmark")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude in EPSG:4326")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude in EPSG:4326")
    source: Optional[str] = Field(None, description="Source agency (e.g., BBMP, KSDMA)")
    year: Optional[int] = Field(None, description="Recorded year of inundation incident")
    cluster_id: Optional[int] = Field(None, description="DBSCAN cluster identifier (-1 indicates noise)")


class FloodClusterSchema(BaseModel):
    """Schema representing a spatial cluster of flood points derived from DBSCAN."""
    cluster_id: int = Field(..., description="DBSCAN assigned cluster index")
    center_latitude: float = Field(..., description="Cluster centroid latitude")
    center_longitude: float = Field(..., description="Cluster centroid longitude")
    point_count: int = Field(..., description="Number of historical incidents in this cluster")
    radius_meters: float = Field(..., description="Estimated spatial spread in meters")


class FloodLayerResponse(BaseModel):
    """API response containing GeoJSON spatial collection of flood features."""
    layer_name: str
    feature_count: int
    crs: str = "EPSG:4326"
    geojson: Dict[str, Any] = Field(default_factory=lambda: {"type": "FeatureCollection", "features": []})
