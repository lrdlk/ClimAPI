"""
Almacenamiento de datos meteorológicos.
Migrado desde processing/storage.py
"""
import csv
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def save_to_csv(data: Dict[str, Any], location_name: str) -> None:
    """
    Guarda datos meteorológicos en archivo CSV.
    
    Args:
        data: Datos procesados a guardar
        location_name: Nombre de la ubicación
    """
    # Crear directorio data si no existe
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Nombre de archivo con timestamp
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = data_dir / f"weather_{location_name}_{timestamp}.csv"
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Escribir encabezados
            writer.writerow(['Campo', 'Valor'])
            
            # Escribir datos
            for key, value in data.items():
                if not isinstance(value, dict):
                    writer.writerow([key, value])
        
        logger.info(f"✓ Datos guardados en {filename}")
    except Exception as e:
        logger.error(f"❌ Error al guardar CSV: {str(e)}")
        raise

class CacheManager:
    """Gestor de caché para datos meteorológicos."""
    
    def __init__(self, cache_dir: str = "cache", ttl_minutes: int = 15):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl_seconds = ttl_minutes * 60
        self._cache = {}
    
    def get(self, key: str) -> Any:
        """Obtiene valor de caché."""
        return self._cache.get(key)
    
    def set(self, key: str, value: Any, ttl_seconds: int = None) -> None:
        """Almacena valor en caché."""
        self._cache[key] = value
    
    def clear(self) -> None:
        """Limpia el caché."""
        self._cache.clear()
    
    def size(self) -> int:
        """Retorna tamaño del caché."""
        return len(self._cache)
    
    @property
    def max_size(self) -> int:
        """Tamaño máximo del caché."""
        return 100