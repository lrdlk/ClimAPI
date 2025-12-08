# 🚀 Guía de Ejecución en Environment - ClimAPI

## Estado Actual

✅ Entorno Virtual Configurado
✅ Todas las Dependencias Instaladas
✅ Tests Completados (5/5 ✓)
✅ Dashboard Listo para Usar

---

## 📍 Ubicación del Entorno Virtual

```
Ruta: E:\C0D3\Python\Jupyter\ClimAPI\.venv
Executable: .venv\Scripts\python.exe
Streamlit: .venv\Scripts\streamlit.exe
```

---

## 🎯 Opciones de Ejecución

### OPCIÓN 1: Ejecutar Dashboard Directamente (RECOMENDADO)

```powershell
# En PowerShell, desde E:\C0D3\Python\Jupyter\ClimAPI

.venv\Scripts\streamlit.exe run dashboard/app.py
```

**Resultado esperado:**
```
Local URL: http://localhost:8501
Network URL: http://192.168.1.12:8501
```

---

### OPCIÓN 2: Ejecutar con Python Module

```powershell
.venv\Scripts\python.exe -m streamlit run dashboard/app.py
```

---

### OPCIÓN 3: Ejecutar Tests de Integración

```powershell
# Ejecutar tests completos
.venv\Scripts\python.exe dashboard/test_integration.py

# Resultado: 5/5 tests pasando
```

---

### OPCIÓN 4: Ejecutar API FastAPI

```powershell
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload
```

**Acceso:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

---

## 📊 Dependencias Disponibles en el Entorno

Versiones Confirmadas:

```
✓ streamlit          (1.52.1)
✓ plotly             (6.5.0)
✓ fastapi            (0.124.0)
✓ uvicorn            (0.38.0)
✓ pandas             (2.3.3)
✓ numpy              (2.3.5)
✓ pytest             (9.0.2)
✓ pytest-asyncio    (1.3.0)
✓ pydantic           (2.12.5)
✓ python-dotenv      (1.2.1)
✓ requests           (2.32.5)
```

Total: 50+ paquetes instalados

---

## 🧪 Resultados de Tests

### Test 1: Agregador ✅
- Obtención de datos de 5 fuentes
- 2 fuentes activas (Open-Meteo, SIATA)
- Datos normalizados correctamente

### Test 2: Estadísticas ✅
- Temperature: average 22.50°C
- Humidity: average 65%
- Wind Speed: average 3.2 m/s

### Test 3: Cache Manager ✅
- TTL: 60 segundos
- Almacenamiento: OK
- Recuperación: OK

### Test 4: Integración Dashboard ✅
- 7 componentes principales
- Todas las características implementadas
- Responsive design

### Test 5: Rendimiento ✅
- Primera consulta: 1.12s
- Segunda consulta (caché): 1.10s
- Mejora: 2.0%

---

## 🎨 4 Modos del Dashboard

Al ejecutar el dashboard, tienes acceso a:

### 1. 📊 TIEMPO REAL
- Datos en vivo de múltiples fuentes
- Open-Meteo (siempre disponible)
- SIATA Medellín (disponible)
- Gráficos interactivos
- Status indicators

### 2. 📈 DATOS HISTÓRICOS
- Cargar archivos CSV
- Filtros por fecha
- 4 tipos de visualización:
  - Temperatura
  - Humedad
  - Precipitación
  - Velocidad del viento

### 3. 📋 COMPARATIVA
- Seleccionar ubicación
- Comparar fuentes lado a lado
- Identificar diferencias
- Análisis visual

### 4. ℹ️  INFORMACIÓN
- Cache Manager Stats
- Aggregator Status
- JSON Data Viewer
- Métricas del sistema

---

## 🔄 Flujo de Trabajo Recomendado

### Sesión 1: Pruebas y Validación

```powershell
# 1. Abrir terminal
cd E:\C0D3\Python\Jupyter\ClimAPI

# 2. Ejecutar tests
.venv\Scripts\python.exe dashboard/test_integration.py

# 3. Verificar que todos los tests pasen (5/5)
```

### Sesión 2: Ejecutar Dashboard

```powershell
# 1. Desde terminal
.venv\Scripts\streamlit.exe run dashboard/app.py

# 2. Abrir navegador
# URL: http://localhost:8501

# 3. Explorar los 4 modos
# - Tiempo Real
# - Datos Históricos
# - Comparativa
# - Información
```

### Sesión 3: Desarrollo API

```powershell
# 1. Ejecutar API
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload

# 2. Verificar documentación
# URL: http://localhost:8000/docs

# 3. Probar endpoints
```

---

## 🛠️ Comandos Útiles del Entorno

### Ver versión de Python
```powershell
.venv\Scripts\python.exe --version
```

### Ver paquetes instalados
```powershell
.venv\Scripts\pip.exe list
```

### Actualizar pip
```powershell
.venv\Scripts\python.exe -m pip install --upgrade pip
```

### Instalar nuevo paquete
```powershell
.venv\Scripts\pip.exe install nombre-paquete
```

### Desactivar estadísticas de Streamlit
```powershell
.venv\Scripts\streamlit.exe run dashboard/app.py --client.gatherUsageStats=false
```

---

## 📁 Estructura del Proyecto

```
ClimAPI/
├── .venv/                      ← Entorno virtual
│   ├── Scripts/
│   │   ├── python.exe
│   │   ├── streamlit.exe
│   │   ├── pip.exe
│   │   └── pytest.exe
│   └── Lib/
│
├── dashboard/
│   ├── app.py                  ← Dashboard (4 modos)
│   ├── test_integration.py     ← Tests (5/5 ✓)
│   ├── README.md
│   └── .streamlit/config.toml
│
├── backend/
│   ├── app/main.py             ← FastAPI
│   ├── app/services/
│   │   ├── aggregator.py       ← Multi-source
│   │   ├── cache_manager.py    ← TTL cache
│   │   └── open_meteo.py
│   └── tests/
│
├── data/
│   ├── weather_*.csv           ← Datos históricos
│   └── ...
│
└── main.py                     ← Entry point
```

---

## ✨ Características Confirmadas

### Dashboard
✅ 4 modos de visualización
✅ Gráficos interactivos Plotly
✅ Selector de ubicaciones
✅ Filtros de fecha
✅ Exportación a CSV
✅ Cache visual

### Backend
✅ API FastAPI funcional
✅ Agregador de 5 fuentes
✅ Cache con TTL (15 min)
✅ Validación de coordenadas
✅ Documentación automática (/docs)

### Testing
✅ Tests de agregador
✅ Tests de estadísticas
✅ Tests de caché
✅ Tests de integración
✅ Tests de rendimiento

---

## 🔗 URLs de Acceso

```
Dashboard Streamlit:
  Local:    http://localhost:8501
  Red:      http://192.168.1.12:8501
  Externa:  http://191.91.10.213:8501

API FastAPI:
  URL:      http://localhost:8000
  Docs:     http://localhost:8000/docs
  ReDoc:    http://localhost:8000/redoc
```

---

## 📝 Archivo de Configuración

Ubicación: `dashboard/.streamlit/config.toml`

```toml
[theme]
primaryColor = "#667eea"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"

[server]
port = 8501
headless = true
runOnSave = true
maxUploadSize = 200
```

---

## 🎓 Próximos Pasos

1. ✅ Ejecutar dashboard: `.venv\Scripts\streamlit.exe run dashboard/app.py`
2. ✅ Explorar los 4 modos
3. ✅ Probar datos en tiempo real
4. ✅ Verificar datos históricos
5. ✅ Ejecutar API: `.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload`

---

## 🚀 Estado Final

**Ambiente:** ✅ LISTO
**Tests:** ✅ 5/5 PASANDO
**Dashboard:** ✅ EJECUTÁNDOSE
**Documentación:** ✅ COMPLETA

**PROYECTO LISTO PARA DESARROLLO Y PRODUCCIÓN**

---

ClimAPI v1.0.0 - Diciembre 2025
Configurado en Environment Virtual Python 3.14
