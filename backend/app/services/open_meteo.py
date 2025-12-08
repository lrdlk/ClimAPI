"""
Cliente para Open-Meteo API.
Servicio meteorológico gratuito sin necesidad de API key.
"""
import httpx
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Constantes
API_BASE_URL = "https://api.open-meteo.com/v1/forecast"
DEFAULT_TIMEOUT = 10.0
DEFAULT_TIMEZONE = "America/Bogota"


async def get_weather_data(
    latitude: float,
    longitude: float,
    timezone: str = DEFAULT_TIMEZONE
) -> Dict[str, Any]:
    """
    Obtiene datos meteorológicos de Open-Meteo API.
    
    Args:
        latitude: Latitud de la ubicación (-90 a 90)
        longitude: Longitud de la ubicación (-180 a 180)
        timezone: Zona horaria (default: America/Bogota)
    
    Returns:
        Diccionario con datos meteorológicos
    
    Raises:
        ValueError: Si las coordenadas son inválidas
        httpx.HTTPError: Si hay error en la petición HTTP
    """
    # Validar coordenadas
    if not validate_coordinates(latitude, longitude):
        raise ValueError(
            f"Coordenadas inválidas: lat={latitude}, lon={longitude}"
        )
    
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ",".join([
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "wind_speed_10m",
            "wind_direction_10m"
        ]),
        "current_weather": "true",
        "timezone": timezone
    }
    
    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            logger.debug(f"Petición a Open-Meteo: lat={latitude}, lon={longitude}")
            response = await client.get(API_BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            logger.info(
                f"✓ Datos obtenidos de Open-Meteo para "
                f"({latitude:.4f}, {longitude:.4f})"
            )
            return data
            
    except httpx.TimeoutException:
        logger.error(f"⏱️ Timeout al conectar con Open-Meteo API")
        raise
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ Error HTTP {e.response.status_code}: {e.response.text}")
        raise
    except Exception as e:
        logger.error(f"❌ Error inesperado en Open-Meteo: {str(e)}")
        raise


def validate_coordinates(lat: float, lon: float) -> bool:
    """
    Valida que las coordenadas estén en rangos válidos.
    
    Args:
        lat: Latitud
        lon: Longitud
    
    Returns:
        True si las coordenadas son válidas
    """
    is_valid = -90 <= lat <= 90 and -180 <= lon <= 180
    
    if not is_valid:
        logger.warning(
            f"Coordenadas fuera de rango: lat={lat}, lon={lon}"
        )
    
    return is_valid


def get_location_name(latitude: float, longitude: float) -> str:
    """
    Genera un nombre de ubicación basado en coordenadas.
    
    Args:
        latitude: Latitud
        longitude: Longitud
    
    Returns:
        String con formato "lat_lon"
    """
    return f"{latitude:.4f}_{longitude:.4f}"