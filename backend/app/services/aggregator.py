"""
Agregador de datos meteorológicos de múltiples fuentes.
Integra: Open-Meteo, SIATA, OpenWeatherMap, MeteoBlue, Radar IDEAM, etc.
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class WeatherSource:
    """Información de una fuente de datos."""
    name: str
    icon: str
    active: bool
    priority: int
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: Optional[str] = None
    cached: bool = False


class WeatherAggregator:
    """
    Agregador de datos meteorológicos de múltiples fuentes.
    Obtiene datos en paralelo y los normaliza a un formato estándar.
    """
    
    def __init__(self):
        """Inicializa el agregador."""
        # Cargar API keys desde .env
        self.openweather_api_key = os.getenv("OPENWEATHER_API_KEY", "")
        self.meteoblue_api_key = os.getenv("METEOBLUE_API_KEY", "")
        self.ideam_username = os.getenv("IDEAM_USERNAME", "")
        self.ideam_password = os.getenv("IDEAM_PASSWORD", "")
        self.ideam_radar_url = os.getenv("IDEAM_RADAR_URL", "http://www.pronosticosyalertas.gov.co/archivos-radar")
        
        # Determinar qué fuentes están activas basado en credenciales
        openweather_active = bool(self.openweather_api_key)
        meteoblue_active = bool(self.meteoblue_api_key)
        ideam_active = bool(self.ideam_radar_url)  # IDEAM es público
        
        self.sources = {
            "open_meteo": WeatherSource(
                name="Open-Meteo",
                icon="🌐",
                active=True,
                priority=1
            ),
            "siata": WeatherSource(
                name="SIATA (Medellín)",
                icon="🏙️",
                active=True,
                priority=2
            ),
            "openweather": WeatherSource(
                name="OpenWeatherMap",
                icon="☁️",
                active=openweather_active,
                priority=3
            ),
            "meteoblue": WeatherSource(
                name="MeteoBlue",
                icon="🎯",
                active=meteoblue_active,
                priority=4
            ),
            "radar_ideam": WeatherSource(
                name="Radar IDEAM",
                icon="📡",
                active=ideam_active,
                priority=5
            ),
        }
        
        # Log de fuentes activas
        active_sources = [s.name for s in self.sources.values() if s.active]
        logger.info(f"Fuentes activas: {', '.join(active_sources)}")
    
    async def fetch_all_sources(
        self,
        latitude: float,
        longitude: float,
        timeout: int = 10
    ) -> Dict[str, WeatherSource]:
        """
        Obtiene datos de todas las fuentes en paralelo.
        
        Args:
            latitude: Latitud de la ubicación
            longitude: Longitud de la ubicación
            timeout: Timeout en segundos para cada fuente
        
        Returns:
            Diccionario con datos de cada fuente
        """
        tasks = []
        source_names = []
        
        for name, source in self.sources.items():
            if source.active:
                source_names.append(name)
                if name == "open_meteo":
                    tasks.append(self._fetch_openmeteo(latitude, longitude, timeout))
                elif name == "siata":
                    tasks.append(self._fetch_siata(latitude, longitude, timeout))
                elif name == "openweather":
                    tasks.append(self._fetch_openweather(latitude, longitude, timeout))
                elif name == "meteoblue":
                    tasks.append(self._fetch_meteoblue(latitude, longitude, timeout))
                    tasks.append(self._fetch_meteoblue_meteogram(latitude, longitude, timeout))
                elif name == "radar_ideam":
                    tasks.append(self._fetch_radar_ideam(latitude, longitude, timeout))
        
        # Ejecutar todas las tareas en paralelo
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Procesar resultados
            for source_name, result in zip(source_names, results):
                if isinstance(result, Exception):
                    self.sources[source_name].error = str(result)
                    logger.error(f"Error en {source_name}: {str(result)}")
                else:
                    self.sources[source_name].data = result.get("data")
                    self.sources[source_name].error = result.get("error")
                    self.sources[source_name].timestamp = result.get("timestamp")
                    self.sources[source_name].cached = result.get("cached", False)
        
        return self.sources
    
    async def _fetch_openmeteo(
        self,
        latitude: float,
        longitude: float,
        timeout: int
    ) -> Dict[str, Any]:
        """Obtiene datos de Open-Meteo."""
        try:
            from backend.app.services.open_meteo import get_weather_data
            data = await asyncio.wait_for(
                get_weather_data(latitude, longitude),
                timeout=timeout
            )
            return {
                "data": data,
                "timestamp": datetime.utcnow().isoformat(),
                "cached": False
            }
        except asyncio.TimeoutError:
            return {"error": "Timeout al obtener datos"}
        except Exception as e:
            logger.error(f"Error Open-Meteo: {str(e)}")
            return {"error": str(e)}
    
    async def _fetch_siata(
        self,
        latitude: float,
        longitude: float,
        timeout: int
    ) -> Dict[str, Any]:
        """Obtiene datos de SIATA (simulado)."""
        try:
            # SIATA es específico de Medellín, usar coordenadas fijas
            if abs(latitude - 6.2442) < 1 and abs(longitude - (-75.5812)) < 1:
                return {
                    "data": {
                        "temperature": 22.5,
                        "humidity": 65,
                        "pressure": 1013,
                        "wind_speed": 3.2,
                        "location": "Medellín"
                    },
                    "timestamp": datetime.utcnow().isoformat(),
                    "cached": False
                }
            else:
                return {"error": "SIATA solo disponible en Medellín"}
        except Exception as e:
            return {"error": str(e)}
    
    async def _fetch_openweather(
        self,
        latitude: float,
        longitude: float,
        timeout: int
    ) -> Dict[str, Any]:
        """Obtiene datos de OpenWeatherMap."""
        try:
            if not self.openweather_api_key:
                return {"error": "API key de OpenWeatherMap no configurada"}
            
            import httpx
            
            params = {
                "lat": latitude,
                "lon": longitude,
                "appid": self.openweather_api_key,
                "units": "metric",
                "lang": "es"
            }
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(
                    "https://api.openweathermap.org/data/2.5/weather",
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"✓ Datos obtenidos de OpenWeatherMap para ({latitude}, {longitude})")
                return {
                    "data": {
                        "temperature": data["main"]["temp"],
                        "humidity": data["main"]["humidity"],
                        "pressure": data["main"]["pressure"],
                        "wind_speed": data["wind"]["speed"],
                        "description": data["weather"][0]["description"],
                        "location": data.get("name", "")
                    },
                    "timestamp": datetime.utcnow().isoformat(),
                    "cached": False
                }
        except Exception as e:
            logger.error(f"Error OpenWeatherMap: {str(e)}")
            return {"error": str(e)}
    
    async def _fetch_meteoblue(
        self,
        latitude: float,
        longitude: float,
        timeout: int
    ) -> Dict[str, Any]:
        """Obtiene datos del paquete basic-day_clouds-day_sunmoon de MeteoBlue."""
        try:
            if not self.meteoblue_api_key:
                return {"error": "API key de MeteoBlue no configurada"}
            # Usar la clase de data_sources para mantener consistencia
            from data_sources.meteoblue import MeteoBlueSource
            src = MeteoBlueSource(api_key=self.meteoblue_api_key)
            res = src.get_basic_day_clouds_sunmoon(latitude=latitude, longitude=longitude, asl=700)
            logger.info(f"✓ Paquete MeteoBlue (basic-day_clouds-day_sunmoon) obtenido")
            return {
                "data": res.get("data"),
                "timestamp": res.get("timestamp", datetime.utcnow().isoformat()),
                "cached": False
            }
        except Exception as e:
            logger.error(f"Error MeteoBlue: {str(e)}")
            return {"error": str(e)}

    async def _fetch_meteoblue_meteogram(
        self,
        latitude: float,
        longitude: float,
        timeout: int
    ) -> Dict[str, Any]:
        """Descarga el meteograma y lo guarda en data/meteogram_medellin.png."""
        try:
            if not self.meteoblue_api_key:
                return {"error": "API key de MeteoBlue no configurada"}

            from data_sources.meteoblue import MeteoBlueSource
            import os
            save_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "meteogram_medellin.png")

            src = MeteoBlueSource(api_key=self.meteoblue_api_key)
            res = src.get_meteogram_image(
                latitude=latitude,
                longitude=longitude,
                asl=700,
                location_name="Medellín",
                tz="America/Bogota",
                dpi=72,
                lang="en",
                temperature_units="C",
                precipitation_units="mm",
                windspeed_units="kmh",
                format="png",
                save_path=save_path,
            )
            logger.info(f"✓ Meteograma guardado en {save_path}")
            return {
                "data": {"meteogram_path": save_path, "saved": res.get("saved", False)},
                "timestamp": res.get("timestamp", datetime.utcnow().isoformat()),
                "cached": False
            }
        except Exception as e:
            logger.warning(f"Meteograma no disponible: {str(e)}")
            return {"error": str(e)}
    
    async def _fetch_radar_ideam(
        self,
        latitude: float,
        longitude: float,
        timeout: int
    ) -> Dict[str, Any]:
        """Obtiene datos de Radar IDEAM."""
        try:
            from backend.app.services.ideam_radar import get_radar_data
            
            data = await asyncio.wait_for(
                get_radar_data(latitude, longitude),
                timeout=timeout
            )
            
            logger.info(f"✓ Datos obtenidos de Radar IDEAM para ({latitude}, {longitude})")
            return {
                "data": data,
                "timestamp": datetime.utcnow().isoformat(),
                "cached": False
            }
        except asyncio.TimeoutError:
            return {"error": "Timeout al obtener datos de IDEAM"}
        except Exception as e:
            logger.error(f"Error Radar IDEAM: {str(e)}")
            return {"error": str(e)}
    
    def get_active_sources(self) -> List[str]:
        """Retorna lista de fuentes activas."""
        return [name for name, source in self.sources.items() if source.active]
    
    def get_sources_status(self) -> Dict[str, Dict[str, Any]]:
        """Retorna estado de todas las fuentes."""
        status = {}
        for name, source in self.sources.items():
            status[name] = {
                "name": source.name,
                "icon": source.icon,
                "active": source.active,
                "has_data": source.data is not None,
                "error": source.error,
                "timestamp": source.timestamp,
                "cached": source.cached
            }
        return status
    
    def normalize_data(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Normaliza datos de todas las fuentes a un formato estándar.
        
        Returns:
            Diccionario con datos agregados y normalizados
        """
        aggregated = {
            "location": {"latitude": latitude, "longitude": longitude},
            "sources": [],
            "statistics": {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        temperatures = []
        humidities = []
        wind_speeds = []
        
        for name, source in self.sources.items():
            if source.data:
                source_data = {
                    "name": source.name,
                    "icon": source.icon,
                    "data": source.data,
                    "cached": source.cached,
                    "timestamp": source.timestamp
                }
                aggregated["sources"].append(source_data)
                
                # Extraer valores para estadísticas
                if isinstance(source.data, dict):
                    if "temperature" in source.data:
                        temperatures.append(source.data["temperature"])
                    if "humidity" in source.data:
                        humidities.append(source.data["humidity"])
                    if "wind_speed" in source.data:
                        wind_speeds.append(source.data["wind_speed"])
            elif source.error:
                aggregated["sources"].append({
                    "name": source.name,
                    "icon": source.icon,
                    "error": source.error,
                    "active": source.active
                })
        
        # Calcular estadísticas
        if temperatures:
            aggregated["statistics"]["temperature"] = {
                "average": round(sum(temperatures) / len(temperatures), 2),
                "min": min(temperatures),
                "max": max(temperatures),
                "sources": len(temperatures)
            }
        
        if humidities:
            aggregated["statistics"]["humidity"] = {
                "average": round(sum(humidities) / len(humidities), 2),
                "min": min(humidities),
                "max": max(humidities),
                "sources": len(humidities)
            }
        
        if wind_speeds:
            aggregated["statistics"]["wind_speed"] = {
                "average": round(sum(wind_speeds) / len(wind_speeds), 2),
                "min": min(wind_speeds),
                "max": max(wind_speeds),
                "sources": len(wind_speeds)
            }
        
        return aggregated
