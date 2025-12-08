"""
Procesadores de datos meteorológicos.
"""
from .cache_manager import CacheManager, get_cache, set_cache
from .data_processor import extract_temp_and_humidity, aggregate_sources

__all__ = [
    "CacheManager",
    "get_cache",
    "set_cache",
    "extract_temp_and_humidity",
    "aggregate_sources"
]