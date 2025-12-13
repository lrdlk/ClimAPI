"""
Script de prueba para el visualizador IDEAM optimizado
"""

from pathlib import Path
import sys

# Agregar directorio raíz al path
raiz = Path(__file__).parent.parent
sys.path.insert(0, str(raiz))

# Importar
import importlib.util
spec = importlib.util.spec_from_file_location("ideam_visualizer", 
                                               raiz / "src" / "visualizers" / "ideam_visualizer.py")
ideam_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ideam_module)
IDEAMRadarVisualizer = ideam_module.IDEAMRadarVisualizer

def test_visualizador():
    """Prueba básica del visualizador"""
    print("\n" + "="*70)
    print("🧪 PRUEBA DEL VISUALIZADOR IDEAM OPTIMIZADO")
    print("="*70)
    
    # Crear instancia
    viz = IDEAMRadarVisualizer()
    
    # Listar radares
    print("\n1️⃣ Listando radares disponibles...")
    radares = viz.listar_radares()
    
    if not radares:
        print("❌ No se encontraron radares")
        return False
    
    # Cargar datos del primer radar (solo 20 archivos para prueba rápida)
    radar = radares[0]
    print(f"\n2️⃣ Cargando datos de {radar} (límite: 20 archivos)...")
    df = viz.cargar_datos_radar(radar, limite=20)
    
    if df is None:
        print("❌ No se pudieron cargar datos")
        return False
    
    # Mostrar estructura del DataFrame
    print(f"\n3️⃣ Estructura del DataFrame:")
    print(f"   - Registros: {len(df)}")
    print(f"   - Columnas: {len(df.columns)}")
    print(f"   - Columnas disponibles: {list(df.columns)}")
    
    # Obtener DataFrame trabajable
    print(f"\n4️⃣ Obteniendo DataFrame trabajable...")
    df_trabajable = viz.obtener_dataframe_trabajable()
    
    if df_trabajable is not None:
        print(f"\n✅ DataFrame trabajable:")
        print(df_trabajable.head())
        print(f"\n   Columnas: {list(df_trabajable.columns)}")
    
    # Estadísticas
    print(f"\n5️⃣ Estadísticas completas:")
    stats = viz.estadisticas_completas()
    
    print(f"\n✅ Prueba completada exitosamente!")
    print(f"   - Radar procesado: {radar}")
    print(f"   - Archivos procesados: {len(df)}")
    print(f"   - PyART disponible: {'Sí' if stats else 'No'}")
    
    return True

if __name__ == "__main__":
    try:
        success = test_visualizador()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
