"""
FloodLens — Feature Generation Scaffolding.

Generates derived spatial features for vulnerability assessment and routing:
- Person A: Historical flood density, DBSCAN cluster assignment, road network graph
- Person B: Distance to drainage (SWD), distance to water bodies, elevation/slope values

Usage:
    python scripts/generate_features.py
"""

import sys
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app.core.config import settings


def generate_person_a_features():
    """Person A module: Flood exposure features & DBSCAN spatial clusters."""
    print("[*] [Person A] Initialising Flood Exposure & DBSCAN Feature Generation...")
    print("    - Awaiting processed flood_locations and low_lying_areas.")


def generate_person_b_features():
    """Person B module: Infrastructure & terrain features (drainage, lakes, DEM)."""
    print("[*] [Person B] Initialising Terrain & Infrastructure Feature Generation...")
    print("    - Awaiting processed drainage, water_bodies, and elevation DEM.")


def main():
    print(f"==================================================")
    print(f"FLOODLENS FEATURE GENERATION — Study Area: {settings.STUDY_AREA_NAME}")
    print(f"==================================================")
    generate_person_a_features()
    generate_person_b_features()
    print("[+] Feature generation scaffolding ready.")


if __name__ == "__main__":
    main()
