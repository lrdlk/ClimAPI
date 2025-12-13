# 🗺️ CLIMAPI - Roadmap del Proyecto

**De la toma de datos a la API con MLflow**

---

## 📊 Estado General del Proyecto

| Métrica | Valor |
|---------|-------|
| **Horizonte estimado** | 8-14 semanas (2-3.5 meses) |
| **Fase actual** | 15% (2/8 etapas en progreso) |
| **Etapas completadas** | 2/8 |
| **Próxima recomendada** | Procesamiento y limpieza |
| **Tareas completadas** | 5/12 |

---

## 🎯 Etapas del Proyecto

### ✅ 1. Recolección de datos
**Progreso: 75%** 🟢

Obtener datos climáticos de APIs y almacenarlos.

**Completado:**
- ✅ Configurar cuentas y claves de APIs climáticas (Meteoblue, OpenWeatherMap, Meteosource, Open-Meteo)
- ✅ Desarrollar scripts de extracción en tiempo real/histórico
- ✅ Implementar clientes para 6 fuentes de datos (Meteoblue, Open-Meteo, OpenWeather, Meteosource, IDEAM, SIATA)
- ✅ Sistema de logs automático
- ✅ Dashboard para visualización de consultas

**Pendiente:**
- ⏳ Elegir y poblar la base de datos (PostgreSQL/MongoDB)
- ⏳ Define esquemas y backups
- ⏳ Automatizar ingesta periódica (cron jobs)

---

### 🔄 2. Procesamiento y limpieza
**Progreso: 20%** 🟡

Normalizar, unificar formatos y preparar datasets.

**Completado:**
- ✅ Documentación de estructura de datos por API
- ✅ Guía de normalización en README.md

**Pendiente:**
- ⏳ Implementar `src/processors/data_normalizer.py`
- ⏳ Manejar valores nulos, outliers y estandarizar unidades
- ⏳ Crear esquema común (weather_schema.json, forecast_schema.json)
- ⏳ Documentar decisiones de limpieza
- ⏳ Crear pipeline de transformación ETL
- ⏳ Validar integridad de datos

**Duración estimada:** 1-2 semanas

---

### 3. Análisis exploratorio y feature engineering
**Progreso: 0%** ⚪

Visualizar series temporales y crear variables útiles.

**Tareas:**
- ⏳ Visualizar correlaciones y estacionalidad
- ⏳ Generar notebooks de análisis exploratorio
- ⏳ Crear features (hora, día semana, estacionalidad, ventanas móviles)
- ⏳ Detectar patrones climáticos
- ⏳ Análisis de correlación entre variables
- ⏳ Identificar outliers y anomalías
- ⏳ Documentar features y su significado
- ⏳ Crear visualizaciones con Plotly/Matplotlib

**Duración estimada:** 2-3 semanas

---

### 4. Entrenamiento de modelos
**Progreso: 0%** ⚪

Probar algoritmos, dividir train/test y evaluar métricas.

**Tareas:**
- ⏳ Dividir datos en train/test/validation
- ⏳ Definir métricas (RMSE, MAE, R²)
- ⏳ Entrenar modelos baseline (Linear Regression, ARIMA)
- ⏳ Probar modelos avanzados (Random Forest, XGBoost, LSTM)
- ⏳ Optimizar hiperparámetros (Grid Search, Optuna)
- ⏳ Evaluar y comparar modelos
- ⏳ Prevenir data leakage
- ⏳ Validación cruzada temporal

**Duración estimada:** 2-3 semanas

---

### 5. Integración con MLflow
**Progreso: 0%** ⚪

Registrar experimentos y versionar modelos.

**Tareas:**
- ⏳ Configurar servidor MLflow local/remoto
- ⏳ Registrar parámetros de entrenamiento
- ⏳ Registrar métricas de evaluación
- ⏳ Guardar modelos en Model Registry
- ⏳ Versionar datasets y modelos
- ⏳ Crear experimentos por tipo de modelo
- ⏳ Implementar tracking automático
- ⏳ Configurar artefactos (plots, reports)

**Duración estimada:** 1-2 semanas

---

### 6. API con FastAPI
**Progreso: 0%** ⚪

Exponer endpoints y conectar el modelo registrado.

**Tareas:**
- ⏳ Crear proyecto FastAPI
- ⏳ Endpoint `/predict` (predicción de clima)
- ⏳ Endpoint `/health` (estado del servicio)
- ⏳ Endpoint `/model/info` (información del modelo)
- ⏳ Validación de inputs con Pydantic
- ⏳ Cargar modelo desde MLflow
- ⏳ Manejo de errores y excepciones
- ⏳ Documentación automática (Swagger)
- ⏳ Rate limiting y autenticación
- ⏳ Tests unitarios de la API

**Duración estimada:** 2 semanas

---

### 7. Dashboard con Streamlit
**Progreso: 80%** 🟢

Visualizar datos y predicciones en tiempo real.

**Completado:**
- ✅ Dashboard básico implementado (`dashboard.py`)
- ✅ Página de inicio con estadísticas
- ✅ Verificación de APIs en tiempo real
- ✅ Visualización de consultas realizadas
- ✅ Formulario para nuevas consultas
- ✅ Explorador de datos por API
- ✅ Gráficos interactivos con Plotly

**Pendiente:**
- ⏳ Conectar dashboard a la API de predicción
- ⏳ Mostrar predicciones vs datos reales
- ⏳ Añadir filtros avanzados (fecha, ubicación, variable)
- ⏳ Métricas de rendimiento del modelo
- ⏳ Comparación entre modelos

**Duración estimada:** 1 semana (completar)

---

### 8. Despliegue y pruebas
**Progreso: 0%** ⚪

Dockerizar, desplegar y monitorear el sistema.

**Tareas:**
- ⏳ Dockerizar API con FastAPI
- ⏳ Dockerizar Dashboard Streamlit
- ⏳ Dockerizar MLflow server
- ⏳ Docker Compose para orquestación
- ⏳ Optimizar imágenes Docker
- ⏳ Configurar CI/CD (GitHub Actions)
- ⏳ Desplegar en cloud (AWS/GCP/Azure/Railway)
- ⏳ Pruebas de integración end-to-end
- ⏳ Pruebas de carga (locust, artillery)
- ⏳ Configurar monitoreo (Prometheus, Grafana)
- ⏳ Alertas tempranas (email, Slack)
- ⏳ Documentación de despliegue

**Duración estimada:** 2-3 semanas

---

## ✅ Checklist General de Tareas

### Infraestructura y Configuración
- [x] Configurar cuentas y claves de APIs climáticas
- [x] Desarrollar scripts de extracción en tiempo real/histórico
- [ ] Elegir y poblar la base de datos (PostgreSQL/MongoDB)
- [ ] Configurar servidor MLflow

### Procesamiento de Datos
- [ ] Manejar valores nulos, outliers y estandarizar unidades
- [ ] Visualizar correlaciones y estacionalidad
- [ ] Crear features (hora, estacionalidad, ventanas móviles)
- [ ] Dividir datos y definir métricas (RMSE, MAE)

### Machine Learning
- [ ] Entrenar modelos baseline y avanzados
- [ ] Registrar parámetros, métricas y modelo en MLflow
- [ ] Optimizar hiperparámetros

### Desarrollo de APIs
- [ ] Crear endpoints /predict y /health
- [x] Conectar dashboard a datos existentes
- [ ] Conectar dashboard a la API de predicción

### Despliegue
- [ ] Dockerizar API y dashboard
- [ ] Ejecutar pruebas de integración y monitoreo

**Progreso:** 5/12 tareas completadas (42%)

---

## ⚠️ Riesgos Críticos

### 1. Integración con múltiples APIs climáticas
- **Riesgo:** Límites de cuotas, cambios en endpoints, latencia variable
- **Mitigación:** 
  - Implementar rate limiting inteligente
  - Cache de resultados (requests-cache)
  - Fallback a APIs alternativas
  - Monitoreo de disponibilidad (dashboard implementado ✅)

### 2. Escalabilidad del almacenamiento
- **Riesgo:** Datos históricos crecen rápidamente, costos de almacenamiento
- **Mitigación:**
  - Base de datos optimizada (índices, particionado)
  - Políticas de retención de datos
  - Compresión de datos antiguos
  - Archivado en S3/Object Storage

### 3. Calidad de datos históricos
- **Riesgo:** Datos faltantes, inconsistencias, outliers extremos
- **Mitigación:**
  - Pipeline de validación robusto
  - Documentación de decisiones de limpieza
  - Múltiples fuentes para redundancia
  - Alertas de calidad de datos

### 4. Latencia y disponibilidad de la API
- **Riesgo:** Tiempos de respuesta altos, downtime
- **Mitigación:**
  - Caching de predicciones frecuentes
  - Load balancing
  - Health checks automáticos
  - SLA y monitoreo continuo

---

## 🚀 Oportunidades de Paralelización

### Mientras el modelo se entrena:
- ✅ Diseñar arquitectura de la API (en progreso)
- ✅ Desarrollar dashboard básico (completado)
- ⏳ Definir esquemas de base de datos
- ⏳ Crear documentación de API

### Durante ingesta de datos:
- ✅ Iterar EDA (análisis exploratorio)
- ✅ Desarrollar feature engineering en notebooks
- ⏳ Entrenar modelos baseline
- ⏳ Configurar MLflow

### Desde las primeras etapas:
- ✅ Automatizar pruebas unitarias (verificación de APIs)
- ⏳ Configurar CI/CD pipeline
- ⏳ Preparar infraestructura Docker
- ⏳ Documentación continua

---

## 📅 Cronograma Estimado

```
Semana 1-2:   ✅ Recolección de datos (75% completado)
Semana 3-4:   🔄 Procesamiento y limpieza (en progreso)
Semana 5-7:   ⏳ Análisis exploratorio y feature engineering
Semana 8-10:  ⏳ Entrenamiento de modelos + MLflow
Semana 11-12: ⏳ API con FastAPI
Semana 13:    🔄 Dashboard finalización (80% completado)
Semana 14-16: ⏳ Despliegue, pruebas y monitoreo
```

**Estado actual:** Semana 2-3 ✅

---

## 🎯 Próximos Pasos Inmediatos

### Esta Semana
1. **[ALTA]** Implementar script de normalización (`data_normalizer.py`)
2. **[ALTA]** Crear esquemas comunes de datos (JSON schemas)
3. **[MEDIA]** Configurar base de datos PostgreSQL/MongoDB
4. **[MEDIA]** Iniciar notebooks de EDA

### Próxima Semana
1. **[ALTA]** Pipeline ETL completo
2. **[ALTA]** Feature engineering básico
3. **[MEDIA]** Primer modelo baseline (ARIMA)
4. **[BAJA]** Configurar MLflow local

---

## 📝 Notas de Progreso

### 2024-12-13
- ✅ Dashboard Streamlit implementado con verificación de APIs
- ✅ Sistema de visualización de consultas existentes
- ✅ Integración de 6 fuentes de datos (Meteoblue, Open-Meteo, OpenWeather, Meteosource, IDEAM, SIATA)
- ✅ Documentación completa en README.md
- ✅ Guía de normalización de datos

### Pendiente para esta semana
- ⏳ Implementar normalizador de datos
- ⏳ Crear esquemas JSON comunes
- ⏳ Configurar base de datos

---

## 🔗 Enlaces Útiles

- **Roadmap interactivo:** https://interactive.phind.com/streaming-preview/session_1765509468704/index.html
- **Documentación:** [README.md](README.md)
- **Guía del Dashboard:** [DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md)

---

## 📊 Visualización del Progreso

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Recolección de datos        ████████████████░░░░ 75%
Procesamiento y limpieza    ████░░░░░░░░░░░░░░░░ 20%
EDA y feature engineering   ░░░░░░░░░░░░░░░░░░░░  0%
Entrenamiento de modelos    ░░░░░░░░░░░░░░░░░░░░  0%
Integración MLflow          ░░░░░░░░░░░░░░░░░░░░  0%
API con FastAPI             ░░░░░░░░░░░░░░░░░░░░  0%
Dashboard Streamlit         ████████████████░░░░ 80%
Despliegue y pruebas        ░░░░░░░░░░░░░░░░░░░░  0%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Progreso Global: ██████████░░░░░░░░░░░░░░░░░░░░ 27%
```

---

**Última actualización:** 13 de diciembre de 2025  
**Versión:** 1.0.0  
**Mantener este roadmap actualizado con cada hito alcanzado** ✅
