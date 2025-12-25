# 📊 SOLUCIÓN DE PROCESAMIENTO DE DATOS CLIMÁTICOS

## ✅ Lo que se ha implementado

Se ha creado un **sistema modular y escalable** para procesar datos climáticos sin alterar tu estructura existente:

```
✨ 4 nuevos módulos
├── src/data_loaders/     → Cargar JSON, CSV, TXT, Excel
├── src/validators/       → Limpiar y validar datos
├── src/pipelines/        → Orquestar flujos ETL
└── ejemplo_procesamiento.py  → Script listo para usar
```

---

## 🚀 Inicio Rápido (3 líneas de código)

```python
from src.pipelines import ClimateDataPipeline

pipeline = ClimateDataPipeline("data")
df = pipeline.execute(validate=True, fill_nulls=True)

print(f"✓ {len(df)} registros procesados")
```

---

## 📂 Estructura nueva (sin alterar la existente)

```
ClimAPI/
├── src/
│   ├── data_loaders/     ← 🆕 NUEVO
│   │   ├── json_loader.py      # Parsea APIs: Meteoblue, OpenMeteo, OpenWeather
│   │   ├── file_loader.py      # CSV, TXT, Excel
│   │   └── unified_loader.py   # Punto único de entrada
│   │
│   ├── validators/       ← 🆕 NUEVO
│   │   └── data_validator.py   # Validación de rangos + limpieza
│   │
│   ├── pipelines/        ← 🆕 NUEVO
│   │   └── climate_pipeline.py # Orquesta: Load → Validate → Clean
│   │
│   ├── data_sources/     ← Original (sin cambios)
│   ├── processors/       ← Original (sin cambios)
│   └── visualizers/      ← Original (sin cambios)
│
├── ejemplo_procesamiento.py  ← Demo con 5 opciones
├── verificar_pipeline.py     ← Comprobación del sistema
└── GUIA_PROCESAMIENTO_DATOS.md ← Documentación completa
```

---

## 🎯 Opciones de Uso

### **Opción 1: Lo más básico**
```python
from src.data_loaders import UnifiedDataLoader

df = UnifiedDataLoader("data").load_all()
# Carga TODO: JSON + CSV + TXT en un DataFrame
```

### **Opción 2: Pipeline completo (RECOMENDADO)**
```python
from src.pipelines import ClimateDataPipeline

pipeline = ClimateDataPipeline("data")
df = pipeline.execute(
    validate=True,        # Eliminar outliers
    fill_nulls=True,     # Rellenar nulos
    remove_outliers=True # Validar rangos
)
```

### **Opción 3: Por ubicación**
```python
df_bogota = pipeline.execute_by_location("Bogota")
df_medellin = pipeline.execute_by_location("Medellín")
```

### **Opción 4: Por fuente climática**
```python
df_meteoblue = pipeline.execute_by_source("meteoblue")
df_openmeteo = pipeline.execute_by_source("openmeteo")
```

---

## 📊 Columnas Generadas

Después de procesar, obtienes:

```
timestamp              → Fecha/Hora
temperature_C          → Temperatura (°C)
windspeed_ms          → Velocidad del viento (m/s)
winddirection_deg     → Dirección del viento (°)
precipitation_mm      → Precipitación (mm)
humidity_percent      → Humedad relativa (%)
pressure_hPa          → Presión atmosférica (hPa)
location              → Ubicación (Bogota, Medellín, etc)
source                → Fuente (meteoblue, openmeteo, etc)
```

---

## 🔧 Características Principales

### **Data Loaders** - Parsea múltiples formatos
- ✅ JSON de APIs (Meteoblue, OpenMeteo, OpenWeatherMap)
- ✅ CSV con detección automática de separadores
- ✅ TXT y Excel
- ✅ Consolidación automática en un DataFrame

### **Validators** - Limpieza inteligente
- ✅ Detección de outliers (temperatura -50 a 60°C, etc)
- ✅ Rellenado de nulos (forward, lineal, media, drop)
- ✅ Detección de duplicados
- ✅ Análisis de calidad de datos

### **Pipelines** - Orquestación completa
- ✅ Carga automática de datos
- ✅ Validación de rangos realistas
- ✅ Limpieza y transformación
- ✅ Resampling temporal (horario, diario, etc)
- ✅ Exportación en CSV/Parquet

---

## 💡 Ejemplo Completo

```python
from src.pipelines import ClimateDataPipeline
from src.data_loaders import UnifiedDataLoader

# 1. Crear pipeline
pipeline = ClimateDataPipeline("data")

# 2. Procesar todos los datos
df = pipeline.execute(
    validate=True,
    fill_nulls=True,
    remove_outliers=True
)

# 3. Análisis básicos
print(f"Registros: {len(df)}")
print(f"Columnas: {list(df.columns)}")

# 4. Estadísticas por ubicación
for location in UnifiedDataLoader.get_available_locations("data"):
    df_loc = df[df['location'] == location]
    print(f"\n{location}:")
    print(f"  Temperatura: {df_loc['temperature_C'].mean():.1f}°C promedio")
    print(f"  Viento: {df_loc['windspeed_ms'].mean():.1f} m/s promedio")
    print(f"  Humedad: {df_loc['humidity_percent'].mean():.0f}% promedio")

# 5. Guardar resultado
pipeline.save_processed(df)
# Genera: data/processed/clima_procesado_YYYYMMDD_HHMMSS.csv
```

---

## 📈 Casos de Uso Reales

### **Análisis temporal**
```python
df = pipeline.execute(resample_freq='1H')  # Horario
df['fecha'] = df['timestamp'].dt.date
df['hora'] = df['timestamp'].dt.hour

temp_por_hora = df.groupby('hora')['temperature_C'].agg(['mean', 'min', 'max'])
```

### **Comparación entre ciudades**
```python
ciudades = UnifiedDataLoader.get_available_locations("data")

resultados = {}
for ciudad in ciudades:
    df_ciudad = pipeline.execute_by_location(ciudad)
    resultados[ciudad] = {
        'temp_prom': df_ciudad['temperature_C'].mean(),
        'humedad_prom': df_ciudad['humidity_percent'].mean(),
        'lluvia_total': df_ciudad['precipitation_mm'].sum(),
    }

import pandas as pd
df_resumen = pd.DataFrame(resultados).T
print(df_resumen)
```

### **Detección de anomalías**
```python
from src.validators import DataValidator

df = pipeline.execute(validate=False)

# Encontrar temperaturas anormales
temp_anomalas = df[
    (df['temperature_C'] < -50) | (df['temperature_C'] > 60)
]

print(f"Anomalías detectadas: {len(temp_anomalas)}")
```

---

## ✨ Ventajas de esta implementación

| Aspecto | Beneficio |
|--------|-----------|
| **Modular** | Cada componente es independiente |
| **No invasivo** | No toca código existente |
| **Escalable** | Fácil de extender con nuevas fuentes |
| **Documentado** | Guía completa incluida |
| **Testeable** | Cada módulo se puede probar por separado |
| **Performante** | Caching y optimizaciones built-in |

---

## 📚 Próximos Pasos

### **Fase 1: Experimentar** (Ya lista)
```bash
python ejemplo_procesamiento.py
```

### **Fase 2: Análisis Exploratorio** (EDA)
```python
import pandas as pd

df = pipeline.execute()

# Estadísticas
print(df.describe())

# Correlaciones
numeric = df.select_dtypes(include=['number']).columns
print(df[numeric].corr())

# Visualizar
df.plot(x='timestamp', y=['temperature_C', 'humidity_percent'])
```

### **Fase 3: Machine Learning** (Futuro)
```python
# Predicción de temperatura
from sklearn.ensemble import RandomForestRegressor

X = df[['humidity_percent', 'pressure_hPa', 'windspeed_ms']]
y = df['temperature_C']

model = RandomForestRegressor()
model.fit(X, y)
```

### **Fase 4: Dashboard Dinámico** (Integración con Streamlit)
```python
# Reutilizar el pipeline en streamlit
import streamlit as st
from src.pipelines import ClimateDataPipeline

pipeline = ClimateDataPipeline("data")
df = pipeline.execute()

st.dataframe(df)
st.line_chart(df.set_index('timestamp')['temperature_C'])
```

---

## 🔗 Archivos clave

| Archivo | Propósito |
|---------|----------|
| [GUIA_PROCESAMIENTO_DATOS.md](GUIA_PROCESAMIENTO_DATOS.md) | Documentación detallada |
| [ejemplo_procesamiento.py](ejemplo_procesamiento.py) | Demo con 5 casos de uso |
| [verificar_pipeline.py](verificar_pipeline.py) | Test del sistema |
| `src/data_loaders/` | Importar datos |
| `src/validators/` | Limpiar y validar |
| `src/pipelines/` | Orquestar todo |

---

## 🆘 Soporte Rápido

**"¿Cómo cargo mis datos?"**
```python
from src.pipelines import ClimateDataPipeline
df = ClimateDataPipeline("data").execute()
```

**"¿Cómo limpio nulos?"**
```python
from src.validators import DataValidator
df = DataValidator.fill_missing(df, method='linear')
```

**"¿Cómo exporto los datos?"**
```python
df.to_csv('datos_limpios.csv', index=False)
df.to_parquet('datos_limpios.parquet')
```

**"¿Dónde están mis datos procesados?"**
```
data/processed/clima_procesado_*.csv  (se genera automáticamente)
```

---

## 📞 ¿Necesitas ayuda?

Ejecuta el verificador:
```bash
python verificar_pipeline.py
```

Lee la guía:
```bash
Abre: GUIA_PROCESAMIENTO_DATOS.md
```

Ve el ejemplo:
```bash
python ejemplo_procesamiento.py
```

---

## 🎉 ¡Lista para usar!

Tu sistema de ciencia de datos está listo. Puedes:

✅ Cargar datos de múltiples fuentes
✅ Validar y limpiar automáticamente
✅ Procesar en batch o por ubicación
✅ Exportar en múltiples formatos
✅ Integrar con análisis y ML

¡Adelante con tu proyecto ClimAPI! 🚀
