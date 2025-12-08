"""
Configuración centralizada - ClimAPI
Lee desde .env y proporciona valores por defecto.
"""
from pydantic_settings import BaseSettings
from typing import List, Union
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Ruta del archivo .env
ENV_FILE = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    """Configuración de ClimAPI."""
    
    # API Keys (con valores por defecto vacíos)
    OPENWEATHER_API_KEY: str = ""
    METEOSOURCE_API_KEY: str = ""
    METEOBLUE_API_KEY: str = ""
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # CORS - Soporta string separado por comas o lista
    ALLOWED_ORIGINS: Union[str, List[str]] = "http://localhost:3000,http://localhost:3001"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    DEBUG_MODE: bool = False
    
    # Cache
    CACHE_TTL_MINUTES: int = 15
    CACHE_DIR: str = "cache"
    CACHE_TTL: int = 900  # segundos (15 min)
    
    class Config:
        env_file = str(ENV_FILE) if ENV_FILE.exists() else None
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    def __init__(self, **kwargs):
        """Inicializa configuración."""
        super().__init__(**kwargs)
        
        # Convertir ALLOWED_ORIGINS a lista si es string
        if isinstance(self.ALLOWED_ORIGINS, str):
            self.ALLOWED_ORIGINS = [
                origin.strip() 
                for origin in self.ALLOWED_ORIGINS.split(",")
                if origin.strip()
            ]
        
        logger.info(f"✓ Configuración cargada: {len(self.ALLOWED_ORIGINS)} orígenes CORS")


# Instancia global de settings
try:
    settings = Settings()
except Exception as e:
    logger.warning(f"⚠️ Error al cargar .env: {e}. Usando valores por defecto.")
    settings = Settings()