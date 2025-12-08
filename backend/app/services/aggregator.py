"""
Agregador de datos meteorológicos de múltiples fuentes.
Integra: Open-Meteo, SIATA, OpenWeatherMap, MeteoBlue, Radar IDEAM, etc.
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass

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
                active=False,  # Requiere API key
                priority=3
            ),
            "meteoblue": WeatherSource(
                name="MeteoBlue",
                icon="🎯",
                active=False,  # Requiere API key
                priority=4
            ),
            "radar_ideam": WeatherSource(
                name="Radar IDEAM",
                icon="📡",
                active=False,  # Datos limitados
                priority=5
            ),
        }
    
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
        return {"error": "API key no configurada"}
    
    async def _fetch_meteoblue(
        self,
        latitude: float,
        longitude: float,
        timeout: int
    ) -> Dict[str, Any]:
        """Obtiene datos de MeteoBlue."""
        return {"error": "API key no configurada"}
    
    async def _fetch_radar_ideam(
        self,
        latitude: float,
        longitude: float,
        timeout: int
    ) -> Dict[str, Any]:
        """Obtiene datos de Radar IDEAM."""
        return {"error": "Datos limitados en esta fase"}
    
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
