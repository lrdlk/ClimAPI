"""
Módulo para consumir datos meteorológicos desde la API de Open-Meteo.

Este módulo proporciona funciones para obtener datos horarios del clima
(temperatura, humedad, precipitación y velocidad del viento) usando
la API pública de Open-Meteo.
"""

import requests
from typing import Dict, Optional
import json


def get_weather_data(
    latitude: float,
    longitude: float,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    timezone: str = "America/Bogota"
) -> Dict:
    """
    Obtiene datos meteorológicos horarios desde la API de Open-Meteo.
    
    Args:
        latitude: Latitud de la ubicación (ej: 6.244 para Medellín)
        longitude: Longitud de la ubicación (ej: -75.581 para Medellín)
        start_date: Fecha de inicio en formato YYYY-MM-DD (opcional, por defecto hoy)
        end_date: Fecha de fin en formato YYYY-MM-DD (opcional, por defecto hoy)
        timezone: Zona horaria (por defecto America/Bogota)
    
    Returns:
        Dict: Respuesta JSON de la API con los datos meteorológicos
    
    Raises:
        requests.exceptions.RequestException: Si hay un error al hacer la petición
        ValueError: Si los parámetros son inválidos
    """
    # URL base de la API de Open-Meteo
    base_url = "https://api.open-meteo.com/v1/forecast"
    
    # Parámetros de la petición
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,relative_humidity_2m,precipitation,windspeed_10m",
        "timezone": timezone
    }
    
    # Agregar fechas si se proporcionan
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    
    try:
        # Realizar la petición GET
        response = requests.get(base_url, params=params, timeout=30)
        
        # Verificar que la petición fue exitosa
        response.raise_for_status()
        
        # Retornar los datos en formato JSON
        data = response.json()
        
        # Validar que la respuesta contiene datos
        if "hourly" not in data:
            raise ValueError("La respuesta de la API no contiene datos horarios")
        
        return data
    
    except requests.exceptions.Timeout:
        raise requests.exceptions.RequestException(
            "La petición a la API excedió el tiempo de espera"
        )
    except requests.exceptions.HTTPError as e:
        raise requests.exceptions.RequestException(
            f"Error HTTP al consultar la API: {e}"
        )
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            f"Error al conectarse con la API: {e}"
        )
    except json.JSONDecodeError:
        raise ValueError("La respuesta de la API no es un JSON válido")


def validate_coordinates(latitude: float, longitude: float) -> bool:
    """
    Valida que las coordenadas estén en rangos válidos.
    
    Args:
        latitude: Latitud (-90 a 90)
        longitude: Longitud (-180 a 180)
    
    Returns:
        bool: True si las coordenadas son válidas
    """
    if not (-90 <= latitude <= 90):
        raise ValueError(f"Latitud inválida: {latitude}. Debe estar entre -90 y 90")
    if not (-180 <= longitude <= 180):
        raise ValueError(f"Longitud inválida: {longitude}. Debe estar entre -180 y 180")
    return True

