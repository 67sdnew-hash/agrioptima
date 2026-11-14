"""
AgriOptima - Multispectral Satellite & Drone NDVI Crop Vigor Heatmap Service
Generates Normalized Difference Vegetation Index (NDVI) raster grids,
calculates canopy chlorophyll index, biomass estimation, and zone-specific
Variable Rate Nitrogen prescriptions.
"""

import math
import random

# Multispectral NDVI color ramp specifications
NDVI_PALETTE = [
    {"min": -1.0, "max": 0.15, "color": "#78350f", "label": "Bare Soil / Water / Non-Veg", "textColor": "#ffffff"},
    {"min": 0.15, "max": 0.30, "color": "#ef4444", "label": "Severe Stress / Stunted", "textColor": "#ffffff"},
    {"min": 0.30, "max": 0.45, "color": "#f59e0b", "label": "Low Vigor / Nutrient Starvation", "textColor": "#000000"},
    {"min": 0.45, "max": 0.60, "color": "#84cc16", "label": "Moderate Vigor / Vegetative", "textColor": "#000000"},
    {"min": 0.60, "max": 0.75, "color": "#22c55e", "label": "Healthy Canopy / Optimal Growth", "textColor": "#ffffff"},
    {"min": 0.75, "max": 1.00, "color": "#15803d", "label": "Dense Biomass / Peak Vigor", "textColor": "#ffffff"},
]


def get_ndvi_color_and_label(ndvi_val: float) -> dict:
    """Returns color hex and descriptive label for an NDVI score."""
    val = max(-1.0, min(1.0, float(ndvi_val)))
    for bracket in NDVI_PALETTE:
        if bracket["min"] <= val <= bracket["max"]:
            return bracket
    return NDVI_PALETTE[-1]


def generate_field_ndvi_analysis(lat: float, lon: float, zones: list = None, radius_deg: float = 0.008) -> dict:
    """
    Simulates high-resolution multispectral remote sensing (Sentinel-2 MSI / Landsat 9 / Drone NIR).
    Generates a GeoJSON Grid of NDVI polygons around the farm coordinate,
    and computes zonal chlorophyll & variable rate prescription factors.
    """
    lat = float(lat)
    lon = float(lon)
    
    # Deterministic pseudo-random seed based on coordinates so the field remains consistent
    seed_int = int(abs(lat * 10000) + abs(lon * 10000))
    rnd = random.Random(seed_int)

    # Grid dimension: 8x8 cells covering the field boundary
    grid_size = 8
    step_lat = (radius_deg * 2) / grid_size
    step_lon = (radius_deg * 2) / grid_size
    start_lat = lat - radius_deg
    start_lon = lon - radius_deg

    features = []
    all_ndvi_values = []

    for r in range(grid_size):
        for c in range(grid_size):
            cell_lat_min = start_lat + (r * step_lat)
            cell_lat_max = cell_lat_min + step_lat
            cell_lon_min = start_lon + (c * step_lon)
            cell_lon_max = cell_lon_min + step_lon

            # Spatial distance from farm centroid creates realistic agronomic canopy gradients
            dist_from_center = math.hypot((r - grid_size / 2), (c - grid_size / 2)) / (grid_size / 2)
            
            # Base NDVI between 0.30 and 0.82 with spatial continuity
            noise = (rnd.random() - 0.5) * 0.22
            base_val = 0.72 - (dist_from_center * 0.28) + noise
            # Soil variability pocket
            if (r + c) % 5 == 0:
                base_val -= 0.18
            
            ndvi_val = round(max(0.18, min(0.88, base_val)), 3)
            all_ndvi_values.append(ndvi_val)

            palette_info = get_ndvi_color_and_label(ndvi_val)

            # Build polygon coordinate ring [Lon, Lat] format for GeoJSON
            coords = [
                [round(cell_lon_min, 6), round(cell_lat_min, 6)],
                [round(cell_lon_max, 6), round(cell_lat_min, 6)],
                [round(cell_lon_max, 6), round(cell_lat_max, 6)],
                [round(cell_lon_min, 6), round(cell_lat_max, 6)],
                [round(cell_lon_min, 6), round(cell_lat_min, 6)]
            ]

            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coords]
                },
                "properties": {
                    "cell_id": f"R{r+1}C{c+1}",
                    "ndvi": ndvi_val,
                    "chlorophyll_spad": round(ndvi_val * 58.0 + 8.5, 1),
                    "biomass_est_tha": round(ndvi_val * 6.4 + 1.2, 2),
                    "color": palette_info["color"],
                    "textColor": palette_info["textColor"],
                    "label": palette_info["label"],
                    "center": [
                        round((cell_lat_min + cell_lat_max) / 2, 6),
                        round((cell_lon_min + cell_lon_max) / 2, 6)
                    ]
                }
            }
            features.append(feature)

    mean_ndvi = round(sum(all_ndvi_values) / len(all_ndvi_values), 3)
    min_ndvi = round(min(all_ndvi_values), 3)
    max_ndvi = round(max(all_ndvi_values), 3)
    health_score = int(min(100, max(15, mean_ndvi * 125)))

    # Process custom zones if provided
    zone_assessments = []
    if zones:
        for idx, z in enumerate(zones):
            z_name = z.get('name', f'Zone {idx + 1}')
            z_crop = z.get('crop', 'Wheat')
            z_area = float(z.get('area', 1.0))
            
            # Predict zone specific NDVI
            zone_ndvi = round(max(0.20, min(0.85, mean_ndvi + ((idx % 3 - 1) * 0.12))), 2)
            
            # Agronomic VRA N recommendation based on NDVI deficit
            # If NDVI < 0.45: crop is nitrogen starved; prescribe +20 to +30 kg/ha N
            # If NDVI > 0.70: canopy is dense luxury consumption; reduce N by -10 to -15 kg/ha to avoid lodging
            if zone_ndvi < 0.40:
                n_rec_adjustment = +25.0
                vigor_eval = "Underperforming / Severe Nitrogen Deficit"
            elif zone_ndvi < 0.55:
                n_rec_adjustment = +12.0
                vigor_eval = "Sub-optimal / Moderate Top-dress Recommended"
            elif zone_ndvi < 0.72:
                n_rec_adjustment = 0.0
                vigor_eval = "Optimal Biomass / Maintain Baseline Prescription"
            else:
                n_rec_adjustment = -15.0
                vigor_eval = "Luxury Consumption / Reduce N to Prevent Lodging"

            zone_assessments.append({
                "zone_id": z.get('id', idx + 1),
                "name": z_name,
                "crop": z_crop,
                "area_ha": z_area,
                "zone_ndvi": zone_ndvi,
                "vigor_evaluation": vigor_eval,
                "chlorophyll_spad": round(zone_ndvi * 56.0 + 9.0, 1),
                "n_adjustment_kg_ha": n_rec_adjustment,
                "color": get_ndvi_color_and_label(zone_ndvi)["color"]
            })

    geojson_result = {
        "type": "FeatureCollection",
        "features": features
    }

    return {
        "success": True,
        "centroid": {"lat": lat, "lon": lon},
        "mean_ndvi": mean_ndvi,
        "min_ndvi": min_ndvi,
        "max_ndvi": max_ndvi,
        "health_score": health_score,
        "canopy_uniformity_pct": round(max(60.0, 100.0 - ((max_ndvi - min_ndvi) * 80)), 1),
        "geojson": geojson_result,
        "palette": NDVI_PALETTE,
        "zones": zone_assessments
    }
