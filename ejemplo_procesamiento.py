"""
EJEMPLO DE USO DEL PIPELINE DE PROCESAMIENTO DE DATOS CLIMÁTICOS
=================================================================

Este script muestra cómo usar los nuevos módulos de carga, validación y procesamiento
sin alterar la estructura existente del proyecto.
"""

import sys
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Importar del nuevo módulo
from src.pipelines import ClimateDataPipeline
from src.data_loaders import UnifiedDataLoader
from src.validators import DataValidator

# ============================================================================
# OPCIÓN 1: CARGAR TODOS LOS DATOS DE UNA VEZ
# ============================================================================

def ejemplo_1_cargar_todo():
    """Carga todos los datos y genera un DataFrame consolidado"""
    print("\n" + "="*70)
    print("OPCIÓN 1: Cargar y consolidar todos los datos")
    print("="*70)
    
    loader = UnifiedDataLoader("data")
    
    # Cargar TODO
    df = loader.load_all(standardize=True, remove_nulls=True)
    
    print(f"\nDatos cargados:")
    print(f"  - Forma: {df.shape}")
    print(f"  - Columnas: {list(df.columns)}")
    print(f"\nMuestra de datos:")
    print(df.head())
    
    # Ubicaciones disponibles
    print(f"\nUbicaciones encontradas: {UnifiedDataLoader.get_available_locations('data')}")
    print(f"Fuentes encontradas: {UnifiedDataLoader.get_available_sources('data')}")
    
    return df


# ============================================================================
# OPCIÓN 2: USAR EL PIPELINE COMPLETO (RECOMENDADO)
# ============================================================================

def ejemplo_2_pipeline_completo():
    """
    Ejecuta pipeline completo:
    Load → Validate → Fill Nulls → Remove Duplicates
    """
    print("\n" + "="*70)
    print("OPCIÓN 2: Pipeline completo (RECOMENDADO)")
    print("="*70)
    
    pipeline = ClimateDataPipeline("data")
    
    # Ejecutar pipeline con todas las opciones
    df_clean = pipeline.execute(
        validate=True,           # Validar rangos
        fill_nulls=True,         # Rellenar valores nulos
        remove_outliers=True,    # Eliminar outliers
        resample_freq=None       # Sin resampleo (usar '1H' para horario)
    )
    
    print(f"\nDataFrame limpio:")
    print(f"  - Registros: {len(df_clean)}")
    print(f"  - Columnas: {list(df_clean.columns)}")
    print(f"\nMuestra:")
    print(df_clean.head())
    
    # Guardar resultado
    output_path = pipeline.save_processed(df_clean)
    print(f"\n✓ Guardado en: {output_path}")
    
    return df_clean


# ============================================================================
# OPCIÓN 3: PROCESAR POR UBICACIÓN
# ============================================================================

def ejemplo_3_por_ubicacion():
    """Procesa datos por ubicación específica"""
    print("\n" + "="*70)
    print("OPCIÓN 3: Procesar por ubicación")
    print("="*70)
    
    pipeline = ClimateDataPipeline("data")
    
    # Obtener ubicaciones disponibles
    locations = UnifiedDataLoader.get_available_locations("data")
    
    print(f"\nUbicaciones disponibles: {locations}")
    
    # Procesar cada ubicación
    for location in locations:
        df_location = pipeline.execute_by_location(
            location,
            fill_nulls=True,
            remove_outliers=True
        )
        
        if not df_location.empty:
            print(f"\n{location}:")
            print(f"  - Registros: {len(df_location)}")
            print(f"  - Período: {df_location['timestamp'].min()} → {df_location['timestamp'].max()}")


# ============================================================================
# OPCIÓN 4: ANÁLISIS ESTADÍSTICO
# ============================================================================

def ejemplo_4_estadisticas(df):
    """Genera estadísticas de los datos"""
    print("\n" + "="*70)
    print("OPCIÓN 4: Estadísticas de los datos")
    print("="*70)
    
    # Estadísticas básicas
    print("\nEstadísticas de variables climáticas:")
    print(df.describe().round(2))
    
    # Análisis de nulos
    print("\nAnálisis de valores faltantes:")
    missing = DataValidator.check_missing_data(df)
    
    # Correlación
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 1:
        print("\nCorrelación entre variables:")
        corr = df[numeric_cols].corr()
        print(corr.round(3))


# ============================================================================
# OPCIÓN 5: EXPORTAR POR FORMATO
# ============================================================================

def ejemplo_5_exportar(df):
    """Guarda en múltiples formatos"""
    print("\n" + "="*70)
    print("OPCIÓN 5: Exportar en múltiples formatos")
    print("="*70)
    
    output_dir = Path("data/processed")
    output_dir.mkdir(exist_ok=True)
    
    # CSV
    csv_path = output_dir / "clima_datos.csv"
    df.to_csv(csv_path, index=False)
    print(f"✓ CSV: {csv_path}")
    
    # Parquet (más eficiente)
    try:
        parquet_path = output_dir / "clima_datos.parquet"
        df.to_parquet(parquet_path, index=False)
        print(f"✓ Parquet: {parquet_path}")
    except:
        print("⚠ Parquet no disponible (instala: pip install pyarrow)")
    
    # Excel (si está disponible)
    try:
        excel_path = output_dir / "clima_datos.xlsx"
        df.to_excel(excel_path, index=False, sheet_name='Datos')
        print(f"✓ Excel: {excel_path}")
    except:
        print("⚠ Excel no disponible (instala: pip install openpyxl)")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    
    # Opción 1: Cargar todo
    # df = ejemplo_1_cargar_todo()
    
    # Opción 2: Pipeline completo (RECOMENDADO)
    df = ejemplo_2_pipeline_completo()
    
    # Opción 3: Por ubicación
    # ejemplo_3_por_ubicacion()
    
    # Opción 4: Estadísticas
    ejemplo_4_estadisticas(df)
    
    # Opción 5: Exportar
    ejemplo_5_exportar(df)
    
    print("\n" + "="*70)
    print("✓ EJEMPLO COMPLETADO")
    print("="*70)
