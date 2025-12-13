# Guía de Uso - IDEAM Visualizer Optimizado

## 📋 Descripción

El visualizador optimizado de radar IDEAM procesa archivos RAW de radar meteorológico y genera **DataFrames trabajables** con análisis completos y gráficas precisas.

## 🆕 Mejoras Principales

### 1. **DataFrame Trabajable con Datos Relevantes**
- ✅ Extracción automática de timestamps de archivos RAW
- ✅ Información meteorológica con PyART (reflectividad, cobertura)
- ✅ Categorización de intensidad (Débil, Moderada, Fuerte, Muy Fuerte)
- ✅ Análisis temporal (hora, periodo del día, día de la semana)
- ✅ Estadísticas completas (tamaño, duración, frecuencia)

### 2. **Gráficas Meteorológicamente Relevantes**
- 📊 **Serie Temporal**: Reflectividad máxima y promedio con referencias de lluvia
- 📈 **Distribución de Intensidad**: Histogramas, boxplots y categorías
- 🕐 **Patrones Temporales**: Actividad por hora, heatmaps, timeline
- 📉 **Dashboard Completo**: Vista integrada de todas las métricas

### 3. **Integración con PyART**
- Lectura nativa de archivos RAW IDEAM
- Extracción de campos meteorológicos (reflectividad, velocidad, ancho espectral)
- Estadísticas avanzadas de reflectividad
- Cálculo de cobertura del radar

## 🚀 Uso Rápido

### Ejemplo Básico

```python
from src.visualizers.ideam_visualizer import IDEAMRadarVisualizer

# Crear visualizador
viz = IDEAMRadarVisualizer()

# Listar radares disponibles
radares = viz.listar_radares()

# Cargar datos (limite=100 para prueba rápida)
df = viz.cargar_datos_radar('Barrancabermeja', limite=100)

# Obtener DataFrame trabajable
df_trabajable = viz.obtener_dataframe_trabajable()
print(df_trabajable.head())

# Estadísticas completas
stats = viz.estadisticas_completas()

# Generar visualizaciones
viz.grafica_resumen_completo(save_path="dashboard.png")
viz.grafica_serie_temporal_reflectividad(save_path="serie_temporal.png")
viz.grafica_distribucion_intensidad(save_path="distribucion.png")
viz.grafica_patron_temporal(save_path="patrones.png")

# Exportar datos
viz.exportar_datos(formato='csv')
viz.exportar_datos(formato='json')
```

## 📊 Estructura del DataFrame

### Columnas Disponibles

```python
df.columns
# ['radar', 'archivo', 'ruta', 'tamaño_bytes', 'tamaño_mb', 
#  'timestamp', 'fecha', 'hora', 'minuto', 'segundo', 'prefijo',
#  'campos_disponibles', 'num_sweeps', 
#  'reflectividad_max', 'reflectividad_mean', 'reflectividad_std',
#  'cobertura_pct', 'dia_semana', 'es_dia', 'periodo', 'intensidad']
```

### Descripción de Campos

| Campo | Descripción | Tipo |
|-------|-------------|------|
| `radar` | Nombre del radar | string |
| `timestamp` | Fecha y hora de captura | datetime |
| `reflectividad_max` | Reflectividad máxima (dBZ) | float |
| `reflectividad_mean` | Reflectividad promedio (dBZ) | float |
| `reflectividad_std` | Desviación estándar (dBZ) | float |
| `cobertura_pct` | Cobertura del radar (%) | float |
| `intensidad` | Categoría (Débil/Moderada/Fuerte/Muy Fuerte) | category |
| `periodo` | Periodo del día (Madrugada/Mañana/Tarde/Noche) | category |
| `tamaño_mb` | Tamaño del archivo (MB) | float |
| `num_sweeps` | Número de barridos del radar | int |

## 📈 Tipos de Gráficas

### 1. Dashboard Completo
```python
viz.grafica_resumen_completo(save_path="dashboard.png")
```
**Incluye:**
- Serie temporal de reflectividad
- Distribución de intensidades (pie chart)
- Actividad por hora
- Estadísticas textuales
- Histograma de reflectividad
- Boxplot de cobertura

### 2. Serie Temporal de Reflectividad
```python
viz.grafica_serie_temporal_reflectividad(save_path="serie.png")
```
**Muestra:**
- Reflectividad máxima y promedio
- Líneas de referencia (20, 40, 50 dBZ)
- Cobertura del radar en el tiempo

### 3. Distribución de Intensidad
```python
viz.grafica_distribucion_intensidad(save_path="distribucion.png")
```
**Incluye:**
- Histograma de reflectividad máxima
- Boxplot de reflectividad promedio
- Reflectividad por periodo del día
- Distribución de categorías de intensidad

### 4. Patrones Temporales
```python
viz.grafica_patron_temporal(save_path="patrones.png")
```
**Muestra:**
- Distribución de archivos por hora
- Timeline con intensidad de color
- Heatmap hora vs fecha
- Reflectividad promedio por hora

## 🔧 Análisis Avanzado

### Filtrado por Intensidad

```python
# Obtener solo eventos fuertes
df_fuertes = df[df['intensidad'].isin(['Fuerte', 'Muy Fuerte'])]
print(f"Eventos fuertes: {len(df_fuertes)}")
```

### Análisis por Periodo

```python
# Reflectividad promedio por periodo
periodo_stats = df.groupby('periodo').agg({
    'reflectividad_max': ['mean', 'max', 'count'],
    'cobertura_pct': 'mean'
})
print(periodo_stats)
```

### Detección de Picos

```python
# Encontrar momentos de mayor intensidad
umbral = df['reflectividad_max'].quantile(0.9)
picos = df[df['reflectividad_max'] > umbral]
print(f"Picos detectados: {len(picos)}")
print(picos[['timestamp', 'reflectividad_max', 'intensidad']])
```

## 📦 Exportación de Datos

### Formatos Disponibles

```python
# CSV (recomendado para análisis)
viz.exportar_datos(formato='csv', ruta='datos_radar.csv')

# JSON (recomendado para APIs)
viz.exportar_datos(formato='json', ruta='datos_radar.json')

# Excel (recomendado para reportes)
viz.exportar_datos(formato='excel', ruta='datos_radar.xlsx')

# Parquet (recomendado para Big Data)
viz.exportar_datos(formato='parquet', ruta='datos_radar.parquet')
```

## 🎯 Casos de Uso

### 1. Análisis de Evento Meteorológico

```python
# Cargar datos del periodo del evento
df = viz.cargar_datos_radar('Barrancabermeja')

# Filtrar por fecha específica
evento = df[df['fecha'] == '2025-12-09']

# Analizar evolución
viz.df_radar = evento  # Reemplazar temporalmente
viz.grafica_serie_temporal_reflectividad()
```

### 2. Comparación de Periodos

```python
# Cargar todos los datos
df = viz.cargar_datos_radar('Barrancabermeja')

# Comparar día vs noche
dia_vs_noche = df.groupby('es_dia').agg({
    'reflectividad_max': 'mean',
    'cobertura_pct': 'mean'
})
print(dia_vs_noche)
```

### 3. Estadísticas Mensuales

```python
# Agregar mes
df['mes'] = df['timestamp'].dt.month
df['año'] = df['timestamp'].dt.year

# Estadísticas por mes
mensual = df.groupby(['año', 'mes']).agg({
    'reflectividad_max': ['mean', 'max'],
    'archivo': 'count'
}).round(2)
print(mensual)
```

## ⚙️ Requisitos

### Instalación de PyART (Recomendado)

```bash
pip install arm-pyart
```

PyART permite:
- Lectura nativa de archivos RAW
- Extracción de campos meteorológicos
- Cálculo de estadísticas avanzadas

### Dependencias Alternativas

Si PyART no está disponible, el visualizador funciona con capacidades limitadas:
- ✅ Extracción de timestamps
- ✅ Análisis de archivos
- ✅ Estadísticas básicas
- ❌ Datos de reflectividad
- ❌ Análisis meteorológico avanzado

## 📝 Notas

### Interpretación de Reflectividad (dBZ)

| Valor (dBZ) | Interpretación | Categoría |
|-------------|----------------|-----------|
| < 20 | Lluvia muy débil o gotas dispersas | Débil |
| 20-40 | Lluvia ligera a moderada | Moderada |
| 40-50 | Lluvia fuerte | Fuerte |
| > 50 | Lluvia muy fuerte, posible granizo | Muy Fuerte |

### Cobertura del Radar

- **100%**: Cobertura completa, todos los bins con datos
- **80-99%**: Cobertura muy buena
- **60-79%**: Cobertura aceptable
- **< 60%**: Cobertura limitada, posibles obstrucciones

## 🐛 Solución de Problemas

### Error: PyART no disponible

```bash
# Instalar PyART
pip install arm-pyart

# Si falla, instalar dependencias primero
pip install numpy scipy matplotlib netCDF4
pip install arm-pyart
```

### Error: No se pueden leer archivos RAW

Verificar que los archivos tienen el formato correcto:
- Prefijo: BAR, CAR, MUN, GUA
- Formato: PREFIXYYMMDDHHMMSS.RAWXXXXX

### Visualizaciones no se generan

```python
# Verificar que hay datos cargados
if viz.df_radar is not None:
    print(f"Datos disponibles: {len(viz.df_radar)} registros")
else:
    print("No hay datos cargados")
```

## 📚 Recursos Adicionales

- [Documentación PyART](https://arm-doe.github.io/pyart/)
- [IDEAM - Datos Abiertos](http://www.ideam.gov.co/)
- [Interpretación de Reflectividad](https://www.weather.gov/jetstream/reflectivity)

## 🔄 Versión

**Versión Optimizada 2.0** - Diciembre 2025

### Cambios respecto a v1.0
- ✅ DataFrames estructurados con pandas
- ✅ Integración con PyART
- ✅ Gráficas meteorológicamente relevantes
- ✅ Categorización de intensidad
- ✅ Análisis temporal avanzado
- ✅ Múltiples formatos de exportación
- ✅ Dashboard completo integrado
