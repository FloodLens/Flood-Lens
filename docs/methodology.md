# FloodLens — Methodology & Analytical Framework

This document outlines the end-to-end scientific and GeoAI methodology implemented in FloodLens.

---

## 1. Vulnerability Assessment vs. Hydrodynamic Simulation

A critical architectural distinction governs the FloodLens platform:

- **What FloodLens IS:** An explainable, data-driven **urban vulnerability assessment platform**. It combines historical empirical inundation records, topological terrain depressions, hydrological drainage corridors, and road network topology to rank spatial exposure.
- **What FloodLens IS NOT:** A dynamic, physics-based numerical hydraulic model (e.g., SWMM, HEC-RAS, or 2D Navier-Stokes hydrodynamic solver). FloodLens does not simulate real-time turbulent pipe flows, rainfall hyetographs, or transient weir discharges.

---

## 2. Multi-Stage Analytical Pipeline

```
1. Ingestion & Validation  ──►  2. Projected Metric Harmonisation (EPSG:32643)
                                            │
        ┌───────────────────────────────────┴───────────────────────────────────┐
        ▼                                                                       ▼
3. DBSCAN Spatial Clustering (Person A)                4. Multi-Criteria Vulnerability Index (Person B)
   - Metric density search in UTM 43N                     - Distance to Rajakaluve drains
   - Chronic hotspot discovery                            - Distance to lakebeds (keres)
   - Cluster radius and centroid mapping                  - DEM elevation depression & slope
        │                                                                       │
        └───────────────────────────────────┬───────────────────────────────────┘
                                            ▼
                       5. Graph Integration & Risk-Aware Routing (Person B)
                          - OSMnx Base Network (Person A)
                          - Edge impedance: w_e = length * (1 + alpha * vuln_e)
                          - Pareto comparison: Shortest vs Risk-Aware Route
                                            │
                                            ▼
                       6. Interactive Cartographic Presentation
```

---

## 3. Metric Spatial Harmonisation

To compute valid Euclidean distances and density radiuses in meters without geographic angular distortion (lat/lon degree curvature), all spatial analysis is carried out in:

$$\text{EPSG:32643 — WGS 84 / UTM Zone 43N}$$

When exchanging spatial vectors with web maps (Leaflet) and client APIs, geometries are converted into:

$$\text{EPSG:4326 — WGS 84 (Decimal Degrees)}$$

---

## 4. DBSCAN Spatial Clustering (Person A)

Historical flood observations are clustered using **DBSCAN (Density-Based Spatial Clustering of Applications with Noise)**:

- **Inputs:** Projected 2D coordinates $(X, Y)$ in EPSG:32643.
- **Parameters:**
  - $\epsilon$ (Epsilon): Spatial neighbourhood radius in meters (e.g. 200m – 400m).
  - $MinPts$ (Minimum points): Minimum incident observations required to designate a dense flood core (e.g. 3 points).
- **Outputs:**
  - Core clusters representing persistent, chronic flood-prone nodes (e.g., underpasses, low valley junctions).
  - Noise points (outliers with label `-1`) indicating isolated, non-recurrent events.

---

## 5. Explainable Multi-Criteria Vulnerability Scoring (Person B)

Rather than using an opaque black-box deep learning model, FloodLens applies an **explainable, transparent multi-criteria formula** to evaluate every road edge $e$:

$$V_e = w_{\text{flood}} \cdot F_e + w_{\text{drain}} \cdot D_e + w_{\text{lake}} \cdot L_e + w_{\text{elev}} \cdot E_e$$

Where:
- $F_e$: Historical flood cluster proximity score (inverse exponential distance to DBSCAN cluster centroids).
- $D_e$: Drainage proximity score (higher vulnerability within 30m of major rajakaluve stormwater drains).
- $L_e$: Lake proximity score (higher exposure within lakebed buffer zones).
- $E_e$: Topographical depression score (calculated from Copernicus DEM GLO-30 relative elevation).
- $\sum w_i = 1.0$: Transparently calibrated weighting factors.

---

## 6. Risk-Aware Route Comparison (Person B)

To help navigators and emergency vehicles avoid flood-prone zones, FloodLens models routing on a directed NetworkX graph $G = (V, E)$:

1. **Shortest-Distance Route:**
   Standard Dijkstra / A* where edge cost is purely physical distance:
   $$\text{Cost}_{\text{standard}}(e) = \text{length}(e)$$
2. **Risk-Aware Route:**
   Edge cost is dynamically penalized by its vulnerability score $V_e$:
   $$\text{Cost}_{\text{risk-aware}}(e) = \text{length}(e) \cdot \left(1.0 + \alpha \cdot V_e^{\beta}\right)$$
   Where $\alpha$ is the risk penalty multiplier and $\beta$ is a non-linear aversion factor.
3. **Trade-off Comparison:**
   The system calculates:
   - $\Delta \text{Distance} = \text{Distance}_{\text{risk-aware}} - \text{Distance}_{\text{shortest}}$
   - $\Delta \text{Exposure} = \frac{\text{Exposure}_{\text{shortest}} - \text{Exposure}_{\text{risk-aware}}}{\text{Exposure}_{\text{shortest}}} \times 100\%$
