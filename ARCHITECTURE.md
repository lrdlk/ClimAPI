# 🏗️ ARQUITECTURA DEL PROYECTO - ClimAPI v1.0.0

## Diagrama de Estructura

```
📦 ClimAPI/
├── 📄 main.py                          ← Entry point (Delegador)
├── 📄 requirements.txt                 ← Dependencias raíz
├── 📄 .env                             ← Configuración local
├── 📄 verify_integrity.py              ← Script de verificación
├── 📄 INTEGRITY_REPORT.md              ← Reporte de verificación
├── 📄 PROJECT_STATUS.json              ← Estado del proyecto (JSON)
├── 📄 ARCHITECTURE.md                  ← Este archivo
│
├── 📁 backend/                         ← 🔧 BACKEND FASTAPI
│   ├── 📄 __init__.py                  ← Package marker (v1.0.0)
│   ├── 📄 requirements.txt             ← Dependencias backend
│   ├── 📄 start.py                     ← Script de inicio
│   │
│   └── 📁 app/                         ← Aplicación principal
│       ├── 📄 __init__.py              ← Exports (settings, app)
│       ├── 📄 main.py                  ← FastAPI app instance
│       ├── 📄 config.py                ← Configuración (Pydantic)
│       ├── 📄 models.py                ← Modelos de datos
│       ├── 📄 init.py                  ← [DEPRECATED]
│       │
│       ├── 📁 services/                ← Servicios externos
│       │   ├── 📄 __init__.py          ← Exports
│       │   ├── 📄 open_meteo.py        ← Cliente Open-Meteo (ASYNC)
│       │   ├── 📄 cache_manager.py     ← [MOVED to processors]
│       │   └── 📄 data_processor.py    ← [DEPRECATED]
│       │
│       ├── 📁 processors/              ← Procesamiento de datos
│       │   ├── 📄 __init__.py          ← Exports (storage, transform)
│       │   ├── 📄 storage.py           ← CacheManager + File I/O
│       │   ├── 📄 transform.py         ← Normalización de datos
│       │   └── 📄 init.py              ← [DEPRECATED]
│       │
│       ├── 📁 scripts/                 ← Scripts y CLI
│       │   ├── 📄 __init__.py          ← Exports
│       │   ├── 📄 legacy_main.py       ← CLI script (ASYNC)
│       │   ├── 📄 init.py              ← [DEPRECATED]
│       │   └── 📄 init.py              ← [DEPRECATED]
│       │
│       └── 📁 api/                     ← API Routes (REST)
│           ├── 📄 __init__.py          ← Placeholder
│           ├── 📄 dependencies.py      ← Inyección de dependencias
│           ├── 📄 routes.py            ← [PENDING]
│           └── 📁 routes/
│               ├── 📄 __init__.py
│               ├── 📄 health.py        ← /health (liveness probe)
│               ├── 📄 weather.py       ← /api/weather
│               └── 📄 locations.py     ← /api/locations
│
│   └── 📁 tests/                       ← Test Suite [PLACEHOLDER]
│       ├── 📄 __init__.py
│       ├── 📄 test_api.py              ← [PENDING]
│       ├── 📄 test_services.py         ← [PENDING]
│       └── 📁 test_integration/        ← [PENDING]
│
├── 📁 frontend/                        ← 🎨 FRONTEND NEXT.JS [PENDING]
│   ├── 📄 package.json
│   ├── 📄 tsconfig.json
│   ├── 📄 next.config.js
│   ├── 📄 tailwind.config.ts
│   ├── 📁 app/
│   │   ├── 📄 layout.tsx
│   │   ├── 📄 page.tsx
│   │   └── 📁 dashboard/
│   │       └── 📄 page.tsx
│   └── 📁 lib/
│       ├── 📄 api.ts                  ← Cliente HTTP (axios/fetch)
│       ├── 📄 types.ts                ← TypeScript interfaces
│       └── 📄 utils.ts                ← Utilidades
│
├── 📁 data/                            ← 📊 Datos guardados
│   └── 📄 weather_data.csv
│
├── 📁 cache/                           ← 💾 Caché local
│
├── 📁 config/                          ← ⚙️ Configuración
│   ├── 📄 config.py
│   └── 📄 settings.json
│
└── 📁 data_sources/                    ← 🌐 Integraciones externas
    ├── 📄 __init__.py
    ├── 📄 open_meteo.py               ← Open-Meteo API
    ├── 📄 meteoblue.py                ← MeteoBlue API
    ├── 📄 openweathermap.py           ← OpenWeather API
    └── 📄 radar_ideam.py              ← Radar IDEAM (Colombia)
```

---

## 🔄 Flujo de Datos

```
┌─────────────────────────────────────────────────────────────┐
│                    USUARIO/CLIENTE                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│               FRONTEND (Next.js/React)                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Dashboard (Mapa + Gráficos + Tablas)               │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬─────────────────────────────────────┘
                         │ HTTP/REST
                         ▼
┌──────────────────────────────────────────────────────────────┐
│              FASTAPI (Backend) Port 8000                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  CORS Middleware (localhost:3000, localhost:3001)   │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬─────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
    ┌────────┐      ┌────────┐      ┌──────────┐
    │ /health│      │ /api/  │      │/api/     │
    │        │      │weather │      │locations │
    └────────┘      └────────┘      └──────────┘
        │                │                │
        │                └────────────────┤
        │                                 │
        └─────────────────────┬───────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │  SERVICIOS (Services)        │
              │  ┌─────────────────────────┐ │
              │  │ OpenMeteo Service       │ │
              │  │ (get_weather_data())    │ │
              │  └─────────────────────────┘ │
              └───────────┬───────────────────┘
                          │
                          ▼
              ┌───────────────────────────────┐
              │  PROCESADORES (Processors)   │
              │  ┌──────────────────────────┐│
              │  │ Transform (normaliza)    ││
              │  ├──────────────────────────┤│
              │  │ Storage (caché + archivos││
              │  └──────────────────────────┘│
              └───────────┬───────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
    ┌────────┐      ┌─────────┐      ┌──────────┐
    │ Caché  │      │CSV/JSON │      │Múltiples │
    │ (TTL)  │      │ archivos │      │ fuentes  │
    └────────┘      └─────────┘      └──────────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
        ┌─────────────────┴─────────────────┐
        │                                   │
        ▼                                   ▼
┌──────────────────┐            ┌──────────────────┐
│ Open-Meteo API   │            │ Otras fuentes    │
│ (Implementado)   │            │ (Pendiente)      │
└──────────────────┘            └──────────────────┘
```

---

## 🔗 Flujo de Importes

```
main.py (Root)
    ├─ Imports: backend.app.main (app)
    ├─ Imports: uvicorn (serve)
    └─ Imports: pytest (test)
            │
            ▼
backend/app/main.py (FastAPI Instance)
    ├─ Imports: .config (settings)
    ├─ Imports: .models (Pydantic models)
    ├─ Imports: fastapi (FastAPI)
    ├─ Imports: fastapi.middleware.cors
    └─ Imports: logging
            │
            ├──────────────────────────────┐
            │                              │
            ▼                              ▼
backend/app/config.py          backend/app/services/
(Settings)                      open_meteo.py
    ├─ Imports: pydantic_settings      ├─ Imports: httpx
    ├─ Imports: dotenv                 ├─ Imports: logging
    └─ Imports: pathlib                ├─ Imports: typing
                                        └─ Imports: .config (settings)
                                               │
                                               ▼
                                    backend/app/processors/
                                    transform.py & storage.py
                                        ├─ Imports: typing
                                        ├─ Imports: datetime
                                        ├─ Imports: logging
                                        ├─ Imports: csv/json
                                        └─ Imports: pathlib
```

---

## 📊 Componentes Clave

### 1️⃣ Backend/App/Config.py (Configuración)
```
Función: Centralizar todas las configuraciones
Entrada: Variables de entorno (.env)
Salida: Settings object (singleton)
Manejo: Pydantic-Settings (automático)
```

### 2️⃣ Backend/App/Main.py (Aplicación)
```
Función: Instancia FastAPI, setup CORS, rutas
Entrada: settings (config)
Salida: app (FastAPI instance)
Eventos: startup, shutdown
Documentación: /docs, /redoc
```

### 3️⃣ Backend/App/Services/open_meteo.py (Cliente)
```
Función: Conectar con API Open-Meteo
Entrada: lat, lon, timezone
Salida: weather data (dict)
Validación: coordinate validation
Async: Si (httpx)
```

### 4️⃣ Backend/App/Processors/storage.py (Almacenamiento)
```
Función: Caché + Persistencia
Clase: CacheManager (TTL-based)
Métodos: set, get, clear
File I/O: save_to_csv(), save_to_json()
```

### 5️⃣ Backend/App/Processors/transform.py (Normalización)
```
Función: Unificar múltiples formatos
Entrada: Raw weather data
Salida: Standardized format
Soporta: OpenMeteo, SIATA, Generic
```

### 6️⃣ Backend/App/Scripts/legacy_main.py (CLI)
```
Función: Script para uso en terminal
Entrada: Ubicaciones predefinidas
Salida: CSV files
Async: Si
```

---

## 🔐 Configuración

### Archivo: backend/.env
```
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

# API Keys (cuando sea necesario)
OPENWEATHERMAP_KEY=xxxxx
SIATA_KEY=xxxxx
```

---

## 📈 Estados y Transiciones

```
┌─────────────────┐
│    CREACIÓN     │ ← Proyecto iniciado
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   VALIDACIÓN    │ ← Verificación de estructura
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   ÓPTIMO ✓      │ ← Estado actual (100% integridad)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  PRODUCCIÓN     │ ← Próximo objetivo
└─────────────────┘
```

---

## 📋 Checklist de Implementación

### ✅ Completado
- [x] Estructura de carpetas
- [x] Configuración centralizada
- [x] FastAPI setup + CORS
- [x] Servicio Open-Meteo
- [x] Procesadores (transform + storage)
- [x] Script legacy CLI
- [x] Verificación de integridad
- [x] Documentación

### 🔄 En Progreso
- [ ] Frontend Next.js integration
- [ ] Endpoints REST completos

### ⏳ Pendiente
- [ ] Tests unitarios (backend/tests/)
- [ ] Múltiples fuentes de datos
- [ ] Autenticación API
- [ ] CI/CD pipeline
- [ ] Deploy en producción

---

## 🚀 Comandos de Uso

```bash
# Iniciar API
python main.py api

# Ejecutar script legacy
python main.py legacy

# Ejecutar tests
python main.py test

# Ver ayuda
python main.py help
```

---

**Arquitectura v1.0.0 | Generado: 2025-12-07 | Estado: ÓPTIMO ✓**
