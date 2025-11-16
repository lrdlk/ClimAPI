"""
Paquete para consumir datos de diferentes fuentes meteorológicas.
"""

from .open_meteo import get_weather_data, validate_coordinates

__all__ = ['get_weather_data', 'validate_coordinates']

