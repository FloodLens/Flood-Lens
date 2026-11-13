"""
API Routers Package for FloodLens.
"""

from .health import router as health_router
from .floods import router as floods_router
from .routes import router as routes_router

__all__ = ["health_router", "floods_router", "routes_router"]
