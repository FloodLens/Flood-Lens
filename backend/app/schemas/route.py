"""
Pydantic schemas for route requests, comparisons, and risk exposures.
"""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class LatLng(BaseModel):
    """Geographic coordinate pair."""
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude in EPSG:4326")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude in EPSG:4326")


class RouteRequest(BaseModel):
    """Request payload for routing queries."""
    origin: LatLng
    destination: LatLng
    profile: Literal["shortest", "risk_aware", "compare"] = Field(
        "compare",
        description="Calculate shortest route, risk-aware route, or compare both",
    )


class RouteResult(BaseModel):
    """Single evaluated route with metrics and geometry."""
    route_type: Literal["shortest", "risk_aware"]
    distance_meters: float = Field(..., description="Total route length in meters")
    exposure_score: float = Field(..., description="Aggregated flood vulnerability / exposure score")
    exposure_tier: Literal["Low", "Medium", "High"] = Field(..., description="Qualitative exposure category")
    coordinates: List[List[float]] = Field(
        default_factory=list,
        description="LineString coordinates as [[lon, lat], ...]",
    )
    explanation: Optional[str] = Field(None, description="Human-readable summary of route risk tradeoffs")


class RouteComparisonResponse(BaseModel):
    """Comparative response containing both shortest and risk-aware routes."""
    origin: LatLng
    destination: LatLng
    status: str = Field(
        "pending_road_network",
        description="Operational status of the routing service (e.g., 'completed', 'pending_road_network')",
    )
    message: Optional[str] = Field(
        None,
        description="Informational note explaining routing engine availability or data requirements",
    )
    shortest_route: Optional[RouteResult] = None
    risk_aware_route: Optional[RouteResult] = None
    delta_distance_meters: Optional[float] = Field(
        None, description="Additional distance needed to lower exposure (meters)"
    )
    delta_exposure_percentage: Optional[float] = Field(
        None, description="Percentage reduction in flood exposure score"
    )
