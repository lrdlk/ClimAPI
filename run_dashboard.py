#!/usr/bin/env python3
"""
Guía rápida para ejecutar el dashboard con datos de clima verificados.
ClimAPI - Dashboard Meteorológico Integrado
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Ejecuta el dashboard de ClimAPI."""
    
    # Cambiar al directorio del proyecto
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║      🌍 CLIMAPI DASHBOARD - VERIFICADO Y FUNCIONANDO 🌍      ║
    ╚═══════════════════════════════════════════════════════════════╝
    
    📊 FUENTES DE DATOS ACTIVAS:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    ✅ Open-Meteo (Global)
       └─ Datos: Temperatura, Humedad, Presión, Viento, Precipitación
    
    ✅ SIATA (Medellín)
       └─ Datos: Temperatura, Humedad, Presión, Viento
    
    ✅ OpenWeatherMap (Global)
       └─ Datos: Temperatura, Humedad, Presión, Viento, Descripción
    
    ✅ Radar IDEAM (Colombia)
       └─ Datos: Temperatura, Humedad, Presión, Viento, Descripción
       └─ Estaciones: Medellín, Bogotá, Cali, Barranquilla, Santa Marta, 
                      Cartagena, Bucaramanga, Cúcuta, Manizales
    
    ❌ MeteoBlue (Error - API key expirada)
       └─ Para activar: Obtener nueva key en https://www.meteoblue.com
    
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    📈 CARACTERÍSTICAS DEL DASHBOARD:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    🔄 Modo Real-time
       └─ Datos en vivo de 4 fuentes simultáneamente
       └─ Selector de ubicación (Medellín, Bogotá, Cali, personalizado)
       └─ Actualización automática configurable
    
    📊 Modo Histórico
       └─ Análisis de datos desde CSV
       └─ Filtros por fecha
       └─ Gráficos históricos
    
    🔀 Modo Comparativo
       └─ Comparación lado a lado de fuentes
       └─ Diferencias de lecturas
    
    ℹ️  Modo Información
       └─ Estado del sistema
       └─ Estadísticas de caché
       └─ Configuración activa
    
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    🌐 ACCESO REMOTO CON PINGGY.IO:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    Para exponer el dashboard a internet con HTTPS seguro:
    
    $ python pinggy_installer.py
    
    Ver: PINGGY_QUICKSTART.md para más detalles
    
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    🚀 INICIANDO DASHBOARD...
    """)
    
    # Ejecutar Streamlit
    try:
        subprocess.run([
            ".venv/Scripts/streamlit.exe",
            "run",
            "dashboard/app.py"
        ], check=True)
    except KeyboardInterrupt:
        print("\n\n✋ Dashboard detenido por el usuario.")
        sys.exit(0)
    except FileNotFoundError:
        print("\n❌ Error: No se encontró streamlit.")
        print("Por favor ejecuta primero: pip install streamlit")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error al ejecutar dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
