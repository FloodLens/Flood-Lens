"""
FloodLens — Road Graph Service (Person A Ownership).

Responsibilities:
- Road network data ingestion (OSM / OSMnx).
- Construction and persistence of the routable NetworkX graph.
- Association of road segments with metric projection (EPSG:32643).
- Provision of the base graph for Person B's routing optimizations.
"""

from typing import Any, Optional
from backend.app.core.config import settings
from backend.app.utils.logging import logger


class RoadGraphService:
    """
    Constructs and maintains the Bengaluru road network graph.
    Owned by Person A.
    """

    def __init__(self):
        self.raw_roads_dir = settings.get_raw_dir("roads")
        self.processed_roads_dir = settings.PROCESSED_DATA_DIR / "roads"
        self._graph = None

    def load_base_graph(self) -> Optional[Any]:
        """
        Loads or builds the foundational road graph using OSMnx/NetworkX.
        Returns None until road datasets or OSM boundaries are loaded.
        """
        logger.info("[Person A] RoadGraphService: Initialising base graph scaffolding.")
        return None


road_graph_service = RoadGraphService()
