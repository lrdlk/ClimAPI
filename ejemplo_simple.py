"""
EJEMPLO SIMPLE Y DIRECTO
========================

Carga los datos climáticos reales de tus JSON y muestra estadísticas.
Ejecuta: python ejemplo_simple.py
"""

from src.data_loaders import UnifiedDataLoader, JSONDataLoader
from src.pipelines import ClimateDataPipeline
from pathlib import Path
import pandas as pd


def main():
    print("\n" + "="*70)
    print("PROCESAMIENTO DE DATOS CLIMÁTICOS - EJEMPLO SIMPLE")
    print("="*70)
    
    # ========================================================================
    # PASO 1: CARGAR LOS DATOS
    # ========================================================================
    
    print("\n[1] CARGANDO DATOS DE APIS CLIMÁTICAS...")
    
    loader = UnifiedDataLoader("data")
    
    # Cargar directamente los JSON (sin procesar TXT)
    df = JSONDataLoader.load_from_directory("data", pattern="consulta_completa_*.json")
    
    print(f"✓ Cargados {len(df)} registros climáticos")
    print(f"✓ Ubicaciones: {df['location'].unique().tolist()}")
    print(f"✓ Fuentes: {df['source'].unique().tolist()}")
    
    # ========================================================================
    # PASO 2: MOSTRAR INFORMACIÓN BÁSICA
    # ========================================================================
    
    print("\n[2] INFORMACIÓN DEL DATAFRAME")
    print("-" * 70)
    print(f"Forma: {df.shape[0]} registros × {df.shape[1]} columnas")
    print(f"\nColumnas disponibles:")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i}. {col} ({df[col].dtype})")
    
    print(f"\nPrimeros 3 registros:")
    print(df.head(3).to_string())
    
    # ========================================================================
    # PASO 3: ESTADÍSTICAS POR VARIABLE
    # ========================================================================
    
    print("\n[3] ESTADÍSTICAS DE VARIABLES CLIMÁTICAS")
    print("-" * 70)
    
    numeric_cols = df.select_dtypes(include=['number']).columns
    
    if len(numeric_cols) > 0:
        print(df[numeric_cols].describe().round(2).to_string())
    else:
        print("No hay columnas numéricas para analizar")
    
    # ========================================================================
    # PASO 4: ANÁLISIS POR UBICACIÓN
    # ========================================================================
    
    print("\n[4] RESUMEN POR UBICACIÓN")
    print("-" * 70)
    
    for location in df['location'].unique():
        df_loc = df[df['location'] == location]
        print(f"\n{location}: {len(df_loc)} registros")
        
        # Mostrar variables disponibles
        numeric_loc = df_loc.select_dtypes(include=['number']).columns
        
        if 'temperature_C' in numeric_loc:
            temp = df_loc['temperature_C'].dropna()
            if len(temp) > 0:
                print(f"  Temperatura: {temp.min():.1f} - {temp.max():.1f}°C "
                      f"(promedio: {temp.mean():.1f}°C)")
        
        if 'windspeed_ms' in numeric_loc:
            wind = df_loc['windspeed_ms'].dropna()
            if len(wind) > 0:
                print(f"  Viento: {wind.mean():.1f} m/s promedio "
                      f"(máximo: {wind.max():.1f} m/s)")
        
        if 'humidity_percent' in numeric_loc:
            humid = df_loc['humidity_percent'].dropna()
            if len(humid) > 0:
                print(f"  Humedad: {humid.mean():.0f}% promedio")
        
        if 'precipitation_mm' in numeric_loc:
            precip = df_loc['precipitation_mm'].dropna()
            if len(precip) > 0:
                print(f"  Precipitación: {precip.sum():.1f}mm total "
                      f"({precip.mean():.1f}mm promedio)")
    
    # ========================================================================
    # PASO 5: ANÁLISIS POR FUENTE
    # ========================================================================
    
    print("\n[5] RESUMEN POR FUENTE CLIMÁTICA")
    print("-" * 70)
    
    for source in df['source'].unique():
        df_src = df[df['source'] == source]
        print(f"\n{source.upper()}: {len(df_src)} registros")
        print(f"  Ubicaciones: {df_src['location'].unique().tolist()}")
        
        numeric_src = df_src.select_dtypes(include=['number']).columns
        print(f"  Variables: {list(numeric_src)}")
    
    # ========================================================================
    # PASO 6: VALORES FALTANTES
    # ========================================================================
    
    print("\n[6] ANÁLISIS DE VALORES FALTANTES")
    print("-" * 70)
    
    missing = df.isna().sum()
    missing_pct = 100 * missing / len(df)
    
    missing_data = pd.DataFrame({
        'Faltantes': missing,
        'Porcentaje': missing_pct.round(2)
    })
    
    missing_data = missing_data[missing_data['Faltantes'] > 0].sort_values('Porcentaje', ascending=False)
    
    if len(missing_data) > 0:
        print(missing_data.to_string())
    else:
        print("✓ No hay valores faltantes")
    
    # ========================================================================
    # PASO 7: GUARDAR DATOS
    # ========================================================================
    
    print("\n[7] GUARDANDO DATOS PROCESADOS")
    print("-" * 70)
    
    output_dir = Path("data/processed")
    output_dir.mkdir(exist_ok=True)
    
    # Guardar CSV
    csv_path = output_dir / "datos_climaticos_raw.csv"
    df.to_csv(csv_path, index=False)
    print(f"✓ CSV: {csv_path}")
    
    # Guardar Parquet (más eficiente)
    try:
        parquet_path = output_dir / "datos_climaticos_raw.parquet"
        df.to_parquet(parquet_path, index=False)
        print(f"✓ Parquet: {parquet_path}")
    except:
        print("⚠ Parquet no disponible")
    
    # ========================================================================
    # PASO 8: CORRELACIONES
    # ========================================================================
    
    print("\n[8] CORRELACIÓN ENTRE VARIABLES")
    print("-" * 70)
    
    numeric = df.select_dtypes(include=['number']).columns
    
    if len(numeric) > 1:
        corr = df[numeric].corr()
        print("\nMatriz de correlación:")
        print(corr.round(3).to_string())
    
    # ========================================================================
    # RESUMEN FINAL
    # ========================================================================
    
    print("\n" + "="*70)
    print("✓ PROCESAMIENTO COMPLETADO")
    print("="*70)
    
    print("\n📊 Resumen:")
    print(f"  • Registros: {len(df)}")
    print(f"  • Variables: {len(df.columns)}")
    print(f"  • Ubicaciones: {df['location'].nunique()}")
    print(f"  • Fuentes: {df['source'].nunique()}")
    print(f"  • Período: {df['timestamp'].min()} → {df['timestamp'].max()}")
    
    print("\n💾 Archivos guardados en: data/processed/")
    
    print("\n🔍 Próximos pasos:")
    print("  1. Abre: GUIA_PROCESAMIENTO_DATOS.md")
    print("  2. Usa: from src.pipelines import ClimateDataPipeline")
    print("  3. Ejecuta: python ejemplo_procesamiento.py")
    
    print("\n" + "="*70 + "\n")
    
    return df


if __name__ == "__main__":
    df = main()
