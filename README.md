# 🌦️ CLIMAPI - Sistema Integrado de Consulta de Datos Climáticos

Sistema completo para consultar y procesar datos climáticos de múltiples fuentes en Colombia.

## 🚀 Despliegue en Streamlit Cloud

**¿Quieres desplegar el dashboard?** Ver guías de despliegue:
- 🚀 [**QUICK_START_DEPLOY.md**](QUICK_START_DEPLOY.md) - Inicio rápido (10 min)
- 📦 [**DEPLOYMENT_STREAMLIT.md**](DEPLOYMENT_STREAMLIT.md) - Guía completa
- 📊 [**INFORME_DESPLIEGUE_STREAMLIT.md**](INFORME_DESPLIEGUE_STREAMLIT.md) - Análisis técnico

---

## 📋 Tabla de Contenidos
- [Descripción](#descripción)
- [🗺️ Roadmap del Proyecto](#roadmap)
- [Fuentes de Datos](#fuentes-de-datos)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Uso](#uso)
- [Posibles Fallas y Soluciones](#posibles-fallas-y-soluciones)
- [Normalización de Datos](#normalización-de-datos)

---

## 🎯 Descripción

CLIMAPI es un sistema integrado que permite consultar y procesar datos meteorológicos de múltiples fuentes:

- **Meteoblue**: Pronósticos detallados con meteogramas visuales
- **Open-Meteo**: API gratuita con pronósticos y datos históricos
- **OpenWeatherMap**: Clima actual, pronóstico 5 días y calidad del aire
- **Meteosource**: API freemium con datos actuales y pronósticos detallados
- **IDEAM**: Datos de radares meteorológicos desde AWS
- **SIATA**: Datos históricos meteorológicos de Medellín

---

## 🗺️ Roadmap

**📊 Estado del Proyecto: 27% completado**

El proyecto sigue un roadmap estructurado de 8 etapas, desde la recolección de datos hasta el despliegue con MLflow. 

### Progreso Actual
- ✅ **Recolección de datos** (75%) - 6 APIs integradas
- 🔄 **Procesamiento y limpieza** (20%) - En progreso
- ✅ **Dashboard Streamlit** (80%) - Implementado

### Próximos Hitos
1. Normalización de datos y esquemas comunes
2. Análisis exploratorio y feature engineering
3. Entrenamiento de modelos con MLflow
4. API REST con FastAPI
5. Despliegue en producción

📄 **Ver roadmap completo:** [ROADMAP.md](ROADMAP.md)  
🔗 **Roadmap interactivo:** [Phind Interactive](https://interactive.phind.com/streaming-preview/session_1765509468704/index.html)

---

## 🌐 Fuentes de Datos

### 1. Meteoblue
- **Tipo**: API comercial (requiere API key + secret)
- **Datos**: Pronósticos hasta 7 días, meteogramas, múltiples variables
- **Formato**: JSON + PNG (imágenes)
- **Almacenamiento**: `data/data_meteoblue/` y `data/images_meteo_blue/`
- **Notebook**: No tiene notebook dedicado
- **Cliente**: `src/data_sources/meteoblue.py`

### 2. Open-Meteo
- **Tipo**: API gratuita (sin API key)
- **Datos**: Pronósticos 1-16 días, datos históricos desde 1940
- **Formato**: JSON + CSV
- **Almacenamiento**: `data/data_openmeteo/`
- **Notebook**: No tiene notebook dedicado
- **Cliente**: `src/data_sources/open_meteo.py`

### 3. OpenWeatherMap
- **Tipo**: API freemium (plan gratuito disponible)
- **Datos**: Clima actual, pronóstico 5 días (cada 3h), calidad del aire
- **Formato**: JSON
- **Almacenamiento**: `data/data_openweathermap/`
- **Notebook**: No tiene notebook dedicado
- **Cliente**: `src/data_sources/openweather.py`

### 4. Meteosource
- **Tipo**: API freemium (plan gratuito con 400 llamadas/día)
- **Datos**: Clima actual, pronóstico horario (hasta 7 días), pronóstico diario (hasta 14 días)
- **Variables**: Temperatura, sensación térmica, humedad, viento, precipitación, presión, visibilidad
- **Formato**: JSON
- **Almacenamiento**: `data/data_meteosource/`
- **Notebook**: No tiene notebook dedicado
- **Cliente**: `src/data_sources/Meteosource.py`
- **Ventajas**: Usa place_id (nombres de ciudad simples), respuesta rápida, buena cobertura

### 5. IDEAM - Radares Meteorológicos
- **Tipo**: AWS Open Data (público, sin credenciales)
- **Datos**: Datos de radar nivel 2 (4 radares disponibles)
- **Radares**: Barrancabermeja, Guaviare, Munchique, Carimagua
- **Formato**: Archivos binarios comprimidos
- **Almacenamiento**: `data/Radar_IDEAM/`
- **Notebook**: `notebooks/API_IDEAM.ipynb`
- **Cliente**: `src/data_sources/ideam_radar_downloader.py`
- **Procesadores**: `src/processors/radar_*.py`

### 6. SIATA - Sistema de Alerta Temprana de Medellín
- **Tipo**: Datos públicos web scraping
- **Datos**: Datos históricos meteorológicos de Medellín
- **Formato**: TXT, CSV, XLSX, JSON
- **Almacenamiento**: `data/siata_historico/`
- **Notebook**: `notebooks/SIATA_Historico.ipynb`
- **Cliente**: `src/data_sources/siata_cliente.py`

---

## 📁 Estructura del Proyecto

```
ClimApi/
├── main.py                          # ✅ Script principal integrado
├── README.md                        # ✅ Documentación completa
├── requirements.txt                 # Dependencias
├── .env.example                     # Plantilla de configuración
├── .env                            # Configuración (NO subir a git)
│
├── config/                          # Configuraciones
│
├── data/                            # Datos climáticos
│   ├── data_meteoblue/             # JSON de Meteoblue
│   ├── images_meteo_blue/          # Meteogramas PNG
│   ├── data_openmeteo/             # CSV/JSON de Open-Meteo
│   ├── data_openweathermap/        # JSON de OpenWeatherMap
│   ├── data_meteosource/           # JSON de Meteosource
│   ├── Radar_IDEAM/                # Datos de radares
│   │   ├── Barrancabermeja/
│   │   ├── Guaviare/
│   │   ├── Munchique/
│   │   └── Carimagua/
│   └── siata_historico/            # Datos históricos SIATA
│       ├── precipitacion/
│       ├── temperatura/
│       └── otros/
│
├── logs/                            # Logs de operaciones
│   ├── ideam/
│   └── siata/
│
├── notebooks/                       # Jupyter Notebooks
│   ├── API_IDEAM.ipynb             # Exploración IDEAM
│   └── SIATA_Historico.ipynb       # Exploración SIATA
│
├── src/                             # Código fuente
│   ├── data_sources/               # Clientes de APIs
│   │   ├── meteoblue.py
│   │   ├── open_meteo.py
│   │   ├── openweather.py
│   │   ├── Meteosource.py
│   │   ├── ideam_radar_downloader.py
│   │   └── siata_cliente.py
│   │
│   ├── processors/                 # Procesadores de datos
│   │   ├── radar_processor.py
│   │   ├── radar_advanced_processor.py
│   │   └── radar_raw_processor.py
│   │
│   └── visualizers/                # Visualizaciones (vacío)
│
├── tests/                          # Tests (vacío)
│
└── visualizaciones/                # Visualizaciones generadas
    └── mapa_radares_ideam.html
```

---

## 🚀 Instalación

### Prerequisitos
- Python 3.8 o superior
- pip (gestor de paquetes Python)
- Git (opcional)

### Pasos

1. **Clonar o descargar el repositorio**
```bash
cd ClimApi
```

2. **Crear entorno virtual (recomendado)**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Instalar dependencias opcionales para procesamiento de radar**
```bash
# Si vas a procesar datos de radar (avanzado)
pip install arm-pyart wradlib netCDF4 xarray
```

---

## ⚙️ Configuración

### 1. Crear archivo de configuración

Copia el archivo de ejemplo:
```bash
cp .env.example .env
```

### 2. Configurar API Keys

Edita el archivo `.env` con tus credenciales:

```env
# Meteoblue (requiere registro en https://www.meteoblue.com/en/weather-api)
METEOBLUE_API_KEY=tu_api_key
METEOBLUE_SHARED_SECRET=tu_shared_secret

# OpenWeatherMap (registro gratuito en https://openweathermap.org/api)
OPENWEATHER_API_KEY=tu_api_key

# Meteosource (registro gratuito en https://www.meteosource.com)
METEOSOURCE_API_KEY=tu_api_key

# Open-Meteo (no requiere API key)
# IDEAM (no requiere credenciales)
# SIATA (no requiere credenciales)
```

### 3. APIs sin configuración requerida

- **Open-Meteo**: Totalmente gratuito, sin API key
- **IDEAM**: Datos públicos en AWS, sin credenciales
- **SIATA**: Web scraping de datos públicos

### 4. Límites de APIs gratuitas

- **Meteosource**: 400 llamadas/día en plan gratuito
- **OpenWeatherMap**: 1,000 llamadas/día en plan gratuito
- **Open-Meteo**: Sin límite de llamadas
- **IDEAM/SIATA**: Sin límite (datos públicos)

---

## 📖 Uso

### 🎨 Dashboard Streamlit (Recomendado)

El dashboard interactivo ofrece la mejor experiencia visual:

```bash
streamlit run dashboard.py
```

Características del dashboard:
- 🏠 **Inicio**: Vista general con estadísticas y actividad reciente
- ✅ **Verificación APIs**: Verifica el estado de todas las APIs en tiempo real
- 📊 **Consultas Realizadas**: Visualiza y analiza consultas previas con gráficos interactivos
- 🔍 **Nueva Consulta**: Realiza nuevas consultas con formularios intuitivos
- 📁 **Datos por API**: Explora datos guardados organizados por fuente

El dashboard se abrirá automáticamente en tu navegador en `http://localhost:8501`

### Modo Interactivo (Terminal)

Ejecuta el script principal:
```bash
python main.py
```

El menú interactivo te permite:
1. Consulta completa (todas las APIs)
2. Consultar Meteoblue individual
3. Consultar Open-Meteo pronóstico
4. Consultar Open-Meteo histórico
5. Consultar OpenWeatherMap
6. Consultar Meteosource
7. Consultar radares IDEAM
8. Listar radares disponibles
9. Descargar datos SIATA históricos
10. Salir

### Uso Programático

```python
from main import ClimAPIManager

# Inicializar gestor
manager = ClimAPIManager()

# Consulta completa para Medellín
manager.consulta_completa(
    lat=6.245,
    lon=-75.5715,
    location_name="Medellín",
    asl=1495
)

# Consulta específica Open-Meteo
forecast = manager.consultar_openmeteo(6.245, -75.5715, "Medellín")

# Consulta Meteosource (usa place_id)
data = manager.consultar_meteosource("medellin", "Medellín")

# Datos históricos
manager.consultar_openmeteo_historico(
    lat=6.245,
    lon=-75.5715,
    location_name="Medellín",
    start_date="2024-12-01",
    end_date="2024-12-13"
)

# Listar radares IDEAM
manager.listar_radares_ideam()

# Descargar datos SIATA
manager.descargar_datos_siata(max_depth=2)
```

### Uso de Notebooks

#### IDEAM Radar
```bash
jupyter notebook notebooks/API_IDEAM.ipynb
```

Incluye:
- Exploración de radares disponibles
- Descarga de datos de radar
- Procesamiento básico de archivos
- Visualización de cobertura

#### SIATA Histórico
```bash
jupyter notebook notebooks/SIATA_Historico.ipynb
```

Incluye:
- Web scraping de datos históricos
- Organización por categorías
- Análisis exploratorio de datos
- Generación de resúmenes

---

## ⚠️ Posibles Fallas y Soluciones

### 1. Error de Autenticación en Meteoblue

**Error:**
```
HTTP 401 Unauthorized
```

**Causa:** API key o shared secret incorrecto/expirado

**Solución:**
- Verifica que las credenciales en `.env` sean correctas
- Asegúrate de copiar el shared secret completo (sin espacios)
- Verifica que tu cuenta Meteoblue esté activa
- Revisa el límite de llamadas de tu plan

### 2. Error de Rate Limiting (Too Many Requests)

**Error:**
```
HTTP 429 Too Many Requests
```

**Causa:** Excediste el límite de llamadas a la API

**Solución:**
- Espera antes de realizar más consultas
- Implementa delays entre llamadas: `time.sleep(1)`
- Considera usar un plan de pago con más llamadas
- Usa cache para evitar consultas repetidas

### 3. Datos IDEAM No Disponibles

**Error:**
```
⚠️  No se encontraron archivos para Radar en fecha
```

**Causa:** Los datos IDEAM tienen 24 horas de delay

**Solución:**
- Consulta datos de ayer o anteriores
- Usa: `fecha = datetime.now() - timedelta(days=1)`
- Verifica que el radar esté operativo
- Intenta con diferentes fechas

### 4. Error Meteosource Place ID Inválido

**Error:**
```
HTTP 404 Not Found
```

**Causa:** Place ID no existe o está mal escrito

**Solución:**
- Usa nombres de ciudades en minúsculas sin acentos: `medellin`, `bogota`, `cali`
- Verifica el place_id en la documentación de Meteosource
- Prueba con variaciones: `medellin`, `medellín`, `medellin_co`
- Usa coordenadas si el place_id no funciona

### 5. Timeout en SIATA

**Error:**
```
requests.exceptions.Timeout
```

**Causa:** Servidor SIATA lento o sobrecargado

**Solución:**
- Aumenta el timeout: `self.timeout = 60`
- Reduce la profundidad de exploración: `max_depth=1`
- Intenta en horarios de menor tráfico
- Aumenta el delay entre peticiones: `self.delay = 2`

### 5. Dependencias Faltantes

**Error:**
```
ModuleNotFoundError: No module named 'xxx'
```

**Solución:**
```bash
pip install -r requirements.txt

# Si faltan dependencias de radar
pip install arm-pyart wradlib netCDF4 xarray
```

### 7. Permisos de Escritura

**Error:**
```
PermissionError: [Errno 13] Permission denied
```

**Causa:** Sin permisos para escribir en directorios

**Solución:**
- Ejecuta con permisos adecuados
- Verifica que los directorios `data/` y `logs/` tengan permisos de escritura
```bash
chmod -R 755 data logs
```

### 8. Encoding de Caracteres

**Error:**
```
UnicodeDecodeError / UnicodeEncodeError
```

**Causa:** Problemas con caracteres especiales (acentos)

**Solución:**
- Usa `encoding='utf-8'` al abrir archivos
- Asegúrate de que `.env` esté en UTF-8
- En Windows, usa `chcp 65001` en CMD

### 9. AWS S3 Access Denied

**Error:**
```
botocore.exceptions.ClientError: Access Denied
```

**Causa:** Problemas con bucket IDEAM

**Solución:**
- Verifica que estés usando: `bucket_name = 's3-radaresideam'`
- Usa configuración sin firma: `Config(signature_version=UNSIGNED)`
- Verifica tu conexión a internet
- Intenta con otra región: `region_name='us-east-1'`

### 10. Pandas/NumPy Compatibility

**Error:**
```
AttributeError: module 'pandas' has no attribute 'xxx'
```

**Causa:** Versiones incompatibles

**Solución:**
```bash
pip install --upgrade pandas numpy
pip install pandas==2.0.0 numpy==1.24.0
```

### 11. Memoria Insuficiente

**Error:**
```
MemoryError
```

**Causa:** Procesamiento de archivos grandes de radar

**Solución:**
- Procesa archivos en lotes más pequeños
- Limita el número de archivos: `limite=10`
- Libera memoria: `del variable; gc.collect()`
- Aumenta la memoria virtual del sistema

---

## 📊 Normalización de Datos

### Objetivo

Crear un esquema unificado para datos de diferentes fuentes, facilitando análisis comparativos y machine learning.

### Paso 1: Organizar Datos por Tipo

Crea la siguiente estructura en `data/normalized/`:

```
data/normalized/
├── weather_current/          # Clima actual
│   ├── meteoblue/
│   ├── openmeteo/
│   ├── openweather/
│   └── meteosource/
│
├── weather_forecast/         # Pronósticos
│   ├── meteoblue/
│   ├── openmeteo/
│   ├── openweather/
│   └── meteosource/
│
├── weather_historical/       # Datos históricos
│   ├── openmeteo/
│   └── siata/
│
├── radar/                    # Datos de radar
│   └── ideam/
│
└── air_quality/             # Calidad del aire
    └── openweather/
```

**Comando:**
```bash
mkdir -p data/normalized/{weather_current,weather_forecast,weather_historical,radar,air_quality}/{meteoblue,openmeteo,openweather,meteosource,siata,ideam}
```

### Paso 2: Definir Esquema Común

#### Esquema de Clima (weather_schema.json)

```json
{
  "location": {
    "name": "string",
    "latitude": "float",
    "longitude": "float",
    "elevation": "int"
  },
  "timestamp": "ISO8601 datetime",
  "source": "string (meteoblue|openmeteo|openweather)",
  "data": {
    "temperature": {
      "value": "float (°C)",
      "min": "float",
      "max": "float"
    },
    "humidity": "float (%)",
    "pressure": "float (hPa)",
    "wind": {
      "speed": "float (km/h)",
      "direction": "int (degrees)",
      "gust": "float (km/h)"
    },
    "precipitation": {
      "amount": "float (mm)",
      "probability": "float (%)"
    },
    "clouds": "float (%)",
    "visibility": "float (km)"
  }
}
```

#### Esquema de Pronóstico (forecast_schema.json)

```json
{
  "location": {...},
  "generated_at": "ISO8601 datetime",
  "source": "string",
  "forecast": [
    {
      "datetime": "ISO8601 datetime",
      "data": {...}  // Mismo esquema que weather
    }
  ]
}
```

#### Esquema de Datos Históricos (historical_schema.json)

Similar al forecast pero con:
- `period`: {"start": "date", "end": "date"}
- Más variables disponibles

### Paso 3: Script de Normalización

Crea `src/processors/data_normalizer.py`:

```python
import pandas as pd
import json
from pathlib import Path
from datetime import datetime

class DataNormalizer:
    """Normaliza datos de diferentes fuentes"""
    
    def __init__(self):
        self.schemas = self._load_schemas()
        self.output_dir = Path("data/normalized")
    
    def normalize_meteoblue(self, data):
        """Normaliza datos de Meteoblue"""
        # Implementar transformación
        pass
    
    def normalize_openmeteo(self, data):
        """Normaliza datos de Open-Meteo"""
        pass
    
    def normalize_openweather(self, data):
        """Normaliza datos de OpenWeatherMap"""
        pass
    
    def normalize_meteosource(self, data):
        """Normaliza datos de Meteosource"""
        pass
    
    def normalize_all(self):
        """Normaliza todos los datos disponibles"""
        pass
```

### Paso 4: Unidades Estandarizadas

| Variable | Unidad Estándar | Conversiones Comunes |
|----------|----------------|----------------------|
| Temperatura | °C | F = (C × 9/5) + 32 |
| Velocidad viento | km/h | m/s = km/h / 3.6 |
| Presión | hPa | 1 hPa = 1 mbar |
| Precipitación | mm | 1 inch = 25.4 mm |
| Visibilidad | km | miles = km × 0.621 |

### Paso 5: Limpieza de Datos

#### Valores Faltantes

```python
# Estrategias por variable
strategies = {
    "temperature": "interpolate",  # Interpolar
    "precipitation": "fill_zero",   # Llenar con 0
    "wind_speed": "forward_fill",   # Propagar anterior
    "humidity": "mean"              # Media del día
}
```

#### Outliers

```python
# Límites razonables para Colombia
limits = {
    "temperature": (-10, 45),  # °C
    "humidity": (0, 100),      # %
    "wind_speed": (0, 200),    # km/h
    "pressure": (800, 1100)    # hPa
}
```

### Paso 6: Formato de Salida

#### CSV (para análisis)

```
date,source,location,temperature,humidity,precipitation
2024-12-13T12:00:00,openmeteo,Medellín,24.5,65,0.0
```

#### Parquet (para Big Data)

```python
df.to_parquet('data/normalized/weather_2024.parquet',
              compression='snappy',
              index=False)
```

#### HDF5 (para series temporales)

```python
df.to_hdf('data/normalized/weather.h5',
          key='medellin',
          mode='a')
```

### Paso 7: Script de Verificación

Crea `scripts/verify_normalization.py`:

```python
def verify_normalized_data():
    """Verifica integridad de datos normalizados"""
    
    checks = [
        "check_schema_compliance",
        "check_data_ranges",
        "check_temporal_continuity",
        "check_missing_values",
        "check_duplicates"
    ]
    
    for check in checks:
        result = run_check(check)
        print(f"{'✅' if result else '❌'} {check}")
```

### Paso 8: Documentación de Transformaciones

Mantén un registro de transformaciones:

```json
{
  "transformation_log": [
    {
      "date": "2024-12-13",
      "source": "meteoblue",
      "file": "forecast_medellin_20241213.json",
      "transformations": [
        "temperature: F to C conversion",
        "wind_speed: mph to km/h",
        "timestamp: localized to UTC"
      ],
      "records_processed": 168,
      "records_valid": 165,
      "records_dropped": 3
    }
  ]
}
```

---

## 📝 Notas Finales

### Licencias de Datos

- **Meteoblue**: Comercial - Revisar términos de licencia
- **Open-Meteo**: CC BY 4.0 - Atribución requerida
- **OpenWeatherMap**: Revisar plan específico
- **Meteosource**: Revisar términos del plan (gratuito/premium)
- **IDEAM**: Datos públicos colombianos
- **SIATA**: Datos públicos de Medellín

### Buenas Prácticas

1. **Siempre usa `.gitignore`** para excluir:
   - `.env` (credenciales)
   - `data/` (archivos grandes)
   - `.cache/` (cache de requests)
   - `__pycache__/` (bytecode Python)

2. **Respeta rate limits** de las APIs
3. **Documenta** tus transformaciones de datos
4. **Valida** los datos antes de usarlos
5. **Mantén logs** de operaciones importantes

### Próximos Pasos

1. Implementar procesamiento avanzado de radar
2. Crear visualizaciones interactivas
3. Desarrollar modelos de predicción
4. Integrar más fuentes de datos
5. Crear API REST para servir datos

---

## 🤝 Contribuciones

Para contribuir al proyecto:

1. Fork del repositorio
2. Crea una rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -am 'Agrega nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Crea un Pull Request

---

## 📧 Contacto

Para preguntas o sugerencias sobre CLIMAPI.

---

**Última actualización**: Diciembre 2025
**Versión**: 1.0.0
