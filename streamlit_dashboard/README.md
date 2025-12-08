# ClimAPI Dashboard - Streamlit

Dashboard interactivo para visualización de datos meteorológicos de múltiples fuentes en tiempo real.

## 🌟 Características

- **📊 Agregación de datos de múltiples fuentes:**
  - Open-Meteo (global, gratuito)
  - SIATA (Medellín)
  - OpenWeatherMap (requiere API key)
  - MeteoBlue (requiere API key)
  - Radar IDEAM (Colombia)

- **🔄 Actualización en tiempo real:** Intervalo configurable (5-300 segundos)

- **💾 Caché inteligente:** TTL de 15 minutos para optimizar consultas

- **📈 Visualizaciones interactivas:**
  - Gráficos de estado de fuentes
  - Disponibilidad de datos
  - Estadísticas agregadas
  - Datos en JSON

- **🌍 Ubicaciones predefinidas:**
  - Medellín: (6.2442, -75.5812)
  - Bogotá: (4.7110, -74.0721)
  - Cali: (3.4372, -76.5225)
  - Personalizado: Ingresa coordenadas

## 📋 Requisitos

```bash
# Dependencias principales
streamlit==1.31.1
plotly==5.18.0
httpx==0.25.2
pydantic==2.5.3
pydantic-settings==2.1.0
```

## 🚀 Instalación

1. **Clonar repositorio:**
```bash
git clone https://github.com/lrdlk/ClimAPI.git
cd ClimAPI
```

2. **Crear entorno virtual:**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno:**
```bash
# Copiar plantilla
cp backend/.env.example backend/.env

# Editar backend/.env con tus API keys (opcional)
# - OPENWEATHERMAP_API_KEY
# - METEOBLUE_API_KEY
```

## 🎮 Uso

### Ejecutar el dashboard:

```bash
# Desde el directorio raíz del proyecto
streamlit run streamlit_dashboard/app.py
```

El dashboard abrirá automáticamente en `http://localhost:8501`

### Ejecutar pruebas de integración:

```bash
python streamlit_dashboard/test_integration.py
```

## 📐 Estructura del Proyecto

```
streamlit_dashboard/
├── app.py                    # Aplicación principal de Streamlit
├── test_integration.py       # Pruebas de integración
├── __init__.py              # Marcador de paquete
└── .streamlit/
    └── config.toml          # Configuración de Streamlit

backend/
├── app/
│   ├── main.py              # Aplicación FastAPI
│   ├── config.py            # Configuración
│   ├── services/
│   │   ├── open_meteo.py    # Cliente Open-Meteo
│   │   └── aggregator.py    # Agregador multi-fuente
│   └── processors/
│       ├── storage.py       # Cache Manager
│       └── transform.py     # Normalización de datos
```

## 🔧 Componentes Principales

### WeatherAggregator

Obtiene datos de múltiples fuentes simultáneamente:

```python
from backend.app.services.aggregator import WeatherAggregator

aggregator = WeatherAggregator()
sources = await aggregator.fetch_all_sources(latitude=6.2442, longitude=-75.5812)
```

### CacheManager

Gestiona caché con TTL:

```python
from backend.app.processors.storage import CacheManager

cache = CacheManager(ttl_minutes=15)
cache.set("key", {"data": "value"})
data = cache.get("key")
```

### Data Normalization

Normaliza datos de diferentes fuentes:

```python
from backend.app.processors.transform import process_weather_data

normalized = process_weather_data(raw_data)
stats = calculate_statistics(normalized)
```

## 📊 Pestaña de Datos Actuales

Muestra los datos de cada fuente:

- ✅ **Con datos:** Muestra valores principales (temperatura, humedad, presión)
- ⏸️ **Inactiva:** Fuente no disponible
- ❌ **Error:** Motivo del error
- 💾 **En caché:** Indica si los datos son cacheados

## 📈 Pestaña de Gráficos

Visualizaciones interactivas con Plotly:

- 🔴 **Estado de fuentes:** Pie chart de fuentes activas/inactivas
- 📊 **Disponibilidad:** Gráfico de fuentes con datos/error

## 📋 Pestaña de Detalles

Información técnica en formato JSON:

- Cache Manager stats
- Estado de cada fuente
- Datos agregados completos

## 🛠️ Configuración

### Editar `streamlit_dashboard/.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#667eea"
backgroundColor = "#FFFFFF"

[server]
port = 8501
headless = true

[client]
showErrorDetails = true
```

### Variables de entorno en `backend/.env`:

```env
# API
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=info

# Cache
CACHE_TTL=15

# API Keys (opcional)
OPENWEATHERMAP_API_KEY=your_key_here
METEOBLUE_API_KEY=your_key_here
```

## 🧪 Testing

### Pruebas de integración:

```bash
python streamlit_dashboard/test_integration.py
```

Valida:
- ✅ Obtención de datos de todas las fuentes
- ✅ Agregación y estadísticas
- ✅ Cache Manager con TTL
- ✅ Integración del dashboard
- ✅ Rendimiento (tiempo de respuesta)

### Pruebas unitarias (backend):

```bash
python -m pytest backend/tests -v
```

## 🚀 Despliegue

### Ejecutar con Gunicorn + Streamlit:

```bash
# Terminal 1: Backend API
python main.py api

# Terminal 2: Streamlit Dashboard
streamlit run streamlit_dashboard/app.py
```

### Docker (próximamente):

```bash
docker build -t climapi .
docker run -p 8000:8000 -p 8501:8501 climapi
```

## 📖 API REST

El backend FastAPI proporciona:

- `GET /health` - Estado del servicio
- `GET /api/weather?lat=6.2442&lon=-75.5812` - Datos agregados
- `GET /docs` - Documentación Swagger
- `GET /redoc` - Documentación ReDoc

## 🔐 Variables de entorno requeridas

```bash
# Obligatorio
CACHE_TTL=15  # Minutos

# Opcional (para activar fuentes adicionales)
OPENWEATHERMAP_API_KEY=sk_live_...
METEOBLUE_API_KEY=...
```

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'streamlit'"
```bash
pip install streamlit==1.31.1
```

### "Connection refused" en Open-Meteo
- Verificar conexión a internet
- Intentar con VPN si hay restricciones regionales

### Datos no se actualizan
- Verificar que CACHE_TTL ha expirado (por defecto 15 min)
- Usar botón "🔄 Actualizar datos ahora"

### API keys no funcionan
- Verificar formato en `backend/.env`
- Verificar que las keys sean válidas en sus respectivos proveedores

## 📚 Documentación

- [README principal del proyecto](../README.md)
- [Arquitectura](../ARCHITECTURE.md)
- [Próximos pasos](../NEXT_STEPS.md)

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/NewFeature`)
3. Commit tus cambios (`git commit -m 'Add NewFeature'`)
4. Push a la rama (`git push origin feature/NewFeature`)
5. Abre un Pull Request

## 📄 Licencia

MIT License - Ver LICENSE para detalles

## 👥 Autores

- **Team ClimAPI** - Desarrollo inicial

## 🎯 Roadmap

- [ ] Pronóstico a 7 días
- [ ] Historial de datos (últimos 30 días)
- [ ] Alertas meteorológicas por email
- [ ] Más ciudades (10+)
- [ ] Exportación de datos (CSV, Excel)
- [ ] Integración con Dark Sky API
- [ ] Mobile app
- [ ] WebSocket para actualizaciones en vivo

## 📞 Soporte

- 🐛 [Reportar bugs](https://github.com/lrdlk/ClimAPI/issues)
- 💬 [Sugerencias](https://github.com/lrdlk/ClimAPI/discussions)
- 📧 Email: support@climapi.dev

---

**¡Gracias por usar ClimAPI! 🌍**
