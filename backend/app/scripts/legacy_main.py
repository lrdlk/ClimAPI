"""
Script legacy - CLI para obtener datos meteorológicos.
Preserva funcionalidad original para uso por consola.
"""
import logging
import asyncio
from pathlib import Path
import sys

# Configurar path correctamente
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.services.open_meteo import get_weather_data
from backend.app.processors.transform import process_weather_data
from backend.app.processors.storage import save_to_csv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def fetch_and_process(location: dict) -> None:
    """
    Obtiene y procesa datos meteorológicos para una ubicación.
    
    Args:
        location: Diccionario con name, latitude, longitude
    """
    try:
        logger.info(f"📡 Obteniendo datos para {location['name']}...")
        
        # 1. Obtener datos de Open-Meteo
        weather_data = await get_weather_data(
            location['latitude'],
            location['longitude']
        )
        
        # 2. Procesar datos
        processed = process_weather_data(weather_data)
        
        # 3. Guardar en CSV
        save_to_csv(processed, location['name'])
        
        # 4. Mostrar resumen
        print("\n" + "="*60)
        print(f"📍 Ubicación: {location['name']}")
        print(f"🌡️  Temperatura: {processed.get('temperature', 'N/A')}°C")
        print(f"💨 Viento: {processed.get('wind_speed', 'N/A')} m/s")
        print(f"🧭 Dirección: {processed.get('wind_direction', 'N/A')}°")
        print(f"📅 Timestamp: {processed.get('timestamp', 'N/A')}")
        print("="*60 + "\n")
        
        logger.info("✓ Proceso completado exitosamente")
        
    except Exception as e:
        logger.error(f"❌ Error procesando {location['name']}: {str(e)}")
        raise


def main():
    """Función principal del script legacy."""
    print("\n" + "="*60)
    print("  ClimAPI Legacy Script v1.0.0")
    print("  Obtención de datos meteorológicos CLI")
    print("="*60 + "\n")
    
    # Ubicaciones por defecto
    locations = [
        {"name": "Medellin", "latitude": 6.2442, "longitude": -75.5812},
        {"name": "Bogota", "latitude": 4.7110, "longitude": -74.0721},
        {"name": "Cali", "latitude": 3.4372, "longitude": -76.5225}
    ]
    
    # Ejecutar para cada ubicación
    success_count = 0
    total = len(locations)
    
    for idx, location in enumerate(locations, 1):
        print(f"\n[{idx}/{total}] Procesando {location['name']}...")
        try:
            asyncio.run(fetch_and_process(location))
            success_count += 1
        except KeyboardInterrupt:
            logger.warning("⚠️ Proceso interrumpido por el usuario")
            sys.exit(0)
        except Exception as e:
            logger.error(f"❌ Error en {location['name']}: {str(e)}")
            continue
    
    # Resumen final
    print("\n" + "="*60)
    print(f"📊 Resumen: {success_count}/{total} ubicaciones procesadas")
    print("="*60 + "\n")
    
    if success_count == 0:
        logger.error("❌ No se pudo procesar ninguna ubicación")
        sys.exit(1)


if __name__ == "__main__":
    main()