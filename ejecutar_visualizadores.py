"""
Ejecutar Todos los Visualizadores
==================================

Script para ejecutar todos los visualizadores de forma secuencial
y generar un reporte completo de los datos.
"""

import sys
from pathlib import Path
from datetime import datetime

# Agregar directorio raíz al path
sys.path.append(str(Path(__file__).parent))

# Importar visualizadores
from src.visualizers.meteoblue_visualizer import MeteoblueVisualizer
from src.visualizers.open_meteo_visualizer import OpenMeteoVisualizer
from src.visualizers.openweather_visualizer import OpenWeatherVisualizer
from src.visualizers.meteosource_visualizer import MeteosourceVisualizer
from src.visualizers.ideam_visualizer import IDEAMRadarVisualizer
from src.visualizers.siata_visualizer import SIATAVisualizer


def crear_directorios():
    """Crea directorios necesarios"""
    dirs = [
        "data/images",
        "data/images_meteo_blue",
        "data/processed"
    ]
    
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)


def ejecutar_meteoblue():
    """Ejecuta visualizador de Meteoblue"""
    print("\n" + "="*80)
    print("☁️  PROCESANDO METEOBLUE")
    print("="*80)
    
    try:
        viz = MeteoblueVisualizer()
        df = viz.cargar_datos()
        
        if df is not None:
            viz.estadisticas_basicas()
            viz.grafico_series_temporales(save_path="data/images_meteo_blue/series_temporales.png")
            viz.analisis_correlacion(save_path="data/images_meteo_blue/correlacion.png")
            viz.clustering_ciudades(save_path="data/images_meteo_blue/clustering.png")
            viz.detectar_outliers()
            viz.exportar_procesado()
            print("\n✅ Meteoblue completado")
            return True
        else:
            print("\n⚠️ No hay datos de Meteoblue")
            return False
    except Exception as e:
        print(f"\n❌ Error en Meteoblue: {e}")
        return False


def ejecutar_open_meteo():
    """Ejecuta visualizador de Open-Meteo"""
    print("\n" + "="*80)
    print("🌐 PROCESANDO OPEN-METEO")
    print("="*80)
    
    try:
        viz = OpenMeteoVisualizer()
        viz.cargar_datos()
        
        if viz.df_daily is not None or viz.df_hourly is not None:
            viz.estadisticas_basicas()
            viz.grafico_temperatura_horaria(save_path="data/images/openmeteo_temp_horaria.png")
            viz.comparacion_ciudades(save_path="data/images/openmeteo_comparacion.png")
            viz.prediccion_temperatura()
            viz.exportar_procesado()
            print("\n✅ Open-Meteo completado")
            return True
        else:
            print("\n⚠️ No hay datos de Open-Meteo")
            return False
    except Exception as e:
        print(f"\n❌ Error en Open-Meteo: {e}")
        return False


def ejecutar_openweather():
    """Ejecuta visualizador de OpenWeatherMap"""
    print("\n" + "="*80)
    print("🌤️  PROCESANDO OPENWEATHERMAP")
    print("="*80)
    
    try:
        viz = OpenWeatherVisualizer()
        df = viz.cargar_datos()
        
        if df is not None:
            viz.estadisticas_basicas()
            viz.grafico_temperatura_feels_like(save_path="data/images/openweather_feels_like.png")
            viz.analisis_viento(save_path="data/images/openweather_viento.png")
            viz.tendencia_temperatura(save_path="data/images/openweather_tendencia.png")
            viz.exportar_procesado()
            print("\n✅ OpenWeatherMap completado")
            return True
        else:
            print("\n⚠️ No hay datos de OpenWeatherMap")
            return False
    except Exception as e:
        print(f"\n❌ Error en OpenWeatherMap: {e}")
        return False


def ejecutar_meteosource():
    """Ejecuta visualizador de Meteosource"""
    print("\n" + "="*80)
    print("🌦️  PROCESANDO METEOSOURCE")
    print("="*80)
    
    try:
        viz = MeteosourceVisualizer()
        df = viz.cargar_datos()
        
        if df is not None:
            viz.estadisticas_basicas()
            viz.grafico_uv_index(save_path="data/images/meteosource_uv.png")
            viz.analisis_visibilidad(save_path="data/images/meteosource_visibilidad.png")
            viz.pca_analysis(save_path="data/images/meteosource_pca.png")
            viz.exportar_procesado()
            print("\n✅ Meteosource completado")
            return True
        else:
            print("\n⚠️ No hay datos de Meteosource")
            return False
    except Exception as e:
        print(f"\n❌ Error en Meteosource: {e}")
        return False


def ejecutar_ideam():
    """Ejecuta visualizador de IDEAM Radar"""
    print("\n" + "="*80)
    print("📡 PROCESANDO IDEAM RADAR")
    print("="*80)
    
    try:
        viz = IDEAMRadarVisualizer()
        radares = viz.listar_radares()
        
        if radares:
            # Procesar primer radar disponible
            radar = radares[0]
            viz.cargar_imagenes_radar(radar)
            
            if viz.metadata:
                viz.estadisticas_basicas()
                viz.visualizar_galeria(save_path=f"data/images/ideam_galeria_{radar}.png")
                viz.analisis_intensidad()
                viz.timeline_imagenes(save_path=f"data/images/ideam_timeline_{radar}.png")
                viz.exportar_metadata()
                print("\n✅ IDEAM Radar completado")
                return True
            else:
                print("\n⚠️ No hay imágenes de IDEAM")
                return False
        else:
            print("\n⚠️ No hay radares disponibles")
            return False
    except Exception as e:
        print(f"\n❌ Error en IDEAM: {e}")
        return False


def ejecutar_siata():
    """Ejecuta visualizador de SIATA"""
    print("\n" + "="*80)
    print("🌐 PROCESANDO SIATA")
    print("="*80)
    
    try:
        viz = SIATAVisualizer()
        df = viz.cargar_datos()
        
        if df is not None:
            viz.estadisticas_basicas()
            viz.grafico_series_temporales(save_path="data/images/siata_series.png")
            viz.analisis_outliers()
            viz.comparacion_estaciones(save_path="data/images/siata_comparacion.png")
            viz.matriz_correlacion(save_path="data/images/siata_correlacion.png")
            viz.exportar_procesado()
            print("\n✅ SIATA completado")
            return True
        else:
            print("\n⚠️ No hay datos de SIATA")
            return False
    except Exception as e:
        print(f"\n❌ Error en SIATA: {e}")
        return False


def generar_reporte(resultados):
    """Genera reporte de ejecución"""
    print("\n" + "="*80)
    print("📊 REPORTE DE EJECUCIÓN")
    print("="*80)
    
    total = len(resultados)
    exitosos = sum(resultados.values())
    fallidos = total - exitosos
    
    print(f"\n✅ Exitosos: {exitosos}/{total}")
    print(f"❌ Fallidos: {fallidos}/{total}")
    
    print("\n📋 Detalle:")
    for api, exito in resultados.items():
        estado = "✅" if exito else "❌"
        print(f"  {estado} {api}")
    
    print("\n" + "="*80)
    print(f"📁 Archivos generados en:")
    print("  - data/images/")
    print("  - data/images_meteo_blue/")
    print("  - data/processed/")
    print("="*80)
    
    # Guardar reporte en archivo
    reporte_path = Path(f"data/reporte_visualizadores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    reporte_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(reporte_path, 'w', encoding='utf-8') as f:
        f.write("REPORTE DE EJECUCIÓN - VISUALIZADORES CLIMAPI\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"Total APIs: {total}\n")
        f.write(f"Exitosos: {exitosos}\n")
        f.write(f"Fallidos: {fallidos}\n\n")
        f.write("Detalle:\n")
        for api, exito in resultados.items():
            estado = "EXITOSO" if exito else "FALLIDO"
            f.write(f"  - {api}: {estado}\n")
    
    print(f"\n💾 Reporte guardado en: {reporte_path}")


def main():
    """Función principal"""
    print("\n" + "🌦️ "*20)
    print("CLIMAPI - EJECUCIÓN DE TODOS LOS VISUALIZADORES")
    print("🌦️ "*20)
    print(f"\nInicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Crear directorios
    crear_directorios()
    
    # Ejecutar visualizadores
    resultados = {
        "Meteoblue": ejecutar_meteoblue(),
        "Open-Meteo": ejecutar_open_meteo(),
        "OpenWeatherMap": ejecutar_openweather(),
        "Meteosource": ejecutar_meteosource(),
        "IDEAM Radar": ejecutar_ideam(),
        "SIATA": ejecutar_siata()
    }
    
    # Generar reporte
    generar_reporte(resultados)
    
    print(f"\nFin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n✨ Proceso completado ✨\n")


if __name__ == "__main__":
    main()
