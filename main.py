"""
Script principal para orquestar el flujo completo del proyecto.

Este script:
1. Consume datos desde la API de Open-Meteo
2. Procesa y transforma los datos
3. Guarda los datos en CSV
4. Opcionalmente, inicia el dashboard
"""

import json
import sys
from pathlib import Path

# Agregar el directorio raíz al path para importar módulos
sys.path.append(str(Path(__file__).parent))

from data_sources.open_meteo import get_weather_data, validate_coordinates
from processing.transform import process_weather_data
from processing.storage import save_to_csv


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
    main()

