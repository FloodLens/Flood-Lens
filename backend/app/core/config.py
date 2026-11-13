"""
Central Configuration for FloodLens.

Defines spatial constants, coordinate reference systems (CRS),
data directory paths, study area bounding references, and server parameters.
Designed for clean collaboration between Person A and Person B.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:
    # Graceful fallback if pydantic-settings is not yet installed in active environment
    from pydantic import BaseModel as BaseSettings  # type: ignore
    SettingsConfigDict = dict  # type: ignore


class Settings(BaseSettings):
    """
    Central project settings. Values can be overridden via environment variables
    or a local .env file.
    """

    # --------------------------------------------------------------------------
    # Project Identity
    # --------------------------------------------------------------------------
    PROJECT_NAME: str = "FloodLens"
    PROJECT_DESCRIPTION: str = (
        "Bengaluru-focused GeoAI platform for urban flood vulnerability assessment "
        "and risk-aware route comparison."
    )
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"

    # --------------------------------------------------------------------------
    # Server & CORS Configuration
    # --------------------------------------------------------------------------
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    RELOAD: bool = True
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # --------------------------------------------------------------------------
    # Study Area & Spatial Configuration (Bengaluru, Karnataka, India)
    # --------------------------------------------------------------------------
    STUDY_AREA_NAME: str = "Bengaluru, Karnataka, India"

    # EPSG:4326 (WGS 84) - Standard geographic CRS for web map interchange (Leaflet/GeoJSON)
    CRS_INTERCHANGE: str = "EPSG:4326"

    # EPSG:32643 (UTM Zone 43N) - Metric projected CRS for accurate planar distance calculations
    CRS_PROJECTED: str = "EPSG:32643"

    # Approximate Bengaluru metropolitan bounding envelope (min_lon, min_lat, max_lon, max_lat)
    # Used solely for sanity-checking ingested datasets, NOT as an artificial boundary.
    BENGALURU_SANITY_BBOX: Tuple[float, float, float, float] = (
        77.40,  # min_lon (West)
        12.75,  # min_lat (South)
        77.85,  # max_lon (East)
        13.20,  # max_lat (North)
    )

    # Path to verified boundary vector file (e.g., BBMP ward / district boundary).
    # Kept None until the user uploads a verified administrative boundary dataset.
    VERIFIED_BOUNDARY_FILE: Optional[Path] = None

    # --------------------------------------------------------------------------
    # Filesystem & Data Directory Scaffolding
    # --------------------------------------------------------------------------
    # Base repository root: resolves D:\Flood-Lens
    BASE_DIR: Path = Path(__file__).resolve().parents[3]

    DATA_DIR: Path = BASE_DIR / "data"
    RAW_DATA_DIR: Path = DATA_DIR / "raw"
    PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"
    METADATA_DIR: Path = DATA_DIR / "metadata"

    # Explicit subdirectories for individual raw datasets
    RAW_DATASETS: Dict[str, Path] = {
        "flood_locations": RAW_DATA_DIR / "flood_locations",
        "low_lying_areas": RAW_DATA_DIR / "low_lying_areas",
        "roads": RAW_DATA_DIR / "roads",
        "drainage": RAW_DATA_DIR / "drainage",
        "water_bodies": RAW_DATA_DIR / "water_bodies",
        "elevation": RAW_DATA_DIR / "elevation",
        "rainfall": RAW_DATA_DIR / "rainfall",
        "land_cover": RAW_DATA_DIR / "land_cover",
    }

    # Metadata files
    DATA_SOURCES_CSV: Path = METADATA_DIR / "data_sources.csv"
    DATA_INVENTORY_CSV: Path = METADATA_DIR / "data_inventory.csv"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def get_raw_dir(self, category: str) -> Path:
        """Retrieve path for a specific raw dataset category."""
        if category not in self.RAW_DATASETS:
            raise KeyError(
                f"Unknown dataset category '{category}'. "
                f"Valid categories: {list(self.RAW_DATASETS.keys())}"
            )
        return self.RAW_DATASETS[category]

    def ensure_data_dirs(self) -> None:
        """Ensure all required data directories exist on disk."""
        self.RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.METADATA_DIR.mkdir(parents=True, exist_ok=True)
        for path in self.RAW_DATASETS.values():
            path.mkdir(parents=True, exist_ok=True)


# Instantiate single global settings instance
settings = Settings()
