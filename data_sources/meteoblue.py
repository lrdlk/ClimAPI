"""
Implementación de la fuente de datos MeteoBlue.

MeteoBlue es una API profesional que proporciona datos meteorológicos
de alta calidad con diferentes formatos (JSON, Protobuf).
"""

from typing import Dict, Any, Optional
import logging
from datetime import datetime
from .base_source import BaseWeatherSource
import requests

logger = logging.getLogger(__name__)


class MeteoBlueSource(BaseWeatherSource):
    """
    Fuente de datos para MeteoBlue API.

    Requiere API key y es una solución profesional para datos
    meteorológicos de alta calidad.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://my.meteoblue.com/packages",
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """
        Inicializa la fuente MeteoBlue.

        Args:
            api_key: API key de MeteoBlue
            base_url: URL base de la API
            timeout: Timeout de peticiones HTTP
            max_retries: Número máximo de reintentos

        Raises:
            ValueError: Si no se proporciona API key
        """
        if not api_key:
            raise ValueError("MeteoBlue requiere una API key")

        super().__init__(
            name="MeteoBlue",
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
        )

    def get_current_weather(
        self, latitude: float, longitude: float, format: str = "json", **kwargs
    ) -> Dict[str, Any]:
        """
        Obtiene el clima actual desde MeteoBlue.

        Args:
            latitude: Latitud de la ubicación
            longitude: Longitud de la ubicación
            format: Formato de respuesta (json, protobuf)
            **kwargs: Argumentos adicionales

        Returns:
            Dict[str, Any]: Datos del clima actual estandarizados
        """
        logger.info(
            f"Obteniendo clima actual de MeteoBlue para "
            f"({latitude}, {longitude})"
        )

        # MeteoBlue usa un formato específico de URL
        endpoint = f"basic-1h_package?lat={latitude}&lon={longitude}&apikey={self.api_key}&format={format}"

        try:
            response = self._make_request(endpoint, params={})
            data = response.json()

            # Estandarizar respuesta (estructura específica de MeteoBlue)
            data_1h = data.get("data_1h", {})
            if data_1h and len(data_1h) > 0:
                current = data_1h[-1]  # Último dato disponible
            else:
                current = {}

            standardized = {
                "source": self.name,
                "timestamp": datetime.now().isoformat(),
                "location": {"lat": latitude, "lon": longitude},
                "temperature": current.get("temperature"),
                "humidity": current.get("relative_humidity"),
                "precipitation": current.get("precipitation"),
                "wind_speed": current.get("wind_speed"),
                "wind_direction": current.get("wind_direction"),
                "pressure": current.get("pressure_msl"),
                "raw_data": data,
            }

            logger.debug(f"Datos obtenidos exitosamente")
            return standardized

        except Exception as e:
            logger.error(f"Error al obtener clima actual: {e}")
            raise

    def get_forecast(
        self,
        latitude: float,
        longitude: float,
        days: int = 5,
        format: str = "json",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Obtiene el pronóstico del clima desde MeteoBlue.

        Args:
            latitude: Latitud de la ubicación
            longitude: Longitud de la ubicación
            days: Número de días de pronóstico
            format: Formato de respuesta (json, protobuf)
            **kwargs: Argumentos adicionales

        Returns:
            Dict[str, Any]: Datos del pronóstico estandarizados
        """
        logger.info(
            f"Obteniendo pronóstico de {days} días desde MeteoBlue "
            f"para ({latitude}, {longitude})"
        )

        # MeteoBlue tiene diferentes paquetes según los días
        if days <= 1:
            package = "basic-1h_package"
        elif days <= 5:
            package = "basic-day_package"
        else:
            package = "basic-16d_package"

        endpoint = f"{package}?lat={latitude}&lon={longitude}&apikey={self.api_key}&format={format}"

        try:
            response = self._make_request(endpoint, params={})
            data = response.json()

            # Estandarizar respuesta
            standardized = {
                "source": self.name,
                "timestamp": datetime.now().isoformat(),
                "location": {"lat": latitude, "lon": longitude},
                "forecast_days": days,
                "data": data,
                "raw_data": data,
            }

            logger.debug(f"Pronóstico obtenido exitosamente")
            return standardized

        except Exception as e:
            logger.error(f"Error al obtener pronóstico: {e}")
            raise

    def get_meteogram_image(
        self,
        latitude: float,
        longitude: float,
        tz: str = "America/Bogota",
        location_name: Optional[str] = None,
        dpi: int = 72,
        lang: str = "en",
        temperature_units: str = "C",
        precipitation_units: str = "mm",
        windspeed_units: str = "kmh",
        format: str = "png",
    ) -> bytes:
        """
        Descarga la imagen de meteograma de MeteoBlue.

        Returns:
            bytes: contenido binario de la imagen.
        """
        logger.info(
            f"Descargando meteograma para ({latitude}, {longitude}) en {tz}"
        )

        images_base = "https://my.meteoblue.com/images"
        endpoint = (
            f"meteogram_one?lat={latitude}&lon={longitude}&asl=1405"
            f"&tz={requests.utils.quote(tz)}&apikey={self.api_key}"
            f"&format={format}&dpi={dpi}&lang={lang}"
            f"&temperature_units={temperature_units}"
            f"&precipitation_units={precipitation_units}"
            f"&windspeed_units={windspeed_units}"
        )
        if location_name:
            endpoint += f"&location_name={requests.utils.quote(location_name)}"

        try:
            # petición directa porque el base_url es para /packages
            url = f"{images_base}/{endpoint}"
            resp = requests.get(url, timeout=self.timeout)
            resp.raise_for_status()
            return resp.content
        except Exception as e:
            logger.error(f"Error al obtener meteograma: {e}")
            raise


