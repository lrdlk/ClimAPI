# 📊 Guía Rápida del Dashboard

## 🚀 Inicio Inmediato

```bash
python main.py dashboard
```

Esto abrirá automáticamente el dashboard en: **http://localhost:8501**

---

## 📑 Modos del Dashboard

### 1. 📊 Tiempo Real
**Para ver datos meteorológicos en vivo**

- Selecciona una ubicación del dropdown (Medellín, Bogotá, Cali, etc.)
- Visualiza datos de múltiples fuentes:
  - Open-Meteo (siempre disponible)
  - SIATA Medellín (para Medellín)
  - OpenWeatherMap (si tienes API key)
  - MeteoBlue (si tienes API key)
  - Radar IDEAM (si tienes acceso)

**Características:**
- Status indicators para cada fuente
- Gráficos interactivos con Plotly
- Estadísticas agregadas
- Datos actualizados cada 15 minutos (caché TTL)

---

### 2. 📈 Datos Históricos
**Para analizar datos pasados desde archivos CSV**

- Selecciona un archivo CSV del dropdown
- Filtra por rango de fechas
- Visualiza 4 tipos de gráficos:
  - 🌡️ Temperatura (mín/máx/promedio)
  - 💧 Humedad relativa
  - 🌧️ Precipitación
  - 💨 Velocidad del viento

**Características:**
- Estadísticas descriptivas (media, desv. est., cuartiles)
- Exporta datos filtrados a CSV
- Filtros interactivos de fechas

---

### 3. 📋 Comparativa
**Para comparar fuentes de datos lado a lado**

- Selecciona una ubicación
- Visualiza cómo diferentes fuentes reportan el mismo dato
- Identifica inconsistencias o diferencias
- Útil para validar datos

**Información mostrada:**
- Temperatura por fuente
- Humedad por fuente
- Diferencias entre fuentes
- Tiempo de respuesta de cada una

---

### 4. ℹ️ Información
**Para ver métricas del sistema**

- **Cache Manager Stats**: Información sobre cachés activos
  - Ubicaciones en caché
  - Tamaño total
  - TTL configurado
  
- **Aggregator Status**: Estado de fuentes conectadas
  - Fuentes disponibles
  - Errores recientes
  
- **Data Viewer**: Visor JSON de datos raw
  - Inspecciona estructura de datos
  - Verifica tipos de campos
  - Debug de problemas

---

## ⚙️ Configuración

### Ubicaciones Disponibles
Por defecto: **Medellín, Bogotá, Cali**

Puedes agregar más editando la variable `LOCATIONS` en `dashboard/app.py`:

```python
LOCATIONS = {
    "Medellín": {"lat": 6.2476, "lon": -75.5679},
    "Bogotá": {"lat": 4.7110, "lon": -74.0721},
    "Cali": {"lat": 3.4372, "lon": -76.5069},
    # Agrega más aquí
}
```

### API Keys (Opcional)
Para activar más fuentes de datos, agrega variables de entorno:

```bash
# Bash/Zsh
export OPENWEATHERMAP_API_KEY="tu_key_aqui"
export METEOBLUE_API_KEY="tu_key_aqui"

# PowerShell
$env:OPENWEATHERMAP_API_KEY = "tu_key_aqui"
$env:METEOBLUE_API_KEY = "tu_key_aqui"
```

---

## 📁 Archivos Históricos (CSV)

El dashboard busca archivos CSV en la carpeta `data/`:

```
data/
├── weather_medellin_20251208_033340.csv
├── weather_bogota_20251208_033341.csv
├── weather_cali_20251208_033342.csv
└── weather_data.csv
```

**Formato esperado:**
```
timestamp,temperature,humidity,precipitation,wind_speed
2025-12-08 10:00:00,22.5,65.3,0.0,3.2
2025-12-08 11:00:00,23.1,62.1,0.0,3.5
```

---

## 🔧 Combinaciones de Ejecución

### Solo Dashboard
```bash
python main.py dashboard
```

### API + Dashboard (en paralelo)
```bash
# Terminal 1
python main.py api

# Terminal 2
python main.py dashboard
```

Dashboard + API = Mayor funcionalidad:
- Dashboard consume datos de la API
- API cacheador centralizado
- Mejor rendimiento en múltiples requests

### Ejecutar Tests del Dashboard
```bash
python dashboard/test_integration.py
```

---

## 📊 Uso Práctico

### Monitoreo Meteorológico
1. Abre modo "Tiempo Real"
2. Selecciona tu ubicación
3. Observa métricas en vivo
4. Cambia la ubicación para comparar

### Análisis Histórico
1. Abre modo "Datos Históricos"
2. Selecciona un archivo CSV
3. Filtra por período
4. Exporta datos de interés

### Validación de Datos
1. Abre modo "Comparativa"
2. Compara múltiples fuentes
3. Identifica anomalías
4. Documenta discrepancias

### Debugging
1. Abre modo "Información"
2. Verifica Cache Manager Stats
3. Inspecciona JSON raw
4. Confirma fuentes activas

---

## 🐛 Troubleshooting

### Dashboard no abre
```bash
# Reinstala Streamlit
pip install streamlit==1.31.1 --force-reinstall

# O ejecuta el diagnóstico
python main.py help
```

### Datos no se cargan en Tiempo Real
1. Verifica conexión a internet
2. Abre modo "Información" → Aggregator Status
3. Revisa si Open-Meteo está disponible
4. Comprueba si hay errores en logs

### CSV no aparece en dropdown
1. Verifica que archivos están en `data/`
2. Confirma que tienen extension `.csv`
3. Revisa que Streamlit tiene permisos de lectura
4. Recarga la página (Ctrl+F5)

### Rendimiento lento
1. El caché está rellenando (espera 30 segundos)
2. Reduce número de ubicaciones
3. Cierra pestaña "Información" si la inspección es lenta
4. Verifica recursos del sistema (CPU, RAM)

---

## 💡 Tips & Tricks

- **Atajos Streamlit**: 
  - `C` = Borrar caché
  - `R` = Recargar
  - `Ctrl+M` = Temas

- **Mejor visualización**: Usa el modo "wide" (arriba-derecha)

- **CSV personalizado**: Coloca tu archivo en `data/` y recarga

- **Comparativas rápidas**: Modo "Comparativa" es más rápido que cambiar ubicación

- **JSON viewer**: Perfecto para debugging de estructuras de datos

---

## 📚 Archivos Relacionados

- **Main logic**: `dashboard/app.py`
- **Configuration**: `dashboard/.streamlit/config.toml`
- **Tests**: `dashboard/test_integration.py`
- **Backend API**: `backend/app/main.py`
- **Aggregator**: `backend/app/services/aggregator.py`
- **Cache Manager**: `backend/app/services/cache_manager.py`

---

**¡Disfruta del Dashboard! 🌤️**

Para más detalles técnicos, consulta:
- `dashboard/README.md` - Documentación técnica completa
- `INTEGRATION_STATUS.md` - Estado de integración
- `ARCHITECTURE.md` - Arquitectura del proyecto
