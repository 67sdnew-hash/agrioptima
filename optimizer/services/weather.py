"""
AgriOptima - Hyper-Local Weather & Climate Risk Service
Queries the Open-Meteo Global Weather API to calculate 14-day cumulative rainfall,
temperature profiles, and fertilizer leaching / run-off risks.
"""

import urllib.request
import json
from typing import Dict, Any

DEFAULT_PRESETS = {
    'Punjab, India': {'lat': 31.1471, 'lon': 75.3412},
    'Iowa (Corn Belt), USA': {'lat': 42.0308, 'lon': -93.6319},
    'Central Valley (California)': {'lat': 36.7783, 'lon': -119.4179},
    'Nile Delta, Egypt': {'lat': 30.8761, 'lon': 31.0004},
    'Thames Valley, UK': {'lat': 51.4543, 'lon': -0.9781},
    'Sao Paulo, Brazil': {'lat': -23.5505, 'lon': -46.6333},
}

def fetch_weather_forecast(lat: float, lon: float) -> Dict[str, Any]:
    """
    Fetches real-time weather & 14-day precipitation projections from Open-Meteo.
    """
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat:.4f}&longitude={lon:.4f}&"
        f"current=temperature_2m,relative_humidity_2m,precipitation,weather_code&"
        f"daily=precipitation_sum,precipitation_probability_max,temperature_2m_max,temperature_2m_min&"
        f"forecast_days=14&timezone=auto"
    )

    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'AgriOptima-Precision-Agriculture/1.0'}
        )
        with urllib.request.urlopen(req, timeout=6) as response:
            data = json.loads(response.read().decode('utf-8'))

        daily_precip = data.get('daily', {}).get('precipitation_sum', [])
        total_14d_precip = sum(daily_precip) if daily_precip else 0.0

        current_temp = data.get('current', {}).get('temperature_2m', 22.0)
        current_humidity = data.get('current', {}).get('relative_humidity_2m', 60.0)

        # Estimate seasonal baseline rainfall (scaling 14-day projection across 90-day growing phase)
        estimated_seasonal_rainfall = round(max(350.0, min(1600.0, total_14d_precip * 6.5 + 300.0)), 1)

        # Nitrate Leaching & Soil Run-Off Risk Assessment
        max_single_day_rain = max(daily_precip) if daily_precip else 0.0
        if max_single_day_rain > 35.0 or total_14d_precip > 120.0:
            leaching_risk = "HIGH"
            risk_color = "red"
            risk_message = "Heavy rainfall projected within forecast window. Avoid immediate broadcast application to prevent nitrate runoff."
        elif max_single_day_rain > 18.0 or total_14d_precip > 60.0:
            leaching_risk = "MODERATE"
            risk_color = "amber"
            risk_message = "Moderate precipitation expected. Band fertilizer 5cm deep to minimize surface washing."
        else:
            leaching_risk = "LOW / OPTIMAL"
            risk_color = "emerald"
            risk_message = "Favorable soil moisture conditions for nutrient absorption."

        return {
            'success': True,
            'latitude': lat,
            'longitude': lon,
            'current_temp': current_temp,
            'current_humidity': current_humidity,
            'total_14d_precip_mm': round(total_14d_precip, 1),
            'recommended_rainfall_mm': estimated_seasonal_rainfall,
            'max_single_day_rain_mm': round(max_single_day_rain, 1),
            'leaching_risk': leaching_risk,
            'risk_color': risk_color,
            'risk_message': risk_message,
            'daily_dates': data.get('daily', {}).get('time', [])[:7],
            'daily_precip': [round(p, 1) for p in daily_precip[:7]]
        }

    except Exception as e:
        # Fallback for offline or unreachable situations
        return {
            'success': False,
            'error': str(e),
            'latitude': lat,
            'longitude': lon,
            'current_temp': 24.0,
            'current_humidity': 65.0,
            'total_14d_precip_mm': 45.0,
            'recommended_rainfall_mm': 750.0,
            'max_single_day_rain_mm': 12.0,
            'leaching_risk': "OPTIMAL",
            'risk_color': "emerald",
            'risk_message': "Standard soil moisture conditions assumed.",
            'daily_dates': [],
            'daily_precip': []
        }
