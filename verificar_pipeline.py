"""
Script de verificación del sistema de procesamiento de datos
Valida que todos los módulos estén correctamente instalados y funcionen
"""

import sys
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Añadir raíz al path
sys.path.insert(0, str(Path(__file__).parent))


def check_imports():
    """Verifica que todos los módulos se pueden importar"""
    print("\n" + "="*70)
    print("1. VERIFICANDO IMPORTACIONES")
    print("="*70)
    
    modules_to_check = [
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("json", "json (built-in)"),
        ("src.data_loaders", "DataLoaders"),
        ("src.validators", "Validators"),
        ("src.pipelines", "Pipelines"),
    ]
    
    failed = []
    
    for import_name, display_name in modules_to_check:
        try:
            __import__(import_name)
            print(f"  ✓ {display_name}")
        except ImportError as e:
            print(f"  ✗ {display_name}: {e}")
            failed.append(display_name)
    
    return len(failed) == 0


def check_data_directory():
    """Verifica estructura de directorio de datos"""
    print("\n" + "="*70)
    print("2. VERIFICANDO DIRECTORIO DE DATOS")
    print("="*70)
    
    data_dir = Path("data")
    
    if not data_dir.exists():
        print(f"  ✗ Directorio 'data' no encontrado")
        return False
    
    print(f"  ✓ Directorio 'data' encontrado")
    
    # Buscar archivos de datos
    json_files = list(data_dir.glob("consulta_completa_*.json"))
    csv_files = list(data_dir.glob("*.csv"))
    txt_files = list(data_dir.glob("*.txt"))
    
    print(f"  ✓ JSON climáticos: {len(json_files)} archivos")
    print(f"  ✓ CSV: {len(csv_files)} archivos")
    print(f"  ✓ TXT: {len(txt_files)} archivos")
    
    if len(json_files) == 0 and len(csv_files) == 0 and len(txt_files) == 0:
        print("  ⚠ No se encontraron archivos de datos")
        return False
    
    # Crear subdirectorios si no existen
    subdirs = ["processed", "temp", "images"]
    for subdir in subdirs:
        sub_path = data_dir / subdir
        sub_path.mkdir(exist_ok=True)
        print(f"  ✓ {subdir}/ listo")
    
    return True


def check_data_loader():
    """Prueba JSONDataLoader"""
    print("\n" + "="*70)
    print("3. PROBANDO JSON DATA LOADER")
    print("="*70)
    
    try:
        from src.data_loaders import JSONDataLoader
        
        # Intentar cargar un JSON
        json_files = list(Path("data").glob("consulta_completa_*.json"))
        
        if json_files:
            json_file = json_files[0]
            data = JSONDataLoader.load_json(json_file)
            
            if data:
                print(f"  ✓ JSON cargado: {json_file.name}")
                print(f"    - Ubicación: {data.get('location', 'Unknown')}")
                
                # Verificar fuentes
                sources = []
                if 'meteoblue' in data: sources.append('meteoblue')
                if 'openmeteo' in data: sources.append('openmeteo')
                if 'openweather' in data: sources.append('openweather')
                
                print(f"    - Fuentes: {', '.join(sources)}")
                
                return True
        else:
            print("  ⚠ No se encontraron JSONs para probar")
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False
    
    return True


def check_unified_loader():
    """Prueba UnifiedDataLoader"""
    print("\n" + "="*70)
    print("4. PROBANDO UNIFIED DATA LOADER")
    print("="*70)
    
    try:
        from src.data_loaders import UnifiedDataLoader
        
        loader = UnifiedDataLoader("data")
        
        # Listar ubicaciones disponibles
        locations = UnifiedDataLoader.get_available_locations("data")
        if locations:
            print(f"  ✓ Ubicaciones encontradas: {locations}")
        else:
            print("  ⚠ No se encontraron ubicaciones en JSON")
        
        # Listar fuentes
        sources = UnifiedDataLoader.get_available_sources("data")
        if sources:
            print(f"  ✓ Fuentes disponibles: {sources}")
        else:
            print("  ⚠ No se encontraron fuentes")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_validators():
    """Prueba DataValidator"""
    print("\n" + "="*70)
    print("5. PROBANDO DATA VALIDATOR")
    print("="*70)
    
    try:
        from src.validators import DataValidator
        import pandas as pd
        
        # Crear DataFrame de prueba
        df_test = pd.DataFrame({
            'temperature_C': [15, 20, 25, -100, 30],  # -100 es outlier
            'windspeed_ms': [5, 10, 15, 20, 25],
            'humidity_percent': [60, 70, 80, 90, 100],
        })
        
        print(f"  ✓ DataFrame de prueba creado: {len(df_test)} registros")
        
        # Validar
        df_valid, reports = DataValidator.validate_all(df_test, remove_outliers=True)
        print(f"  ✓ Validación completada: {len(df_valid)} registros después")
        
        # Detectar nulos
        missing = DataValidator.check_missing_data(df_test)
        print(f"  ✓ Análisis de nulos completado")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_pipeline():
    """Prueba ClimateDataPipeline"""
    print("\n" + "="*70)
    print("6. PROBANDO CLIMATE DATA PIPELINE")
    print("="*70)
    
    try:
        from src.pipelines import ClimateDataPipeline
        
        pipeline = ClimateDataPipeline("data")
        print("  ✓ Pipeline inicializado")
        
        # NOTA: No ejecutamos el pipeline completo para no gastar tiempo
        # Solo verificamos que se puede instanciar
        
        print("  ✓ Pipeline listo para usar")
        print("  → Ejecuta: pipeline.execute()")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def print_summary(results):
    """Imprime resumen"""
    print("\n" + "="*70)
    print("RESUMEN")
    print("="*70)
    
    checks = [
        ("Importaciones", results[0]),
        ("Directorio de datos", results[1]),
        ("JSON Loader", results[2]),
        ("Unified Loader", results[3]),
        ("Data Validator", results[4]),
        ("Climate Pipeline", results[5]),
    ]
    
    passed = sum(1 for _, r in checks if r)
    total = len(checks)
    
    for name, result in checks:
        status = "✓" if result else "✗"
        print(f"  {status} {name}")
    
    print(f"\nResultado: {passed}/{total} pruebas pasadas")
    
    if passed == total:
        print("\n✓✓✓ TODO LISTO PARA USAR ✓✓✓")
        print("\nPróximos pasos:")
        print("  1. Ejecuta: python ejemplo_procesamiento.py")
        print("  2. Lee: GUIA_PROCESAMIENTO_DATOS.md")
        return True
    else:
        print("\n⚠ Hay problemas a resolver")
        return False


def main():
    """Ejecuta todas las verificaciones"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "VERIFICACIÓN DEL SISTEMA DE PROCESAMIENTO DE DATOS CLIMÁTICOS".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    
    results = [
        check_imports(),
        check_data_directory(),
        check_data_loader(),
        check_unified_loader(),
        check_validators(),
        check_pipeline(),
    ]
    
    success = print_summary(results)
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
