"""
Endpoints for route evaluation, risk-aware routing, and route comparisons.
"""

from fastapi import APIRouter
from backend.app.schemas.route import RouteRequest, RouteComparisonResponse
from backend.app.services.routing_service import routing_service

router = APIRouter(prefix="/routes", tags=["Routes"])


@router.post("/compare", response_model=RouteComparisonResponse)
def compare_routes(request: RouteRequest):
    """
    Compare shortest-distance route against a risk-aware route.
    """
    return routing_service.compare_routes(request.origin, request.destination)
