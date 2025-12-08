#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ClimAPI - Quick Command Reference
Referencia rápida de todos los comandos disponibles
"""

# ============================================================================
# 🚀 COMANDOS PRINCIPALES
# ============================================================================

# 1. DASHBOARD (RECOMENDADO)
# ────────────────────────────────────────────────────────────────────────────
print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                    📊 DASHBOARD STREAMLIT (RECOMENDADO)                     ║
╚════════════════════════════════════════════════════════════════════════════╝

COMANDO:
  python main.py dashboard

DESCRIPCIÓN:
  Abre dashboard interactivo en Streamlit con 4 modos de visualización

ACCESO:
  http://localhost:8501

MODOS DISPONIBLES:
  ✓ 📊 Tiempo Real     - Datos en vivo de múltiples fuentes
  ✓ 📈 Datos Históricos - Análisis de CSV históricos
  ✓ 📋 Comparativa     - Lado a lado de múltiples fuentes
  ✓ ℹ️  Información    - Métricas y estado del sistema

CARACTERÍSTICAS:
  ✓ Gráficos interactivos con Plotly
  ✓ Múltiples ubicaciones (Medellín, Bogotá, Cali)
  ✓ Caché TTL (15 minutos)
  ✓ 5 fuentes de datos meteorológicos
  ✓ Exportación a CSV
  ✓ Estadísticas agregadas

REQUISITOS:
  ✓ Python 3.9+
  ✓ Streamlit 1.31.1
  ✓ Plotly 5.18.0
  ✓ Conexión a internet (para datos en vivo)

INSTALACIÓN:
  pip install streamlit==1.31.1 plotly==5.18.0

TIEMPO DE INICIO:
  ~3-5 segundos (primer caché: ~10 segundos)

GUÍA COMPLETA:
  Ver: DASHBOARD_GUIDE.md
""")

# 2. API FASTAPI
# ────────────────────────────────────────────────────────────────────────────
print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                      🔧 API FASTAPI (BACKEND)                              ║
╚════════════════════════════════════════════════════════════════════════════╝

COMANDO:
  python main.py api

DESCRIPCIÓN:
  Inicia servidor API con endpoints meteorológicos

ACCESO:
  API:              http://localhost:8000
  Documentación:    http://localhost:8000/docs
  ReDoc:            http://localhost:8000/redoc

ENDPOINTS PRINCIPALES:
  
  GET /api/weather/{lat}/{lon}
    - Obtiene datos de Open-Meteo
    - Ejemplo: /api/weather/6.2476/-75.5679
    
  GET /api/aggregated/{lat}/{lon}
    - Datos agregados de múltiples fuentes
    - Ejemplo: /api/aggregated/6.2476/-75.5679
    
  GET /api/health
    - Estado del sistema
    
  GET /api/locations
    - Ubicaciones predefinidas

CARACTERÍSTICAS:
  ✓ Documentación automática (Swagger UI)
  ✓ Validación Pydantic
  ✓ Caché centralizado
  ✓ Manejo de errores robusto
  ✓ CORS habilitado

REQUISITOS:
  ✓ FastAPI 0.109.0+
  ✓ Uvicorn 0.27.0+
  ✓ Pydantic 2.0+

INSTALACIÓN:
  pip install fastapi==0.109.0 uvicorn[standard]==0.27.0

TIEMPO DE INICIO:
  ~2-3 segundos

COMBINAR CON DASHBOARD:
  Terminal 1: python main.py api
  Terminal 2: python main.py dashboard
""")

# 3. SCRIPT LEGACY
# ────────────────────────────────────────────────────────────────────────────
print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                    📜 SCRIPT LEGACY (CLI)                                  ║
╚════════════════════════════════════════════════════════════════════════════╝

COMANDO:
  python main.py legacy

DESCRIPCIÓN:
  Ejecuta script legacy para consumir y guardar datos meteorológicos

FUNCIONALIDAD:
  ✓ Descarga datos de múltiples ubicaciones
  ✓ Guarda en archivos CSV
  ✓ Ejecuta procesamiento de datos
  ✓ Genera reportes

SALIDA:
  Archivos guardados en: data/*.csv
  - weather_medellin_*.csv
  - weather_bogota_*.csv
  - weather_cali_*.csv

TIEMPO DE EJECUCIÓN:
  ~15-30 segundos (depende de conectividad)

USO:
  Útil para:
  ✓ Recopilación histórica de datos
  ✓ Scheduling automático (cron jobs)
  ✓ Generación de datasets
  ✓ Procesamiento batch
""")

# 4. TESTS
# ────────────────────────────────────────────────────────────────────────────
print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                    ✅ TESTS DE INTEGRACIÓN                                 ║
╚════════════════════════════════════════════════════════════════════════════╝

COMANDO:
  python main.py test

DESCRIPCIÓN:
  Ejecuta suite completa de tests de integración

TESTS INCLUIDOS:
  ✓ test_aggregator()         - Validar multi-source
  ✓ test_aggregation_stats()  - Validar estadísticas
  ✓ test_cache_manager()      - Validar caché
  ✓ test_dashboard()          - Validar UI components
  ✓ test_performance()        - Benchmarks

RESULTADOS ESPERADOS:
  5/5 tests pasando ✅
  Ejecución: ~20-30 segundos

UBICACIÓN:
  dashboard/test_integration.py

EJECUTAR DIRECTAMENTE:
  python dashboard/test_integration.py

REQUISITOS:
  ✓ Pytest
  ✓ Asyncio
  ✓ Todas las dependencias instaladas
""")

# ============================================================================
# 📋 COMBINACIONES ÚTILES
# ============================================================================
print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                      🔄 COMBINACIONES ÚTILES                               ║
╚════════════════════════════════════════════════════════════════════════════╝

COMBO 1: DESARROLLO RÁPIDO
  python main.py dashboard
  → Acceso inmediato a datos en vivo
  → Ideal para prototipos y demos

COMBO 2: ARQUITECTURA MODULAR
  Terminal 1: python main.py api
  Terminal 2: python main.py dashboard
  → API centralizada
  → Dashboard como cliente
  → Mejor escalabilidad

COMBO 3: CICLO COMPLETO
  Terminal 1: python main.py legacy        # Recopila datos
  Terminal 2: python main.py api           # Inicia API
  Terminal 3: python main.py dashboard     # Visualiza
  → Data collection → Processing → Visualization

COMBO 4: VALIDACIÓN
  python main.py test                      # Ejecuta tests
  python main.py dashboard                 # Verifica UI
  python main.py api                       # Verifica endpoints

COMBO 5: PRODUCCIÓN
  # En contenedor:
  gunicorn "backend.app.main:app" --workers 4 --worker-class uvicorn.workers.UvicornWorker
  # En otra terminal:
  streamlit run dashboard/app.py --server.port=8501
""")

# ============================================================================
# 🔧 CONFIGURACIÓN & PERSONALIZACIÓN
# ============================================================================
print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                      ⚙️  CONFIGURACIÓN                                      ║
╚════════════════════════════════════════════════════════════════════════════╝

VARIABLES DE ENTORNO:
  
  OPENWEATHERMAP_API_KEY        # Para fuente OpenWeatherMap
    export OPENWEATHERMAP_API_KEY="your_key_here"
  
  METEOBLUE_API_KEY             # Para fuente MeteoBlue
    export METEOBLUE_API_KEY="your_key_here"
  
  CACHE_TTL                     # Tiempo caché (segundos)
    export CACHE_TTL=900        # 15 minutos (default)

UBICACIONES (editar en dashboard/app.py):
  
  LOCATIONS = {
      "Medellín": {"lat": 6.2476, "lon": -75.5679},
      "Bogotá": {"lat": 4.7110, "lon": -74.0721},
      "Cali": {"lat": 3.4372, "lon": -76.5069},
      # Agrega más aquí
  }

ARCHIVOS HISTÓRICOS:
  
  Ubicación: data/*.csv
  Formato esperado:
    timestamp,temperature,humidity,precipitation,wind_speed
    2025-12-08 10:00:00,22.5,65.3,0.0,3.2
  
  El dashboard carga automáticamente todos los CSV disponibles

PUERTOS (editable en código):
  
  Streamlit:  http://localhost:8501
  FastAPI:    http://localhost:8000
  
  Para cambiar:
    - Streamlit: dashboard/.streamlit/config.toml
    - FastAPI:   backend/app/main.py (uvicorn.run)

STREAMLIT CONFIG:
  
  Archivo: dashboard/.streamlit/config.toml
  
  [theme]
  primaryColor = "#667eea"
  backgroundColor = "#ffffff"
  secondaryBackgroundColor = "#f0f2f6"
  
  [server]
  port = 8501
  headless = true
""")

# ============================================================================
# 📚 DOCUMENTACIÓN RÁPIDA
# ============================================================================
print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                      📚 DOCUMENTACIÓN RÁPIDA                               ║
╚════════════════════════════════════════════════════════════════════════════╝

COMIENZA CON:
  ✓ DASHBOARD_GUIDE.md        ← Guía completa del dashboard
  ✓ QUICKSTART.md             ← Inicio rápido
  ✓ README.md                 ← Descripción general

DETALLES TÉCNICOS:
  ✓ ARCHITECTURE.md           ← Arquitectura del proyecto
  ✓ INTEGRATION_STATUS.md     ← Estado de integración
  ✓ INTEGRATION_SUMMARY.md    ← Resumen de cambios

ESPECIFICACIONES:
  ✓ dashboard/README.md       ← Docs específicas dashboard
  ✓ NEXT_STEPS.md             ← Próximas mejoras

REFERENCIA:
  ✓ PROJECT_STATUS.json       ← Status actual (JSON)
  ✓ PROJECT_STATUS.txt        ← Status actual (texto)
""")

# ============================================================================
# 🚨 TROUBLESHOOTING
# ============================================================================
print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                      🆘 RESOLUCIÓN DE PROBLEMAS                            ║
╚════════════════════════════════════════════════════════════════════════════╝

PROBLEMA: Dashboard no abre
SOLUCIÓN:
  pip install streamlit==1.31.1 --force-reinstall
  python main.py dashboard

PROBLEMA: "ModuleNotFoundError"
SOLUCIÓN:
  pip install -r requirements.txt
  pip install -r backend/requirements.txt

PROBLEMA: Datos no cargan
SOLUCIÓN:
  1. Verifica conexión a internet
  2. Abre http://localhost:8501 modo "Información"
  3. Revisa "Aggregator Status"
  4. Confirma Open-Meteo disponible

PROBLEMA: Puerto ya en uso
SOLUCIÓN:
  # Encontrar proceso:
  lsof -i :8501        # Streamlit
  lsof -i :8000        # FastAPI
  
  # Matar proceso:
  kill -9 <PID>
  
  # O cambiar puerto en config

PROBLEMA: CSV no aparece en dropdown
SOLUCIÓN:
  1. Mueve archivo a data/
  2. Confirma extensión .csv
  3. Recarga página (Ctrl+F5)
  4. Reinicia dashboard

MÁS AYUDA:
  Ver: DASHBOARD_GUIDE.md → sección "Troubleshooting"
""")

# ============================================================================
# 📊 EJEMPLOS DE USO
# ============================================================================
print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                      💡 EJEMPLOS DE USO                                    ║
╚════════════════════════════════════════════════════════════════════════════╝

CASO 1: Monitoreo Simple
  $ python main.py dashboard
  → Abre dashboard
  → Pestaña "Tiempo Real"
  → Selecciona ubicación
  → Observa métricas en vivo

CASO 2: Análisis Histórico
  $ python main.py dashboard
  → Pestaña "Datos Históricos"
  → Selecciona archivo CSV
  → Filtra por fecha
  → Exporta datos de interés

CASO 3: Desarrollo Backend
  $ python main.py api
  → Accede a http://localhost:8000/docs
  → Prueba endpoints
  → Verifica respuestas JSON

CASO 4: Testing Completo
  $ python main.py test
  → Valida todos los módulos
  → Verifica caché
  → Benchmark de rendimiento

CASO 5: Stack Completo
  Terminal 1: $ python main.py legacy    # Datos históricos
  Terminal 2: $ python main.py api        # Backend
  Terminal 3: $ python main.py dashboard  # Frontend
  → Sistema completamente integrado
""")

# ============================================================================
# ✨ RESUMEN
# ============================================================================
print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                      ✨ RESUMEN EJECUTIVO                                  ║
╚════════════════════════════════════════════════════════════════════════════╝

ClimAPI v1.0.0 - Dashboard Meteorológico Unificado

ESTADO: ✅ LISTO PARA PRODUCCIÓN
INTEGRIDAD: 100%
VERSIÓN: 1.0.0

COMANDOS DISPONIBLES:
  python main.py dashboard    ← 🔥 COMIENZA AQUÍ
  python main.py api
  python main.py legacy
  python main.py test
  python main.py help

CARACTERÍSTICAS PRINCIPALES:
  ✅ Dashboard interactivo Streamlit
  ✅ 4 modos de visualización
  ✅ Múltiples fuentes de datos
  ✅ API REST documentada
  ✅ Caché inteligente TTL
  ✅ Tests de integración
  ✅ Documentación completa

TECNOLOGÍAS:
  Frontend:   Streamlit, Plotly, Pandas
  Backend:    FastAPI, Asyncio, Pydantic
  Datos:      Open-Meteo, SIATA, OpenWeatherMap, etc.

PRÓXIMOS PASOS:
  1. Ejecuta: python main.py dashboard
  2. Abre: http://localhost:8501
  3. Explora los 4 modos
  4. Lee: DASHBOARD_GUIDE.md

CONTACTO & SOPORTE:
  Documentación: Ver archivos .md en carpeta raíz
  GitHub: [Tu repositorio]
  Issues: [Tu tracker]

═══════════════════════════════════════════════════════════════════════════════

¡GRACIAS POR USAR CLIMAPI! 🌤️

═══════════════════════════════════════════════════════════════════════════════
""")
