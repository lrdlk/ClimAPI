# 📊 Guía de Procesamiento de Datos Climáticos

## 🎯 Resumen Ejecutivo

Se ha implementado un **pipeline ETL modular** para procesar datos climáticos sin alterar la estructura existente del proyecto. Los datos fluyen así:

```
📁 Data (JSON, CSV, TXT, Imágenes)
    ↓
📥 Data Loaders (Parsear múltiples formatos)
    ↓
✅ Validators (Detectar anomalías)
    ↓
🔄 Pipelines (Orquestar proceso completo)
    ↓
📊 DataFrame Limpio (Listo para análisis)
```

---

## 📂 Estructura Nueva

```
src/
├── data_loaders/          ← 🆕 NUEVO
│   ├── __init__.py
│   ├── json_loader.py      # Parsea JSON de APIs climáticas
│   ├── file_loader.py      # CSV, TXT, Excel
│   └── unified_loader.py   # Cargador unificado (punto de entrada)
│
├── validators/            ← 🆕 NUEVO
│   ├── __init__.py
│   └── data_validator.py   # Validación y limpieza de datos
│
├── pipelines/             ← 🆕 NUEVO
│   ├── __init__.py
│   └── climate_pipeline.py # Orquesta todo el proceso
│
├── processors/            ← Existente (sin cambios)
├── visualizers/           ← Existente (sin cambios)
└── data_sources/          ← Existente (sin cambios)
```

---

## 🚀 Uso Rápido

### **Opción 1: Lo más simple (1 línea)**
```python
from src.data_loaders import UnifiedDataLoader

# Carga TODO
df = UnifiedDataLoader("data").load_all()
print(df.shape)  # (N registros, M columnas)
```

### **Opción 2: Recomendado (pipeline completo)**
```python
from src.pipelines import ClimateDataPipeline

pipeline = ClimateDataPipeline("data")
df_clean = pipeline.execute(
    validate=True,          # Eliminar outliers
    fill_nulls=True,        # Rellenar nulos
    remove_outliers=True,   # Validar rangos
    resample_freq=None      # Sin resampleo (o '1H' para horario)
)
```

### **Opción 3: Por ubicación**
```python
pipeline = ClimateDataPipeline("data")

# Listar ubicaciones disponibles
locations = UnifiedDataLoader.get_available_locations("data")
# Resultado: ['Bogota', 'Cali', 'Cartagena', 'Medellín', ...]

# Procesar una ubicación
df_bogota = pipeline.execute_by_location("Bogota")
```

---

## 📊 Módulos Detallados

### **1. Data Loaders** (`src/data_loaders/`)

#### `JSONDataLoader` - Parsea APIs climáticas
```python
from src.data_loaders import JSONDataLoader

# Cargar un JSON específico
data = JSONDataLoader.load_json("data/consulta_completa_Bogota.json")

# Extraer datos de Meteoblue
df_meteoblue = JSONDataLoader.extract_meteoblue(data, location="Bogota")

# Extraer datos de OpenMeteo
df_openmeteo = JSONDataLoader.extract_openmeteo(data, location="Bogota")

# Cargar directorio completo
df = JSONDataLoader.load_from_directory("data", pattern="consulta_completa_*.json")
```

**Columnas generadas:**
- `timestamp` - Fecha/hora
- `temperature_C` - Temperatura (°C)
- `windspeed_ms` - Velocidad viento (m/s)
- `winddirection_deg` - Dirección viento (°)
- `precipitation_mm` - Precipitación (mm)
- `humidity_percent` - Humedad (%)
- `pressure_hPa` - Presión (hPa)
- `source` - Fuente (meteoblue, openmeteo, etc)

#### `FileLoader` - CSV, TXT, Excel
```python
from src.data_loaders import FileLoader

# Cargar archivo individual
df = FileLoader.load_file("data/datos_clima.csv")

# Cargar directorio completo
archivos = FileLoader.load_directory("data", pattern="*.csv")

# Estandarizar nombres de columnas
df_std = FileLoader.standardize_columns(df)
```

#### `UnifiedDataLoader` - Punto único de entrada
```python
from src.data_loaders import UnifiedDataLoader

loader = UnifiedDataLoader("data")

# Cargar todo (JSON + CSV + TXT)
df = loader.load_all(
    standardize=True,   # Nombres estándar
    remove_nulls=True,  # Filas completamente vacías
    resample_freq=None  # '1H' = horario, 'D' = diario
)

# Cargar por ubicación
df_bogota = loader.load_location("Bogota")

# Cargar por fuente
df_meteoblue = loader.load_source("meteoblue")

# Listar ubicaciones/fuentes disponibles
locations = UnifiedDataLoader.get_available_locations("data")
sources = UnifiedDataLoader.get_available_sources("data")
```

---

### **2. Validators** (`src/validators/`)

#### `DataValidator` - Limpieza y validación
```python
from src.validators import DataValidator

# Validar rango de temperatura (-50 a 60°C)
df_valid, report = DataValidator.validate_range(
    df, 'temperature_C', -50, 60
)

# Validar TODO contra rangos conocidos
df_clean, reports = DataValidator.validate_all(df)

# Detectar datos faltantes
missing = DataValidator.check_missing_data(df)
# Resultado: {'temperature_C': 2.5, 'pressure_hPa': 1.2, ...}

# Rellenar nulos
df_filled = DataValidator.fill_missing(df, method='linear')
# Methods: 'forward', 'linear', 'mean', 'drop'

# Detectar duplicados
n_duplicates = DataValidator.detect_duplicates(df)
```

**Rangos validados automáticamente:**
```python
VALID_RANGES = {
    'temperature_C': (-50, 60),
    'windspeed_ms': (0, 50),
    'humidity_percent': (0, 100),
    'pressure_hPa': (900, 1100),
    'precipitation_mm': (0, 500),
    'cloudiness_percent': (0, 100),
}
```

---

### **3. Pipelines** (`src/pipelines/`)

#### `ClimateDataPipeline` - Orquesta todo
```python
from src.pipelines import ClimateDataPipeline

pipeline = ClimateDataPipeline("data")

# EXECUTE: Carga → Valida → Llena nulos → Elimina duplicados
df = pipeline.execute(
    validate=True,
    fill_nulls=True,
    remove_outliers=True,
    resample_freq='1H'  # Resamplear a horario
)

# Por ubicación
df_cali = pipeline.execute_by_location("Cali", fill_nulls=True)

# Por fuente
df_meteoblue = pipeline.execute_by_source("meteoblue")

# Guardar resultado
output_path = pipeline.save_processed(df)
# Genera: data/processed/clima_procesado_YYYYMMDD_HHMMSS.csv
```

---

## 📈 Ejemplo Completo

```python
import pandas as pd
from src.pipelines import ClimateDataPipeline

# 1. Crear pipeline
pipeline = ClimateDataPipeline("data")

# 2. Procesar datos
df = pipeline.execute(
    validate=True,
    fill_nulls=True,
    remove_outliers=True
)

# 3. Análisis
print(f"Registros: {len(df)}")
print(f"Columnas: {df.columns.tolist()}")
print(f"Período: {df['timestamp'].min()} → {df['timestamp'].max()}")

# 4. Estadísticas por variable
print(df.describe())

# 5. Correlación
numeric = df.select_dtypes(include=['number']).columns
print(df[numeric].corr())

# 6. Agrupar por ubicación
for location in df['location'].unique():
    df_loc = df[df['location'] == location]
    print(f"\n{location}: {len(df_loc)} registros")
    print(f"  Temperatura: {df_loc['temperature_C'].min():.1f} - {df_loc['temperature_C'].max():.1f}°C")
    print(f"  Viento: {df_loc['windspeed_ms'].mean():.1f} m/s promedio")

# 7. Guardar
pipeline.save_processed(df)
```

---

## 🔍 Casos de Uso

### **Caso 1: Análisis temporal**
```python
df = pipeline.execute(resample_freq='1H')  # Datos horarios

# Temperatura promedio por hora
temp_horaria = df.groupby(df['timestamp'].dt.hour)['temperature_C'].mean()

# Viento máximo diario
df['fecha'] = df['timestamp'].dt.date
viento_max = df.groupby('fecha')['windspeed_ms'].max()
```

### **Caso 2: Comparación entre ubicaciones**
```python
for location in UnifiedDataLoader.get_available_locations("data"):
    df_loc = pipeline.execute_by_location(location)
    
    print(f"{location}:")
    print(f"  Temp prom: {df_loc['temperature_C'].mean():.1f}°C")
    print(f"  Humedad prom: {df_loc['humidity_percent'].mean():.1f}%")
    print(f"  Precipitación total: {df_loc['precipitation_mm'].sum():.1f}mm")
```

### **Caso 3: Análisis de calidad del aire (si disponible)**
```python
df = pipeline.execute()

# Filtrar por variables de aire
air_cols = [col for col in df.columns if 'aqi' in col.lower() or 'pm' in col.lower()]
if air_cols:
    print("Variables de aire disponibles:", air_cols)
    print(df[air_cols].describe())
```

---

## ⚙️ Configuración

### **Cambiar directorio de datos**
```python
pipeline = ClimateDataPipeline("data/clima")  # Otro directorio
```

### **Métodos de rellenado de nulos**
```python
# Forward fill (última observación)
df = DataValidator.fill_missing(df, method='forward')

# Interpolación lineal
df = DataValidator.fill_missing(df, method='linear')

# Media de columna
df = DataValidator.fill_missing(df, method='mean')

# Eliminar filas nulas
df = DataValidator.fill_missing(df, method='drop')
```

### **Crear rango personalizado**
```python
from src.validators import DataValidator

# Validar temperatura entre -10 y 40°C
df_filtered, report = DataValidator.validate_range(
    df, 'temperature_C', min_val=-10, max_val=40
)
print(report)
# {'column': 'temperature_C', 'outliers_count': 25, 'outliers_percent': 0.5, ...}
```

---

## 📝 Logging

El sistema registra automáticamente todos los pasos:

```python
import logging

# Habilitar logging detallado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

pipeline = ClimateDataPipeline("data")
df = pipeline.execute()

# Salida:
# [INFO] ============================================================
# [INFO] Cargando archivos JSON...
# [INFO] ✓ JSON: 1000 registros
# [INFO] Validando datos...
# [INFO] Eliminadas 5 filas con outliers
# ...
```

---

## 🔗 Integración con Proyecto

Sin cambios en:
- ✅ `src/data_sources/` - APIs siguen igual
- ✅ `src/processors/` - Radar processor intacto
- ✅ `src/visualizers/` - Visualizadores intactos
- ✅ `main.py` - Script principal sin tocar

Añade:
- 🆕 `src/data_loaders/` - Nuevos loaders
- 🆕 `src/validators/` - Validadores
- 🆕 `src/pipelines/` - Pipelines ETL

---

## 🚨 Errores Comunes

### **"Módulo no encontrado"**
```python
# Asegúrate de ejecutar desde raíz del proyecto
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
```

### **No se cargan JSON**
```python
# Verifica patrón de archivos
from pathlib import Path
json_files = list(Path("data").glob("*.json"))
print(f"JSONs encontrados: {len(json_files)}")

# Puede necesitar patrón específico
json_files = list(Path("data").glob("consulta_completa_*.json"))
```

### **Muchos nulos después de limpiar**
```python
# No rellenar automáticamente
df = pipeline.execute(fill_nulls=False)
print(df.isna().sum())  # Ver dónde están los nulos

# O cambiar método de relleno
df = DataValidator.fill_missing(df, method='mean')
```

---

## 📚 Referencias

- Pandas: https://pandas.pydata.org/
- NumPy: https://numpy.org/
- Datos meteorológicos: https://openmeteo.com/, https://www.meteoblue.com/

---

## ✨ Próximos Pasos

1. **Machine Learning**: `src/ml_models/` para predicciones
2. **Análisis Avanzado**: `src/analysis/` para correlaciones, trends
3. **Dashboard Dinámico**: Integrar con Streamlit existente
4. **Almacenamiento**: Base de datos para histórico

Ejecuta ahora:
```bash
python ejemplo_procesamiento.py
```
