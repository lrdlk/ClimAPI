"""
Backend FastAPI para Clima Dashboard

Este script:
1. Configura la API FastAPI con CORS
2. Define los endpoints para datos meteorológicos
3. Integra múltiples fuentes de datos
4. Proporciona documentación automática

ClimAPI - API de Datos Meteorológicos

Este módulo es el punto de entrada principal de la aplicación FastAPI que proporciona:
- Una API REST para consultar datos meteorológicos
- Integración con múltiples fuentes de datos
- Sistema de caché para mejorar el rendimiento
- Documentación automática con Swagger UI y ReDoc

Módulos principales:
- data_sources/: Fuentes de datos meteorológicos
- processing/: Procesamiento y transformación de datos
- backend/: Implementación de la API FastAPI
"""

import pandas as pd
import numpy as np
import requests
import json
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

from data_sources.open_meteo import get_weather_data, validate_coordinates
from processing.transform import process_weather_data
from processing.storage import save_to_csv, CacheManager

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicializar caché global
CACHE_TTL = int(os.getenv('CACHE_TTL_MINUTES', '15'))
CACHE_DIR = os.getenv('CACHE_DIR', 'cache')

cache_manager = CacheManager(ttl_minutes=CACHE_TTL)

# Crear directorios necesarios
Path(CACHE_DIR).mkdir(exist_ok=True)
Path("data").mkdir(exist_ok=True)

# Crear aplicación FastAPI
app = FastAPI(
    title="Clima Dashboard API",
    description="API para dashboard meteorológico con múltiples fuentes de datos",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic para respuestas
class WeatherData(BaseModel):
    time: str
    temperature: float
    humidity: float
    precipitation: float
    wind_speed: float

class LocationRequest(BaseModel):
    latitude: float
    longitude: float
    timezone: str = "America/Bogota"

class WeatherResponse(BaseModel):
    location: LocationRequest
    data: List[WeatherData]
    source: str
    timestamp: str

# Endpoints de la API
@app.get("/", tags=["root"])
async def root():
    return {"message": "Clima Dashboard API", "version": "1.0.0"}

@app.get("/api/v1/health", tags=["health"])
async def health_check():
    return {"status": "healthy", "service": "clima-dashboard-api"}

@app.post("/api/v1/weather/current", response_model=WeatherResponse, tags=["weather"])
async def get_current_weather(location: LocationRequest):
    """
    Obtiene datos meteorológicos actuales para una ubicación específica
    """
    try:
        # Validar coordenadas
        validate_coordinates(location.latitude, location.longitude)
        
        # Intentar obtener datos procesados de caché
        cached_df = cache_manager.get_processed_data(
            location.latitude, 
            location.longitude, 
            location.timezone
        )
        
        if cached_df is not None:
            print(" Usando datos desde caché")
            df = cached_df
            source = "Open-Meteo (Cached)"
        else:
            print(" Obteniendo datos frescos desde API")
            # Obtener datos de la API
            api_response = get_weather_data(
                latitude=location.latitude,
                longitude=location.longitude,
                timezone=location.timezone
            )
            
            # Procesar datos
            df = process_weather_data(api_response)
            
            # Guardar en caché
            cache_manager.set_processed_data(
                location.latitude, 
                location.longitude, 
                location.timezone, 
                df
            )
            source = "Open-Meteo"
        
        # Convertir a formato de respuesta
        weather_data = []
        for index, row in df.head(24).iterrows():  # Últimas 24 horas
            weather_data.append(WeatherData(
                time=index.isoformat(),
                temperature=row['temperatura_c'],
                humidity=row['humedad_porcentaje'],
                precipitation=row['precipitacion_mm'],
                wind_speed=row['velocidad_viento_kmh']
            ))
        
        return WeatherResponse(
            location=location,
            data=weather_data,
            source=source,
            timestamp=datetime.now().isoformat()
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener datos: {str(e)}")

@app.get("/api/v1/cache/stats", tags=["cache"])
async def get_cache_stats():
    """
    Obtiene estadísticas del sistema de caché
    """
    return cache_manager.get_stats()

@app.delete("/api/v1/cache", tags=["cache"])
async def clear_cache():
    """
    Limpia toda la caché
    """
    cache_manager.clear()
    return {"message": "Caché limpiada exitosamente"}

@app.get("/api/v1/locations/default", tags=["locations"])
async def get_default_location():
    """
    Retorna la ubicación por defecto (Medellín)
    """
    return {
        "latitude": 6.244,
        "longitude": -75.581,
        "timezone": "America/Bogota",
        "city": "Medellín",
        "country": "Colombia"
    }

def load_config(config_path: str = "config/settings.json") -> dict:
    """
    Carga la configuración desde un archivo JSON.
    
    Args:
        config_path: Ruta al archivo de configuración
    
    Returns:
        dict: Diccionario con la configuración
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"⚠️  Advertencia: No se encontró el archivo de configuración {config_path}")
        print("   Usando valores por defecto.")
        return {
            "location": {
                "latitude": 6.244,
                "longitude": -75.581,
                "timezone": "America/Bogota"
            },
            "data": {
                "output_directory": "data",
                "default_filename": "weather_data.csv"
            }
        }
    except json.JSONDecodeError as e:
        print(f"❌ Error al leer el archivo de configuración: {e}")
        sys.exit(1)


def main():
    """
    Función principal que orquesta todo el flujo del proyecto.
    """
    print("=" * 60)
    print("🌤️  Sistema de Consumo de Datos Meteorológicos")
    print("=" * 60)
    print()
    
    # 1. Cargar configuración
    print("📋 Paso 1: Cargando configuración...")
    config = load_config()
    location = config.get("location", {})
    data_config = config.get("data", {})
    
    latitude = location.get("latitude", 6.244)
    longitude = location.get("longitude", -75.581)
    timezone = location.get("timezone", "America/Bogota")
    output_dir = data_config.get("output_directory", "data")
    filename = data_config.get("default_filename", "weather_data.csv")
    
    print(f"   ✓ Ubicación: Lat {latitude}, Lon {longitude}")
    print(f"   ✓ Zona horaria: {timezone}")
    print()
    
    # 2. Validar coordenadas
    print("🔍 Paso 2: Validando coordenadas...")
    try:
        validate_coordinates(latitude, longitude)
        print("   ✓ Coordenadas válidas")
    except ValueError as e:
        print(f"   ❌ Error: {e}")
        sys.exit(1)
    print()
    
    # 3. Consumir datos de la API
    print("🌐 Paso 3: Consumiendo datos desde Open-Meteo API...")
    try:
        api_response = get_weather_data(
            latitude=latitude,
            longitude=longitude,
            timezone=timezone
        )
        print("   ✓ Datos obtenidos exitosamente")
        print(f"   ✓ Registros recibidos: {len(api_response.get('hourly', {}).get('time', []))}")
    except Exception as e:
        print(f"   ❌ Error al obtener datos: {e}")
        sys.exit(1)
    print()
    
    # 4. Procesar y transformar datos
    print("🔄 Paso 4: Procesando y transformando datos...")
    try:
        df = process_weather_data(api_response)
        print("   ✓ Datos procesados exitosamente")
        print(f"   ✓ Columnas: {', '.join(df.columns)}")
        print(f"   ✓ Registros procesados: {len(df)}")
        print(f"   ✓ Rango de fechas: {df.index.min()} a {df.index.max()}")
    except Exception as e:
        print(f"   ❌ Error al procesar datos: {e}")
        sys.exit(1)
    print()
    
    # 5. Guardar datos en CSV
    print("💾 Paso 5: Guardando datos en CSV...")
    try:
        output_path = Path(output_dir) / filename
        saved_path = save_to_csv(df, str(output_path))
        print(f"   ✓ Datos guardados en: {saved_path}")
        print(f"   ✓ Tamaño del archivo: {Path(saved_path).stat().st_size / 1024:.2f} KB")
    except Exception as e:
        print(f"   ❌ Error al guardar datos: {e}")
        sys.exit(1)
    print()
    
    # 6. Resumen final
    print("=" * 60)
    print("✅ Proceso completado exitosamente!")
    print("=" * 60)
    print()
    print("📊 Resumen de los datos:")
    print(f"   • Temperatura promedio: {df['temperatura_c'].mean():.2f} °C")
    print(f"   • Humedad promedio: {df['humedad_porcentaje'].mean():.2f} %")
    print(f"   • Precipitación total: {df['precipitacion_mm'].sum():.2f} mm")
    print(f"   • Velocidad del viento promedio: {df['velocidad_viento_kmh'].mean():.2f} km/h")
    print()
    print("🚀 Para ver el dashboard, ejecuta:")
    print("   streamlit run dashboard/app.py")
    print()


if __name__ == "__main__":
    import uvicorn
    import os
    import sys
    
    # Verificar si se debe ejecutar como API FastAPI o como script original
    if len(sys.argv) > 1 and sys.argv[1] == "api":
        # Ejecutar como servidor FastAPI
        print("🚀 Iniciando servidor FastAPI...")
        print("📖 Documentación disponible en: http://localhost:8000/docs")
        uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
    else:
        # Ejecutar script original
        main()