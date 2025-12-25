"""
CARGADOR DE DATOS CLIMÁTICOS - VERSIÓN FUNCIONAL
=================================================

Carga datos reales de tus JSONs de OpenMeteo y genera reportes.
Ejecuta: python cargador_datos.py
"""

import json
from pathlib import Path
import pandas as pd


def cargar_json_seguro(filepath):
    """Carga JSON con manejo robusto de errores"""
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            content = f.read()
            content = content.replace('\r\n', '\n')
            return json.loads(content)
    except Exception as e:
        print(f"❌ Error: {filepath.name}: {e}")
        return None


def extraer_openmeteo(data):
    """Carga datos de los JSONs y los procesa"""
    
    print("\n" + "="*70)
    print("CARGADOR DE DATOS CLIMÁTICOS ADAPTADO")
    print("="*70)
    
    data_dir = Path("data")
    json_files = list(data_dir.glob("consulta_completa_*.json"))
    
    print(f"\n✓ Encontrados {len(json_files)} archivos JSON")
    
    all_records = []
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8-sig') as f:
                content = f.read()
                # Limpiar saltos de línea problemáticos
                content = content.replace('\r\n', '\n')
                data = json.loads(content)
            
            location = data.get('location', 'Unknown')
            timestamp = data.get('timestamp', '')
            
            # Procesar OpenMeteo (datos más confiables)
            if 'openmeteo' in data:
                om = data['openmeteo']
                
                # Extraer datos horarios si están disponibles
                if isinstance(om, dict) and 'hourly' in om:
                    hourly = om['hourly']
                    
                    # Si hourly es string, parsearlo
                    if isinstance(hourly, str):
                        hourly = json.loads(hourly)
                    
                    if isinstance(hourly, dict) and 'time' in hourly:
                        times = hourly.get('time', [])
                        temps = hourly.get('temperature_2m', [])
                        winds = hourly.get('windspeed_10m', [])
                        precipit = hourly.get('precipitation', [])
                        humidity = hourly.get('relative_humidity_2m', [])
                        pressure = hourly.get('pressure', [])
                        
                        if times:
                            for i, t in enumerate(times):
                                record = {
                                    'timestamp': t,
                                    'location': location,
                                    'source': 'OpenMeteo',
                                    'temperature_C': temps[i] if i < len(temps) else None,
                                    'windspeed_ms': winds[i] if i < len(winds) else None,
                                    'precipitation_mm': precipit[i] if i < len(precipit) else None,
                                    'humidity_percent': humidity[i] if i < len(humidity) else None,
                                    'pressure_hPa': pressure[i] if i < len(pressure) else None,
                                }
                                all_records.append(record)
        
        except Exception as e:
            print(f"⚠ Error procesando {json_file.name}: {e}")
            continue
    
    if not all_records:
        print("⚠ No se pudieron cargar datos")
        return pd.DataFrame()
    
    df = pd.DataFrame(all_records)
    
    # Convertir timestamp a datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    
    # Convertir columnas numéricas
    numeric_cols = ['temperature_C', 'windspeed_ms', 'precipitation_mm', 'humidity_percent', 'pressure_hPa']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    print(f"\n✓ Cargados {len(df)} registros climáticos")
    
    return df


def main():
    """Main"""
    
    # 1. Cargar datos
    df = load_and_process()
    
    if df.empty:
        print("\n✗ No hay datos para procesar")
        return
    
    # 2. Información básica
    print("\n" + "="*70)
    print("INFORMACIÓN DEL DATASET")
    print("="*70)
    
    print(f"\nDimensiones: {df.shape[0]} registros × {df.shape[1]} columnas")
    print(f"Ubicaciones: {df['location'].nunique()} ({', '.join(df['location'].unique())})")
    print(f"Período: {df['timestamp'].min()} → {df['timestamp'].max()}")
    
    print("\nPrimeros registros:")
    print(df.head().to_string())
    
    # 3. Estadísticas
    print("\n" + "="*70)
    print("ESTADÍSTICAS")
    print("="*70)
    
    numeric_cols = df.select_dtypes(include=['number']).columns
    
    print("\n" + df[numeric_cols].describe().round(2).to_string())
    
    # 4. Por ubicación
    print("\n" + "="*70)
    print("RESUMEN POR UBICACIÓN")
    print("="*70)
    
    for location in df['location'].unique():
        df_loc = df[df['location'] == location]
        print(f"\n{location}:")
        print(f"  Registros: {len(df_loc)}")
        
        if 'temperature_C' in df_loc.columns:
            temp = df_loc['temperature_C'].dropna()
            if len(temp) > 0:
                print(f"  Temperatura: {temp.min():.1f} - {temp.max():.1f}°C "
                      f"(prom: {temp.mean():.1f}°C)")
        
        if 'humidity_percent' in df_loc.columns:
            humid = df_loc['humidity_percent'].dropna()
            if len(humid) > 0:
                print(f"  Humedad: {humid.mean():.0f}% promedio")
        
        if 'windspeed_ms' in df_loc.columns:
            wind = df_loc['windspeed_ms'].dropna()
            if len(wind) > 0:
                print(f"  Viento: {wind.mean():.1f} m/s promedio")
    
    # 5. Valores faltantes
    print("\n" + "="*70)
    print("VALORES FALTANTES")
    print("="*70)
    
    missing = df.isna().sum()
    missing_pct = 100 * missing / len(df)
    
    missing_df = pd.DataFrame({
        'Faltantes': missing,
        '%': missing_pct.round(1)
    })
    
    missing_df = missing_df[missing_df['Faltantes'] > 0].sort_values('%', ascending=False)
    
    if len(missing_df) > 0:
        print(missing_df.to_string())
    else:
        print("✓ Sin valores faltantes")
    
    # 6. Guardar
    print("\n" + "="*70)
    print("GUARDANDO DATOS")
    print("="*70)
    
    output_dir = Path("data/processed")
    output_dir.mkdir(exist_ok=True)
    
    csv_path = output_dir / "datos_climaticos.csv"
    df.to_csv(csv_path, index=False)
    print(f"\n✓ Guardado: {csv_path}")
    
    try:
        parquet_path = output_dir / "datos_climaticos.parquet"
        df.to_parquet(parquet_path, index=False)
        print(f"✓ Guardado: {parquet_path}")
    except:
        pass
    
    # 7. Correlación
    print("\n" + "="*70)
    print("CORRELACIONES")
    print("="*70)
    
    numeric = df.select_dtypes(include=['number']).columns
    if len(numeric) > 1:
        print("\n" + df[numeric].corr().round(3).to_string())
    
    # Final
    print("\n" + "="*70)
    print("✓ COMPLETADO")
    print("="*70)
    
    print("\n📚 Próximos pasos:")
    print("  1. Lee: GUIA_PROCESAMIENTO_DATOS.md")
    print("  2. Usa: from src.pipelines import ClimateDataPipeline")
    print("  3. Analiza: from src.validators import DataValidator")
    
    print("\n✨ Tus datos están listos en: data/processed/\n")
    
    return df


if __name__ == "__main__":
    df = main()
