# 📊 Visualizadores de Datos CLIMAPI

Scripts especializados para procesar y visualizar datos de cada API usando **pandas**, **numpy**, **matplotlib** y **sklearn**.

---

## 🎯 Descripción

Cada visualizador es un módulo independiente que:
- ✅ Carga y procesa datos de una API específica
- ✅ Genera estadísticas descriptivas
- ✅ Crea visualizaciones avanzadas
- ✅ Detecta anomalías y outliers
- ✅ Exporta datos procesados

---

## 📁 Scripts Disponibles

### 1. ☁️ `meteoblue_visualizer.py`
**Procesa datos de Meteoblue**

```bash
python src/visualizers/meteoblue_visualizer.py
```

**Funciones principales:**
- `cargar_datos()` - Carga archivos JSON de Meteoblue
- `estadisticas_basicas()` - Estadísticas descriptivas
- `grafico_series_temporales()` - Gráficos de temperatura, precipitación, humedad
- `analisis_correlacion()` - Matriz de correlación entre variables
- `clustering_ciudades()` - K-Means clustering con PCA
- `detectar_outliers()` - Detección de valores atípicos con IQR
- `exportar_procesado()` - Exporta CSV procesado

**Datos generados:**
- `data/images_meteo_blue/series_temporales.png`
- `data/images_meteo_blue/correlacion.png`
- `data/images_meteo_blue/clustering.png`
- `data/processed/meteoblue_processed.csv`

---

### 2. 🌐 `open_meteo_visualizer.py`
**Procesa datos de Open-Meteo**

```bash
python src/visualizers/open_meteo_visualizer.py
```

**Funciones principales:**
- `cargar_datos()` - Carga CSV hourly y daily
- `grafico_temperatura_horaria()` - Patrón de temperatura por hora del día
- `comparacion_ciudades()` - Boxplots y comparaciones entre ciudades
- `prediccion_temperatura()` - Modelo Random Forest para predicción
- `exportar_procesado()` - Exporta CSV procesados

**Datos generados:**
- `data/images/openmeteo_temp_horaria.png`
- `data/images/openmeteo_comparacion.png`
- `data/processed/openmeteo_hourly_processed.csv`
- `data/processed/openmeteo_daily_processed.csv`

---

### 3. 🌤️ `openweather_visualizer.py`
**Procesa datos de OpenWeatherMap**

```bash
python src/visualizers/openweather_visualizer.py
```

**Funciones principales:**
- `cargar_datos()` - Carga JSON (forecast, current, onecall)
- `grafico_temperatura_feels_like()` - Temperatura real vs sensación térmica
- `analisis_viento()` - Rosa de vientos y distribución de velocidad
- `tendencia_temperatura()` - Regresión lineal de tendencia temporal
- `exportar_procesado()` - Exporta CSV procesado

**Datos generados:**
- `data/images/openweather_feels_like.png`
- `data/images/openweather_viento.png`
- `data/images/openweather_tendencia.png`
- `data/processed/openweather_processed.csv`

---

### 4. 🌦️ `meteosource_visualizer.py`
**Procesa datos de Meteosource**

```bash
python src/visualizers/meteosource_visualizer.py
```

**Funciones principales:**
- `cargar_datos()` - Carga JSON hourly y daily
- `grafico_uv_index()` - Análisis de índice UV por hora
- `analisis_visibilidad()` - Relación visibilidad con humedad/precipitación
- `pca_analysis()` - Análisis de componentes principales
- `exportar_procesado()` - Exporta CSV procesado

**Datos generados:**
- `data/images/meteosource_uv.png`
- `data/images/meteosource_visibilidad.png`
- `data/images/meteosource_pca.png`
- `data/processed/meteosource_processed.csv`

---

### 5. 📡 `ideam_visualizer.py`
**Procesa imágenes de radar IDEAM**

```bash
python src/visualizers/ideam_visualizer.py
```

**Funciones principales:**
- `listar_radares()` - Lista radares disponibles
- `cargar_imagenes_radar(radar_name)` - Carga imágenes de un radar
- `visualizar_galeria()` - Galería de imágenes
- `analisis_intensidad()` - Análisis de intensidad de píxeles
- `comparar_imagenes()` - Compara dos imágenes
- `timeline_imagenes()` - Timeline de capturas
- `exportar_metadata()` - Exporta metadata

**Datos generados:**
- `data/images/ideam_galeria_{radar}.png`
- `data/images/ideam_timeline_{radar}.png`
- `data/processed/ideam_radar_metadata.csv`

---

### 6. 🌐 `siata_visualizer.py`
**Procesa datos históricos de SIATA**

```bash
python src/visualizers/siata_visualizer.py
```

**Funciones principales:**
- `cargar_datos()` - Carga CSV históricos
- `grafico_series_temporales()` - Series temporales por estación
- `analisis_outliers()` - Detección con IQR o Isolation Forest
- `comparacion_estaciones()` - Boxplots entre estaciones
- `matriz_correlacion()` - Heatmap de correlaciones
- `exportar_procesado()` - Exporta CSV procesado

**Datos generados:**
- `data/images/siata_series.png`
- `data/images/siata_comparacion.png`
- `data/images/siata_correlacion.png`
- `data/processed/siata_processed.csv`

---

## 🚀 Uso

### Modo Básico
Ejecuta cualquier script directamente:

```bash
python src/visualizers/meteoblue_visualizer.py
```

### Modo Programático
Importa y usa las clases:

```python
from src.visualizers.meteoblue_visualizer import MeteoblueVisualizer

# Crear instancia
viz = MeteoblueVisualizer()

# Cargar datos
df = viz.cargar_datos()

# Generar estadísticas
viz.estadisticas_basicas()

# Crear gráficos
viz.grafico_series_temporales(save_path="salida.png")
viz.analisis_correlacion()
viz.clustering_ciudades(n_clusters=3)

# Exportar procesados
viz.exportar_procesado()
```

---

## 📦 Dependencias

Asegúrate de tener instalado:

```bash
pip install pandas numpy matplotlib seaborn scikit-learn scipy pillow
```

O desde `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

## 📊 Características Comunes

Todos los visualizadores incluyen:

### 1. **Carga Inteligente**
- Detección automática de formatos (JSON, CSV)
- Manejo robusto de errores
- Logging detallado

### 2. **Procesamiento**
- Conversión de tipos de datos
- Creación de features temporales (hora, día, mes, día_semana)
- Cálculo de estadísticas derivadas

### 3. **Visualización**
- Gráficos interactivos con matplotlib/seaborn
- Paletas de colores específicas por API
- Guardado en alta resolución (300 DPI)

### 4. **Machine Learning**
- Normalización con sklearn
- Clustering (K-Means)
- PCA (Análisis de Componentes Principales)
- Detección de outliers (IQR, Isolation Forest)
- Modelos de predicción (Random Forest, Linear Regression)

### 5. **Exportación**
- CSV procesados en `data/processed/`
- Imágenes en `data/images/`
- Metadata estructurada

---

## 🎨 Estilos de Visualización

Cada visualizador tiene su propio estilo:

| Visualizador | Estilo | Paleta |
|--------------|--------|--------|
| Meteoblue | `seaborn-v0_8-darkgrid` | husl |
| Open-Meteo | `seaborn-v0_8-whitegrid` | muted |
| OpenWeatherMap | `ggplot` | Set2 |
| Meteosource | `seaborn-v0_8-dark` | rocket |
| IDEAM Radar | `default` | Blues_r |
| SIATA | `bmh` | Set3 |

---

## 🔍 Análisis Disponibles

### Estadísticas Descriptivas
- Media, mediana, desviación estándar
- Valores mínimos y máximos
- Conteo de registros
- Rango temporal

### Análisis Temporal
- Series de tiempo
- Patrones por hora del día
- Tendencias con regresión lineal
- Estacionalidad

### Análisis Espacial
- Comparación entre ciudades
- Clustering geográfico
- Diferencias regionales

### Machine Learning
- Clustering K-Means
- PCA para reducción dimensional
- Random Forest para predicción
- Isolation Forest para outliers

### Análisis de Correlación
- Matrices de correlación
- Heatmaps
- Identificación de variables relacionadas

---

## 📝 Ejemplo Completo

```python
from src.visualizers.meteoblue_visualizer import MeteoblueVisualizer
from pathlib import Path

# Configurar directorios
Path("data/images_meteo_blue").mkdir(parents=True, exist_ok=True)
Path("data/processed").mkdir(parents=True, exist_ok=True)

# Crear visualizador
viz = MeteoblueVisualizer(data_dir="data/data_meteoblue")

# Pipeline completo
print("🌦️ PIPELINE DE PROCESAMIENTO METEOBLUE")
print("="*60)

# 1. Cargar
df = viz.cargar_datos()

if df is not None:
    # 2. Estadísticas
    stats = viz.estadisticas_basicas()
    
    # 3. Visualizaciones
    viz.grafico_series_temporales(
        ciudad="bogota",
        save_path="data/images_meteo_blue/series_bogota.png"
    )
    
    corr_matrix = viz.analisis_correlacion(
        save_path="data/images_meteo_blue/correlacion.png"
    )
    
    clusters = viz.clustering_ciudades(
        n_clusters=3,
        save_path="data/images_meteo_blue/clustering.png"
    )
    
    # 4. Detección de anomalías
    viz.detectar_outliers()
    
    # 5. Exportar
    viz.exportar_procesado()
    
    print("\n✅ Pipeline completado exitosamente!")
```

---

## 🛠️ Personalización

### Cambiar directorio de datos
```python
viz = MeteoblueVisualizer(data_dir="ruta/personalizada")
```

### Filtrar por ciudad
```python
viz.grafico_series_temporales(ciudad="medellin")
```

### Cambiar número de clusters
```python
viz.clustering_ciudades(n_clusters=5)
```

### Guardar en ubicación específica
```python
viz.grafico_series_temporales(save_path="/ruta/completa/grafico.png")
```

---

## 📈 Roadmap de Visualizadores

### ✅ Completado (v1.0)
- 6 visualizadores especializados
- Procesamiento con pandas/numpy
- Visualizaciones con matplotlib/seaborn
- Modelos sklearn básicos
- Exportación de datos procesados

### 🔄 En desarrollo (v1.1)
- Visualizaciones interactivas con Plotly
- Integración con Streamlit dashboard
- Modelos avanzados (LSTM, XGBoost)
- Reportes automáticos en PDF

### 📋 Planificado (v2.0)
- Visualizador unificado multi-API
- Comparaciones entre APIs
- Dashboard de métricas en tiempo real
- Alertas automáticas de anomalías

---

## 🤝 Contribuir

Para agregar un nuevo visualizador:

1. Crea el archivo en `src/visualizers/nueva_api_visualizer.py`
2. Implementa la clase `NuevaAPIVisualizer`
3. Incluye métodos estándar:
   - `cargar_datos()`
   - `estadisticas_basicas()`
   - `exportar_procesado()`
4. Agrega visualizaciones específicas
5. Actualiza este README

---

## 📞 Soporte

¿Problemas o preguntas? 

- 📖 Consulta [README.md](../../README.md)
- 🗺️ Revisa [ROADMAP.md](../../ROADMAP.md)
- 🎯 Ejecuta `python verificar_dashboard.py`

---

**CLIMAPI** - Sistema Integrado de Datos Climáticos
Diciembre 2025
