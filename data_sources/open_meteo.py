"""
Cliente Open-Meteo - Migrado desde data_sources/
"""
import httpx
from typing import Dict, Any

async def get_weather_data(latitude: float, longitude: float) -> Dict[str, Any]:
    """Obtiene datos de Open-Meteo."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,relative_humidity_2m,precipitation",
        "timezone": "America/Bogota"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()

def validate_coordinates(lat: float, lon: float) -> bool:
    """Valida coordenadas."""
    return -90 <= lat <= 90 and -180 <= lon <= 180

