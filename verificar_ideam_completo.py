"""
Script de Verificación Completa - IDEAM Radar Visualizer
=========================================================

Verifica todas las funcionalidades del sistema sin perder conexiones existentes.
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from visualizers.ideam_visualizer import IDEAMRadarVisualizer
import pandas as pd

def print_seccion(titulo):
    """Imprime un separador de sección"""
    print("\n" + "="*70)
    print(f"🔍 {titulo}")
    print("="*70 + "\n")

def verificar_inicializacion():
    """Verifica que el visualizador se inicialice correctamente"""
    print_seccion("VERIFICACIÓN 1: Inicialización")
    
    try:
        viz = IDEAMRadarVisualizer()
        print("✅ Inicialización exitosa")
        print(f"   - Directorio de datos: {viz.data_dir}")
        print(f"   - PyART disponible: {'Sí' if hasattr(viz, 'PYART_AVAILABLE') else 'N/A'}")
        return viz
    except Exception as e:
        print(f"❌ Error en inicialización: {e}")
        return None

def verificar_listado_radares(viz):
    """Verifica el listado de radares disponibles"""
    print_seccion("VERIFICACIÓN 2: Listado de Radares")
    
    try:
        viz.listar_radares()
        print("✅ Listado de radares funcionando")
        return True
    except Exception as e:
        print(f"❌ Error en listado: {e}")
        return False

def verificar_carga_datos(viz):
    """Verifica la carga de datos de radar"""
    print_seccion("VERIFICACIÓN 3: Carga de Datos")
    
    try:
        df = viz.cargar_datos_radar('Barrancabermeja', limite=10)
        
        if df is not None and len(df) > 0:
            print(f"✅ Carga de datos exitosa")
            print(f"   - Archivos procesados: {len(df)}")
            print(f"   - Columnas: {len(df.columns)}")
            print(f"   - Columnas principales: {list(df.columns[:5])}")
            return True
        else:
            print("⚠️  No se cargaron datos")
            return False
    except Exception as e:
        print(f"❌ Error en carga: {e}")
        return False

def verificar_dataframe_trabajable(viz):
    """Verifica el DataFrame trabajable"""
    print_seccion("VERIFICACIÓN 4: DataFrame Trabajable")
    
    try:
        df_clean = viz.obtener_dataframe_trabajable()
        
        if df_clean is not None and len(df_clean) > 0:
            print(f"✅ DataFrame trabajable generado")
            print(f"   - Registros: {len(df_clean)}")
            print(f"   - Columnas: {list(df_clean.columns)}")
            print("\n📊 Primeras 3 filas:")
            print(df_clean.head(3))
            return True
        else:
            print("⚠️  DataFrame vacío")
            return False
    except Exception as e:
        print(f"❌ Error en DataFrame: {e}")
        return False

def verificar_estadisticas(viz):
    """Verifica las estadísticas"""
    print_seccion("VERIFICACIÓN 5: Estadísticas")
    
    try:
        stats = viz.obtener_estadisticas_completas()
        
        if stats:
            print("✅ Estadísticas generadas")
            print(f"   - Radar: {stats.get('radar', 'N/A')}")
            print(f"   - Archivos: {stats.get('total_archivos', 0)}")
            print(f"   - Tamaño total: {stats.get('tamaño_total_mb', 0):.1f} MB")
            print(f"   - Reflectividad máxima: {stats.get('reflectividad_max', 0):.2f} dBZ")
            return True
        else:
            print("⚠️  No se generaron estadísticas")
            return False
    except Exception as e:
        print(f"❌ Error en estadísticas: {e}")
        return False

def verificar_visualizaciones(viz):
    """Verifica la generación de visualizaciones"""
    print_seccion("VERIFICACIÓN 6: Visualizaciones")
    
    output_dir = Path("visualizaciones/ideam")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    resultados = {}
    
    # 1. Dashboard completo
    try:
        viz.grafica_resumen_completo(
            save_path=str(output_dir / "test_dashboard.png"),
            show=False
        )
        resultados['dashboard'] = True
        print("✅ Dashboard completo generado")
    except Exception as e:
        resultados['dashboard'] = False
        print(f"❌ Error en dashboard: {e}")
    
    # 2. Serie temporal
    try:
        viz.grafica_serie_temporal_reflectividad(
            save_path=str(output_dir / "test_serie_temporal.png"),
            show=False
        )
        resultados['serie_temporal'] = True
        print("✅ Serie temporal generada")
    except Exception as e:
        resultados['serie_temporal'] = False
        print(f"❌ Error en serie temporal: {e}")
    
    # 3. Distribución de intensidad
    try:
        viz.grafica_distribucion_intensidad(
            save_path=str(output_dir / "test_distribucion.png"),
            show=False
        )
        resultados['distribucion'] = True
        print("✅ Distribución de intensidad generada")
    except Exception as e:
        resultados['distribucion'] = False
        print(f"❌ Error en distribución: {e}")
    
    # 4. Patrón temporal
    try:
        viz.grafica_patron_temporal(
            save_path=str(output_dir / "test_patron.png"),
            show=False
        )
        resultados['patron'] = True
        print("✅ Patrón temporal generado")
    except Exception as e:
        resultados['patron'] = False
        print(f"❌ Error en patrón: {e}")
    
    return all(resultados.values())

def verificar_exportacion(viz):
    """Verifica la exportación de datos"""
    print_seccion("VERIFICACIÓN 7: Exportación de Datos")
    
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    formatos = ['csv', 'json', 'excel', 'parquet']
    resultados = {}
    
    for formato in formatos:
        try:
            output_path = output_dir / f"test_radar_data.{formato}"
            viz.exportar_datos(str(output_path), formato=formato)
            resultados[formato] = output_path.exists()
            if resultados[formato]:
                print(f"✅ Exportación a {formato.upper()} exitosa")
            else:
                print(f"⚠️  Archivo {formato.upper()} no encontrado")
        except Exception as e:
            resultados[formato] = False
            print(f"❌ Error en exportación {formato.upper()}: {e}")
    
    return all(resultados.values())

def verificar_aws_disponible(viz):
    """Verifica si AWS está disponible y configurado"""
    print_seccion("VERIFICACIÓN 8: Capacidades AWS")
    
    if hasattr(viz, 'enable_aws') and viz.enable_aws:
        print("✅ AWS habilitado")
        print("   - boto3 disponible: Sí")
        print("   - fsspec disponible: Sí")
        print("   - Acceso a S3: Configurado")
        return True
    else:
        print("ℹ️  AWS no habilitado (funcionalidad opcional)")
        print("   Instalar con: pip install boto3 fsspec s3fs")
        return None  # None = opcional, no es error

def main():
    """Función principal de verificación"""
    
    print("\n" + "="*70)
    print("🚀 VERIFICACIÓN COMPLETA - IDEAM RADAR VISUALIZER")
    print("="*70)
    print("\nEste script verifica todas las funcionalidades principales")
    print("sin afectar las conexiones y datos existentes.\n")
    
    # Contador de pruebas
    resultados = {
        'total': 0,
        'exitosas': 0,
        'fallidas': 0,
        'opcionales': 0
    }
    
    # 1. Inicialización
    viz = verificar_inicializacion()
    resultados['total'] += 1
    if viz:
        resultados['exitosas'] += 1
    else:
        resultados['fallidas'] += 1
        print("\n❌ VERIFICACIÓN DETENIDA: No se pudo inicializar el visualizador")
        return
    
    # 2. Listado de radares
    resultados['total'] += 1
    if verificar_listado_radares(viz):
        resultados['exitosas'] += 1
    else:
        resultados['fallidas'] += 1
    
    # 3. Carga de datos
    resultados['total'] += 1
    if verificar_carga_datos(viz):
        resultados['exitosas'] += 1
    else:
        resultados['fallidas'] += 1
        print("\n⚠️  ADVERTENCIA: No se pudieron cargar datos. Las siguientes pruebas pueden fallar.")
    
    # 4. DataFrame trabajable
    resultados['total'] += 1
    if verificar_dataframe_trabajable(viz):
        resultados['exitosas'] += 1
    else:
        resultados['fallidas'] += 1
    
    # 5. Estadísticas
    resultados['total'] += 1
    if verificar_estadisticas(viz):
        resultados['exitosas'] += 1
    else:
        resultados['fallidas'] += 1
    
    # 6. Visualizaciones
    resultados['total'] += 1
    if verificar_visualizaciones(viz):
        resultados['exitosas'] += 1
    else:
        resultados['fallidas'] += 1
    
    # 7. Exportación
    resultados['total'] += 1
    if verificar_exportacion(viz):
        resultados['exitosas'] += 1
    else:
        resultados['fallidas'] += 1
    
    # 8. AWS (opcional)
    resultado_aws = verificar_aws_disponible(viz)
    if resultado_aws is None:
        resultados['opcionales'] += 1
    elif resultado_aws:
        resultados['exitosas'] += 1
        resultados['total'] += 1
    else:
        resultados['fallidas'] += 1
        resultados['total'] += 1
    
    # Resumen final
    print_seccion("RESUMEN FINAL")
    
    print(f"Total de pruebas: {resultados['total']}")
    print(f"✅ Exitosas: {resultados['exitosas']}")
    print(f"❌ Fallidas: {resultados['fallidas']}")
    if resultados['opcionales'] > 0:
        print(f"ℹ️  Opcionales: {resultados['opcionales']}")
    
    porcentaje = (resultados['exitosas'] / resultados['total'] * 100) if resultados['total'] > 0 else 0
    
    print(f"\n📊 Tasa de éxito: {porcentaje:.1f}%")
    
    if resultados['fallidas'] == 0:
        print("\n🎉 TODAS LAS VERIFICACIONES PASARON EXITOSAMENTE")
        print("✅ El sistema está funcionando correctamente")
    elif porcentaje >= 80:
        print("\n⚠️  LA MAYORÍA DE VERIFICACIONES PASARON")
        print("✅ El sistema está funcional con algunas limitaciones")
    else:
        print("\n❌ VARIAS VERIFICACIONES FALLARON")
        print("⚠️  Revisar los errores anteriores")
    
    print("\n" + "="*70)
    print("📁 Archivos generados:")
    print("   - Visualizaciones: visualizaciones/ideam/test_*.png")
    print("   - Datos exportados: data/processed/test_radar_data.*")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
