"""
FloodLens — Routing Service (Person B Ownership).

Responsibilities:
- Shortest-distance route computation using base NetworkX graph (from Person A).
- Risk-aware route computation applying edge impedance based on vulnerability scores.
- Route comparison, delta distance, and delta exposure calculation.
"""

from typing import Dict, Any, Optional
from backend.app.schemas.route import LatLng, RouteComparisonResponse, RouteResult
from backend.app.utils.logging import logger


class RoutingService:
    """
    Computes and compares shortest vs risk-aware routes.
    Owned by Person B.
    """

    def compare_routes(
        self, origin: LatLng, destination: LatLng
    ) -> RouteComparisonResponse:
        """
        Compare shortest-distance route with risk-aware route.
        Returns an informative pending response when the road network graph is not yet available.
        """
        logger.info(
            f"[Person B] Route comparison requested from ({origin.latitude}, {origin.longitude}) "
            f"to ({destination.latitude}, {destination.longitude})"
        )

        return RouteComparisonResponse(
            origin=origin,
            destination=destination,
            status="pending_road_network",
            message=(
                "Routing engine is currently offline awaiting road network graph "
                "construction (OSMnx/NetworkX) from data/raw/roads/ in Phase 1."
            ),
            shortest_route=None,
            risk_aware_route=None,
            delta_distance_meters=None,
            delta_exposure_percentage=None,
        )


routing_service = RoutingService()
