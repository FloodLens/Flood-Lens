"""
Health check and system diagnostics endpoint.
"""

from typing import Dict, Any
from fastapi import APIRouter
from backend.app.core.config import settings

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=Dict[str, Any])
def check_health():
    """
    Returns API operational status, study area configuration, and CRS definitions.
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "study_area": settings.STUDY_AREA_NAME,
        "crs": {
            "web_interchange": settings.CRS_INTERCHANGE,
            "projected_metric": settings.CRS_PROJECTED,
        },
        "boundary_configured": settings.VERIFIED_BOUNDARY_FILE is not None,
    }
