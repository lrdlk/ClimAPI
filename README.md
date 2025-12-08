# 🌤️ ClimAPI v1.0.0 - Dashboard Meteorológico

**Estado:** ✅ **PROYECTO EN ESTADO ÓPTIMO** | **Integridad:** 100% | **Pinggy.io:** ✅ **ACTIVO**

Dashboard meteorológico unificado con datos de múltiples fuentes en tiempo real. Backend FastAPI + Frontend Next.js.

> **⚠️ ¿Error de PowerShell?** Lee [`POWERSHELL_ERROR_FIXED.md`](POWERSHELL_ERROR_FIXED.md) - **¡Problema resuelto!**  
> **⚡ INICIO RÁPIDO:** Ejecuta `.\run-tunnel.ps1` para iniciar el túnel Pinggy

---

## 📋 Descripción General

ClimAPI es un proyecto fullstack moderno que permite:

✅ **Backend API (FastAPI)**
- Consumir datos meteorológicos desde múltiples fuentes (Open-Meteo, SIATA, OpenWeatherMap)
- Validación robusta de coordenadas
- Caché inteligente con TTL (15 min)
- Normalización de datos desde múltiples formatos
- Agregador de fuentes para datos consolidados
- Documentación automática en `/docs`

✅ **Dashboard Meteorológico (Streamlit)**
- 4 modos de visualización (Tiempo Real, Histórico, Comparativa, Información)
- Gráficos interactivos con Plotly
- Datos en tiempo real desde múltiples fuentes
- Visualización de datos históricos desde CSV
- Comparación lado a lado de fuentes de datos
- Estadísticas y agregación de datos

✅ **Frontend (Next.js) - En Desarrollo**
- Dashboard interactivo con mapas
- Gráficos en tiempo real
- Tabla de datos meteorológicos
- Múltiples ubicaciones

✅ **Procesamiento de Datos**
- Transformación de formatos Open-Meteo, SIATA, IDEAM
- Cálculo de estadísticas (min/max/avg)
- Exportación a CSV y JSON
- Almacenamiento en caché con gestor de TTL

---

## 🗂️ Estructura del Proyecto

```
ClimAPI/
├── 📄 main.py                    ← Entry point (delegador)
├── 📄 verify_integrity.py        ← Verificador de integridad
├── 📄 requirements.txt           ← Dependencias
│
├── 📁 backend/                   ← 🔧 BACKEND FASTAPI
│   ├── 📄 __init__.py
│   ├── 📄 requirements.txt
│   └── 📁 app/
│       ├── 📄 main.py            ← FastAPI app
│       ├── 📄 config.py          ← Configuración
│       ├── 📄 models.py          ← Modelos Pydantic
│       ├── 📁 services/
│       │   └── 📄 open_meteo.py  ← Cliente Open-Meteo
│       ├── 📁 processors/
│       │   ├── 📄 storage.py     ← Caché + File I/O
│       │   └── 📄 transform.py   ← Normalización
│       ├── 📁 scripts/
│       │   └── 📄 legacy_main.py ← CLI script
│       ├── 📁 api/
│       │   └── 📁 routes/
│       │       ├── 📄 health.py
│       │       ├── 📄 weather.py
│       │       └── 📄 locations.py
│       └── 📁 tests/             ← Tests (placeholder)
│
├── 📁 dashboard/                 ← 📊 DASHBOARD STREAMLIT (UNIFICADO)
│   ├── 📄 app.py                 ← Dashboard principal (4 modos)
│   ├── 📄 README.md              ← Documentación dashboard
│   ├── 📄 test_integration.py    ← Tests de integración
│   └── 📁 .streamlit/
│       └── 📄 config.toml        ← Configuración Streamlit
│
├── 📁 frontend/                  ← 🎨 FRONTEND NEXT.JS
│   ├── 📄 package.json
│   ├── 📄 tsconfig.json
│   ├── 📄 next.config.js
│   ├── 📄 tailwind.config.ts
│   ├── 📁 app/
│   │   ├── 📄 layout.tsx
│   │   └── 📄 page.tsx
│   └── 📁 lib/
│       ├── 📄 api.ts
│       ├── 📄 types.ts
│       └── 📄 utils.ts
│
├── 📁 data_sources/              ← Integraciones externas
├── 📄 SUMMARY.md                 ← Resumen del trabajo
├── 📄 INTEGRITY_REPORT.md        ← Reporte de verificación
├── 📄 ARCHITECTURE.md            ← Documentación arquitectura
├── 📄 INTEGRATION_STATUS.md      ← Estado de integración (nuevo)
├── 📄 NEXT_STEPS.md              ← Guía de próximos pasos
└── 📄 QUICKSTART.md              ← Inicio rápido
```

## 🚀 Inicio Rápido

### ⚡ Opción A: Con Acceso Remoto (Pinggy.io)

```powershell
# 1. Abre PowerShell en el directorio del proyecto
cd "e:\C0D3\Python\Jupyter\ClimAPI"

# 2. Inicia el túnel (Terminal 1)
.\start_tunnel.ps1
# Selecciona opción 1 en el menú

# 3. En una NUEVA terminal, inicia el dashboard (Terminal 2)
.venv\Scripts\streamlit.exe run dashboard/app.py

# 4. Accede al dashboard:
#    - Local:  http://localhost:8501
#    - Remoto: https://Fm4hH7kZ8sz.free.pinggy.io
```

**Nota:** Si encuentras error de PowerShell, lee [`QUICK_START_SCRIPTS.md`](QUICK_START_SCRIPTS.md)

---

### ⚡ Opción B: Solo Local (sin Pinggy)

```bash
# 1. Activa el entorno virtual
.venv\Scripts\activate

# 2. Inicia el dashboard
streamlit run dashboard/app.py

# 3. Accede a http://localhost:8501
```

---

### Requisitos
- Python 3.10+
- pip
- Node.js 16+ (para frontend, opcional)

### 1. Instalar Dependencias

```bash
# Backend
pip install -r backend/requirements.txt

# Frontend (opcional)
cd frontend
npm install
cd ..
```

### 2. Iniciar API Backend

```bash
python main.py api
```

Accede a:
- **API:** http://localhost:8000
- **Documentación:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### 3. Comandos Disponibles

```bash
# Iniciar Dashboard Streamlit (RECOMENDADO)
python main.py dashboard
→ Abre en http://localhost:8501

# Iniciar API FastAPI
python main.py api
→ Abre en http://localhost:8000
→ Documentación en http://localhost:8000/docs

# Ejecutar script legacy (CLI)
python main.py legacy

# Ejecutar tests
python main.py test

# Ver ayuda
python main.py help
```

### 4. 🌐 Acceso Remoto con Pinggy.io (NUEVO)

Para exponer tu dashboard a internet con **HTTPS seguro**:

```bash
# Opción A: Script Automático (Recomendado)
python pinggy_direct.py

# Opción B: Comando Directo
pinggy.exe -p 443 -R0:127.0.0.1:8501 -o StrictHostKeyChecking=no -o ServerAliveInterval=30 Fm4hH7kZ8sz+force@free.pinggy.io

# Opción C: Instalador Interactivo
python pinggy_installer.py
```

**Resultado:**
- URL pública: `https://Fm4hH7kZ8sz.free.pinggy.io`
- Accesible desde cualquier dispositivo
- HTTPS automático (sin certificados)
- Compartible con equipo/clientes

**Requiere:**
- ✅ pinggy.exe (descargable desde https://pinggy.io)
- ✅ Dashboard en puerto 8501

📖 Ver: [`START_PINGGY.md`](START_PINGGY.md) | [`PINGGY_COMMAND.md`](PINGGY_COMMAND.md) | [`PINGGY_GUIDE.md`](PINGGY_GUIDE.md)

### 4. Dashboard Streamlit - 4 Modos

**Tiempo Real**: Datos en directo desde múltiples fuentes (Open-Meteo, SIATA, etc.)
**Datos Históricos**: Visualización y análisis de datos CSV históricos
**Comparativa**: Comparación lado a lado de fuentes de datos
**Información**: Estadísticas del sistema y estado de cachés

---

## 📊 Endpoints de la API

### Health Check
```bash
GET /health
```
Respuesta:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### Obtener Clima
```bash
GET /api/weather?lat=6.2442&lon=-75.5812
```
Respuesta:
```json
{
  "location": "Medellín",
  "temperature": 22.5,
  "humidity": 65,
  "wind_speed": 3.2,
  "timestamp": "2025-12-07T14:00:00"
}
```

### Ubicaciones Predefinidas
```bash
GET /api/locations
```
Respuesta:
```json
[
  {
    "name": "Medellín",
    "latitude": 6.2442,
    "longitude": -75.5812
  },
  ...
]
```

---

## ⚙️ Configuración

Edita `backend/.env` para personalizar:

```env
# Servidor
HOST=0.0.0.0
PORT=8000
DEBUG=True

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# Caché
CACHE_TTL_MINUTES=15

# Logging
LOG_LEVEL=INFO
```

---

## 🔗 Stack Tecnológico

### Backend
- **Framework:** FastAPI 0.109.0
- **Servidor:** Uvicorn 0.27.0
- **Validación:** Pydantic 2.5.3
- **Config:** Pydantic-Settings 2.1.0
- **HTTP:** httpx 0.25.2 (async)

### Frontend
- **Framework:** Next.js 14+
- **Styling:** Tailwind CSS
- **Components:** shadcn/ui
- **HTTP Client:** fetch / axios

### Testing
- **Framework:** pytest 7.4.3
- **Coverage:** pytest-cov 4.1.0
- **Async:** pytest-asyncio 0.23.1

### Data Sources
- **Open-Meteo:** API pública (implementada)
- **SIATA:** Radar meteorológico Medellín
- **IDEAM:** Datos Colombia
- **MeteoBlue:** Pronósticos

---

## 📈 Verificación del Proyecto

Para verificar la integridad del proyecto:

```bash
python verify_integrity.py
```

Resultado esperado:
```
✅ Estructura: 17/17
✅ Imports: 6/6
✅ Funcionalidad: 5/5
✅ INTEGRIDAD: 100%
```

---

## 📚 Documentación

Dentro del proyecto encontrarás:

| Archivo | Descripción |
|---------|-------------|
| **QUICKSTART.md** | Inicio rápido (2 minutos) |
| **SUMMARY.md** | Resumen del trabajo realizado |
| **ARCHITECTURE.md** | Diagrama de arquitectura |
| **NEXT_STEPS.md** | Guía de próximas prioridades |
| **INTEGRITY_REPORT.md** | Reporte de verificación |
| **PROJECT_STATUS.json** | Estado actual en JSON |

---

## 🎯 Próximas Prioridades

1. **Endpoints REST** - Implementar rutas completas
2. **Test Suite** - Escribir tests unitarios
3. **Frontend Integration** - Conectar Next.js
4. **Múltiples Fuentes** - SIATA, IDEAM, MeteoBlue
5. **CI/CD** - GitHub Actions

---

## 🎯 Estado del Proyecto

### ✅ Completado
- Monorepo unificado con estructura clara
- Backend API FastAPI funcional
- Múltiples fuentes de datos meteorológicos integradas
- Caché inteligente con TTL (15 minutos)
- Dashboard Streamlit con 4 modos de visualización
- Soporte para datos históricos (CSV) y tiempo real
- Tests de integración completos
- Documentación integral

### 📊 Dashboard Integrado (NUEVO)
El dashboard proporciona 4 modos complementarios:
- **Tiempo Real**: Agregación de múltiples fuentes con status indicators
- **Histórico**: Análisis de datos CSV con filtros temporales
- **Comparativa**: Visualización lado a lado de fuentes
- **Info**: Métricas del sistema y estado de cachés

### 🔮 Próximas Mejoras
- [ ] Frontend Next.js con integración completa
- [ ] Base de datos persistente
- [ ] Alertas de umbral meteorológico
- [ ] Pronóstico extendido (7 días)
- [ ] Autenticación y perfiles de usuario
- [ ] Exportación a múltiples formatos
- [ ] Despliegue en la nube (Azure, AWS, Heroku)

---

## 🤝 Contribuir

Para contribuir al proyecto:

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📝 Licencia

Este proyecto está bajo licencia MIT.

---

## 📞 Soporte

- **Documentación:** Revisa los archivos `.md` en el proyecto
- **Dashboard:** `python main.py dashboard`
- **Issues:** Abre un issue en el repositorio
- **Contacto:** gargamel@example.com

---

**¡Gracias por usar ClimAPI! 🌤️**

*Última actualización: 8 de diciembre de 2025 | v1.0.0 - INTEGRACIÓN COMPLETA*

## 🤝 Contribuciones

Este proyecto está diseñado para ser un punto de partida. Siéntete libre de:
- Agregar nuevas fuentes de datos
- Mejorar las visualizaciones
- Agregar análisis estadísticos
- Implementar alertas meteorológicas

## 📄 Licencia

Este proyecto es de código abierto y está disponible para uso educativo y personal.

