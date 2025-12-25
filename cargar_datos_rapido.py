"""
CARGADOR RÁPIDO DE DATOS CLIMÁTICOS
====================================

Carga los datos reales de tus JSONs y genera reportes.
Ejecuta: python cargar_datos_rapido.py
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
        return None


def extraer_openmeteo(data):
    """Extrae datos de OpenMeteo"""
    records = []
    location = data.get('location', 'Unknown')
    
    if 'openmeteo' not in data:
        return records
    
    om = data['openmeteo']
    if not isinstance(om, dict) or 'hourly' not in om:
        return records
    
    hourly = om.get('hourly')
    if isinstance(hourly, str):
        try:
            hourly = json.loads(hourly)
        except:
            return records
    
    if not isinstance(hourly, dict) or 'time' not in hourly:
        return records
    
    times = hourly.get('time', [])
    temps = hourly.get('temperature_2m', [])
    winds = hourly.get('windspeed_10m', [])
    precips = hourly.get('precipitation', [])
    humidity = hourly.get('relative_humidity_2m', [])
    pressure = hourly.get('pressure', [])
    
    if not times:
        return records
    
    for i, t in enumerate(times):
        record = {
            'timestamp': t,
            'location': location,
            'temperature_C': temps[i] if i < len(temps) else None,
            'windspeed_ms': winds[i] if i < len(winds) else None,
            'precipitation_mm': precips[i] if i < len(precips) else None,
            'humidity_percent': humidity[i] if i < len(humidity) else None,
            'pressure_hPa': pressure[i] if i < len(pressure) else None,
        }
        records.append(record)
    
    return records


def main():
    print("\n" + "="*70)
    print("CARGADOR DE DATOS CLIMÁTICOS")
    print("="*70)
    
    # 1. Cargar JSONs
    data_dir = Path("data")
    json_files = list(data_dir.glob("consulta_completa_*.json"))
    
    print(f"\n[1] CARGANDO {len(json_files)} ARCHIVOS JSON...")
    
    all_records = []
    
    for json_file in json_files:
        data = cargar_json_seguro(json_file)
        if data:
            records = extraer_openmeteo(data)
            all_records.extend(records)
            print(f"  ✓ {json_file.name}: {len(records)} registros")
    
    if not all_records:
        print("\n❌ No se pudieron cargar datos")
        return
    
    # 2. Crear DataFrame
    df = pd.DataFrame(all_records)
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    
    for col in ['temperature_C', 'windspeed_ms', 'precipitation_mm', 'humidity_percent', 'pressure_hPa']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    print(f"\n✓ Total: {len(df)} registros")
    
    # 3. Información
    print("\n" + "="*70)
    print("INFORMACIÓN DEL DATASET")
    print("="*70)
    
    print(f"\nDimensiones: {df.shape[0]} × {df.shape[1]}")
    print(f"\nUbicaciones ({df['location'].nunique()}):")
    for loc in sorted(df['location'].unique()):
        count = len(df[df['location'] == loc])
        print(f"  • {loc}: {count}")
    
    print(f"\nPeríodo: {df['timestamp'].min()} → {df['timestamp'].max()}")
    
    # 4. Primeros registros
    print("\n[2] PRIMEROS REGISTROS:")
    print(df.head(3).to_string())
    
    # 5. Estadísticas
    print("\n" + "="*70)
    print("ESTADÍSTICAS")
    print("="*70)
    
    numeric = df.select_dtypes(include=['number']).columns
    print("\n" + df[numeric].describe().round(2).to_string())
    
    # 6. Por ubicación
    print("\n" + "="*70)
    print("RESUMEN POR UBICACIÓN")
    print("="*70)
    
    for location in sorted(df['location'].unique()):
        df_loc = df[df['location'] == location]
        print(f"\n{location}:")
        print(f"  Registros: {len(df_loc)}")
        
        if 'temperature_C' in df_loc.columns:
            temp = df_loc['temperature_C'].dropna()
            if len(temp) > 0:
                print(f"  Temperatura: {temp.min():.1f}-{temp.max():.1f}°C (prom: {temp.mean():.1f}°C)")
        
        if 'humidity_percent' in df_loc.columns:
            h = df_loc['humidity_percent'].dropna()
            if len(h) > 0:
                print(f"  Humedad: {h.mean():.0f}%")
        
        if 'windspeed_ms' in df_loc.columns:
            w = df_loc['windspeed_ms'].dropna()
            if len(w) > 0:
                print(f"  Viento: {w.mean():.1f} m/s")
    
    # 7. Guardar
    print("\n" + "="*70)
    print("GUARDANDO DATOS")
    print("="*70)
    
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    csv_path = output_dir / "datos_climaticos.csv"
    df.to_csv(csv_path, index=False)
    print(f"\n✓ CSV: {csv_path}")
    
    try:
        df.to_parquet(output_dir / "datos_climaticos.parquet", index=False)
        print(f"✓ Parquet: {output_dir / 'datos_climaticos.parquet'}")
    except:
        pass
    
    # 8. Correlación
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
    
    print("\n📖 Próximos pasos:")
    print("  1. Lee: GUIA_PROCESAMIENTO_DATOS.md")
    print("  2. Lee: SOLUCIÓN_PROCESAMIENTO_DATOS.md")
    print("  3. Usa: from src.pipelines import ClimateDataPipeline")
    print("\n✨ Tus datos están en: data/processed/\n")
    
    return df


if __name__ == "__main__":
    df = main()
