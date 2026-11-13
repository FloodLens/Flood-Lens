"""
FloodLens FastAPI Application Entrypoint.

Bengaluru-focused GeoAI Platform for Urban Flood Vulnerability Assessment
and Risk-Aware Route Comparison.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.api.routers import health_router, floods_router, routes_router
from backend.app.utils.logging import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle context manager: initializes data directories on application startup
    and logs service operational parameters.
    """
    settings.ensure_data_dirs()
    logger.info(f"FloodLens API started for {settings.STUDY_AREA_NAME}")
    logger.info(f"Interchange CRS: {settings.CRS_INTERCHANGE} | Projected CRS: {settings.CRS_PROJECTED}")
    yield
    logger.info("FloodLens API shutting down.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure Cross-Origin Resource Sharing (CORS) for React + Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 Routers
app.include_router(health_router, prefix=settings.API_V1_PREFIX)
app.include_router(floods_router, prefix=settings.API_V1_PREFIX)
app.include_router(routes_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["Root"])
def root():
    """Welcome endpoint with API sitemap and documentation links."""
    return {
        "project": settings.PROJECT_NAME,
        "description": settings.PROJECT_DESCRIPTION,
        "version": settings.VERSION,
        "study_area": settings.STUDY_AREA_NAME,
        "documentation": "/docs",
        "api_v1": settings.API_V1_PREFIX,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
    )
