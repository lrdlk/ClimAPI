"""
Implementación de la fuente de datos MeteoBlue.

MeteoBlue es una API profesional que proporciona datos meteorológicos
de alta calidad con diferentes formatos (JSON, Protobuf).
"""

from typing import Dict, Any, Optional
import logging
from datetime import datetime
try:
    from .base_source import BaseWeatherSource
except Exception:
    import requests

    class BaseWeatherSource:
        def __init__(self, name: str, base_url: str, api_key: str, timeout: int, max_retries: int):
            self.name = name
            self.base_url = base_url.rstrip("/")
            self.api_key = api_key
            self.timeout = timeout
            self.max_retries = max_retries

        def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None):
            url = endpoint if endpoint.startswith("http") else f"{self.base_url}/{endpoint.lstrip('/')}"
            session = requests.Session()
            for attempt in range(self.max_retries):
                try:
                    resp = session.get(url, params=params or {}, timeout=self.timeout)
                    resp.raise_for_status()
                    return resp
                except Exception as e:
                    if attempt == self.max_retries - 1:
                        raise
                    continue

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

    def get_basic_day_clouds_sunmoon(
        self,
        latitude: float,
        longitude: float,
        asl: int = 0,
        format: str = "json",
    ) -> Dict[str, Any]:
        """
        Obtiene el paquete combinado basic-day_clouds-day_sunmoon de MeteoBlue.

        Args:
            latitude: Latitud
            longitude: Longitud
            asl: Altitud sobre el nivel del mar (metros)
            format: Formato de respuesta (json)

        Returns:
            Dict con datos crudos y metadatos.
        """
        logger.info(
            f"Obteniendo paquete basic-day_clouds-day_sunmoon para ({latitude}, {longitude})"
        )

        endpoint = (
            f"basic-day_clouds-day_sunmoon?apikey={self.api_key}"
            f"&lat={latitude}&lon={longitude}&asl={asl}&format={format}"
        )

        try:
            response = self._make_request(endpoint, params={})
            data = response.json()

            return {
                "source": self.name,
                "timestamp": datetime.now().isoformat(),
                "location": {"lat": latitude, "lon": longitude, "asl": asl},
                "data": data,
                "raw_data": data,
            }
        except Exception as e:
            logger.error(f"Error al obtener paquete basic-day_clouds-day_sunmoon: {e}")
            raise

    def get_meteogram_image(
        self,
        latitude: float,
        longitude: float,
        asl: int,
        location_name: str,
        tz: str = "America/Bogota",
        dpi: int = 72,
        lang: str = "en",
        temperature_units: str = "C",
        precipitation_units: str = "mm",
        windspeed_units: str = "kmh",
        format: str = "png",
        save_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Obtiene la imagen de meteograma (meteogram_one) y opcionalmente la guarda.

        Returns:
            Dict con bytes de imagen y metadatos. Si save_path se proporciona,
            también escribe el archivo en disco.
        """
        logger.info(
            f"Obteniendo imagen meteogram_one para ({latitude}, {longitude})"
        )

        # Este endpoint está bajo /images
        images_base = self.base_url.replace("/packages", "/images")
        endpoint = (
            f"{images_base}/meteogram_one?lat={latitude}&lon={longitude}&asl={asl}"
            f"&tz={tz}&apikey={self.api_key}&format={format}&dpi={dpi}&lang={lang}"
            f"&temperature_units={temperature_units}&precipitation_units={precipitation_units}"
            f"&windspeed_units={windspeed_units}&location_name={location_name}"
        )

        try:
            # _make_request espera endpoint relativo a base_url; para imagen usamos URL completo
            response = self._make_request(endpoint, params={})
            content = response.content

            if save_path:
                try:
                    import os
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                    with open(save_path, "wb") as f:
                        f.write(content)
                    saved = True
                except Exception as file_err:
                    logger.warning(f"No se pudo guardar imagen en {save_path}: {file_err}")
                    saved = False
            else:
                saved = False

            return {
                "source": self.name,
                "timestamp": datetime.now().isoformat(),
                "location": {"lat": latitude, "lon": longitude, "asl": asl},
                "format": format,
                "bytes": content,
                "saved": saved,
                "save_path": save_path,
            }
        except Exception as e:
            logger.error(f"Error al obtener meteograma: {e}")
            raise


