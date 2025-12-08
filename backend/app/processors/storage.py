"""
Almacenamiento de datos meteorológicos en CSV, JSON y cache.
"""
import csv
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Directorios
DATA_DIR = Path("data")
CACHE_DIR = Path("cache")


def save_to_csv(data: Dict[str, Any], location_name: str) -> Path:
    """
    Guarda datos meteorológicos en archivo CSV.
    
    Args:
        data: Datos procesados a guardar
        location_name: Nombre de la ubicación (sin espacios)
    
    Returns:
        Path del archivo creado
    
    Raises:
        IOError: Si hay error al escribir el archivo
    """
    try:
        # Crear directorio si no existe
        DATA_DIR.mkdir(exist_ok=True, parents=True)
        
        # Sanitizar nombre de ubicación
        safe_name = location_name.replace(" ", "_").replace("/", "_").lower()
        
        # Nombre de archivo con timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = DATA_DIR / f"weather_{safe_name}_{timestamp}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Escribir encabezados
            writer.writerow(['Campo', 'Valor'])
            
            # Escribir datos principales (no anidados)
            for key, value in data.items():
                if not isinstance(value, (dict, list)):
                    writer.writerow([key, value])
            
            # Escribir ubicación si existe
            if "location" in data and isinstance(data["location"], dict):
                writer.writerow(['--- Ubicación ---', ''])
                for key, value in data["location"].items():
                    writer.writerow([f"location_{key}", value])
        
        logger.info(f"✓ CSV guardado: {filename}")
        return filename
        
    except IOError as e:
        logger.error(f"❌ Error IO al guardar CSV: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"❌ Error inesperado al guardar CSV: {str(e)}")
        raise


def save_to_json(data: Dict[str, Any], location_name: str) -> Path:
    """
    Guarda datos meteorológicos en formato JSON.
    
    Args:
        data: Datos a guardar
        location_name: Nombre de la ubicación
    
    Returns:
        Path del archivo creado
    """
    try:
        DATA_DIR.mkdir(exist_ok=True, parents=True)
        
        safe_name = location_name.replace(" ", "_").replace("/", "_").lower()
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = DATA_DIR / f"weather_{safe_name}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✓ JSON guardado: {filename}")
        return filename
        
    except Exception as e:
        logger.error(f"❌ Error al guardar JSON: {str(e)}")
        raise


class CacheManager:
    """
    Gestor de caché en memoria para datos meteorológicos.
    Implementa TTL (Time To Live) y límite de tamaño.
    """
    
    def __init__(self, cache_dir: str = "cache", ttl_minutes: int = 15):
        """
        Inicializa el gestor de caché.
        
        Args:
            cache_dir: Directorio para archivos de caché
            ttl_minutes: Tiempo de vida en minutos
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True, parents=True)
        self.ttl_seconds = ttl_minutes * 60
        self._cache: Dict[str, tuple] = {}  # key: (value, timestamp)
        self._max_size = 100
        
        logger.debug(f"CacheManager inicializado: TTL={ttl_minutes}m, MAX_SIZE={self._max_size}")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Obtiene valor de caché si existe y no ha expirado.
        
        Args:
            key: Clave de caché
        
        Returns:
            Valor almacenado o None si no existe/expiró
        """
        if key not in self._cache:
            logger.debug(f"Cache miss: {key}")
            return None
        
        value, timestamp = self._cache[key]
        
        # Verificar si expiró
        age = datetime.utcnow() - timestamp
        if age.total_seconds() > self.ttl_seconds:
            logger.debug(f"Cache expirado: {key} (edad: {age.total_seconds():.0f}s)")
            del self._cache[key]
            return None
        
        logger.debug(f"Cache hit: {key}")
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Almacena valor en caché.
        
        Args:
            key: Clave de caché
            value: Valor a almacenar
        """
        # Limpiar si alcanzó el límite
        if len(self._cache) >= self._max_size:
            self._evict_oldest()
        
        self._cache[key] = (value, datetime.utcnow())
        logger.debug(f"Cache set: {key} (size: {len(self._cache)}/{self._max_size})")
    
    def clear(self) -> None:
        """Limpia todo el caché."""
        count = len(self._cache)
        self._cache.clear()
        logger.info(f"✓ Caché limpiado ({count} items)")
    
    def size(self) -> int:
        """Retorna número de elementos en caché."""
        return len(self._cache)
    
    @property
    def max_size(self) -> int:
        """Tamaño máximo del caché."""
        return self._max_size
    
    def _evict_oldest(self) -> None:
        """Elimina el elemento más antiguo (LRU)."""
        if not self._cache:
            return
        
        oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][1])
        del self._cache[oldest_key]
        logger.debug(f"Cache evicted (LRU): {oldest_key}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del caché.
        
        Returns:
            Diccionario con estadísticas
        """
        return {
            "size": self.size(),
            "max_size": self.max_size,
            "ttl_seconds": self.ttl_seconds,
            "cache_dir": str(self.cache_dir),
            "utilization": f"{(self.size()/self.max_size)*100:.1f}%"
        }