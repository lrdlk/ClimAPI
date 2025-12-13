# 🎨 CLIMAPI Dashboard - Guía de Uso Rápido

## 🚀 Inicio Rápido

### 1. Instalar dependencias
```bash
pip install streamlit streamlit-option-menu
```

### 2. Ejecutar el dashboard
```bash
streamlit run dashboard.py
```

El dashboard se abrirá automáticamente en `http://localhost:8501`

---

## 📋 Funcionalidades

### 🏠 Página de Inicio
- Vista general del sistema
- Estadísticas de consultas realizadas
- Gráfico de actividad reciente
- Contador de datos por API

### ✅ Verificación de APIs
- **Verifica todas las APIs con un solo clic**
- Endpoints de prueba en tiempo real:
  - ☁️ Meteoblue
  - 🌐 Open-Meteo
  - 🌤️ OpenWeatherMap
  - 🌦️ Meteosource
  - 📡 IDEAM Radar (AWS)
  - 🌐 SIATA

- Muestra estado de configuración
- Detecta errores comunes (401, 429, timeout)

### 📊 Consultas Realizadas
- Lista de todas las consultas previas
- Selector interactivo por fecha y ubicación
- Pestañas por fuente de datos
- Visualizaciones automáticas:
  - Gráficos de temperatura
  - Tablas de datos
  - Métricas destacadas

### 🔍 Nueva Consulta
- **Formulario intuitivo** para consultas
- Ubicaciones predefinidas de Colombia:
  - Medellín
  - Bogotá
  - Cartagena
  - Cali
  - Barranquilla
  - Personalizado (coordenadas manuales)

- Tipos de consulta:
  - Completa (todas las APIs)
  - Individual por API

- Los datos se guardan automáticamente en `data/`

### 📁 Datos por API
- Explorador de datos por fuente
- Visualización de archivos guardados
- Previsualización de datos:
  - JSON para Meteoblue, OpenWeather, Meteosource
  - DataFrames para Open-Meteo (CSV)
- Muestra hasta 10 archivos más recientes

---

## 🎯 Casos de Uso

### Verificar Estado de las APIs
1. Ve a "✅ Verificación APIs"
2. Clic en "🔄 Verificar Todas las APIs"
3. Espera los resultados en tiempo real
4. Revisa si hay errores de configuración

### Realizar una Nueva Consulta
1. Ve a "🔍 Nueva Consulta"
2. Selecciona una ubicación (o ingresa coordenadas)
3. Elige el tipo de consulta
4. Clic en "🚀 Realizar Consulta"
5. Espera la confirmación
6. Los datos se guardan automáticamente

### Visualizar Consultas Previas
1. Ve a "📊 Consultas Realizadas"
2. Selecciona una consulta del dropdown
3. Navega por las pestañas de cada API
4. Visualiza gráficos y tablas interactivas

### Explorar Datos Guardados
1. Ve a "📁 Datos por API"
2. Selecciona la API de interés
3. Explora los archivos disponibles
4. Expande para ver detalles

---

## ⚙️ Configuración

### Variables de Entorno Requeridas

El dashboard lee automáticamente del archivo `.env`:

```env
METEOBLUE_API_KEY=tu_api_key
METEOBLUE_SHARED_SECRET=tu_shared_secret
OPENWEATHER_API_KEY=tu_api_key
METEOSOURCE_API_KEY=tu_api_key
```

### APIs sin Configuración
- **Open-Meteo**: Funciona sin API key
- **IDEAM**: Acceso público a AWS
- **SIATA**: Datos públicos

---

## 🐛 Solución de Problemas

### Error: "No module named 'streamlit'"
```bash
pip install streamlit
```

### Error: "Port 8501 is already in use"
```bash
streamlit run dashboard.py --server.port 8502
```

### Error: "ModuleNotFoundError: No module named 'main'"
Asegúrate de ejecutar el dashboard desde el directorio raíz del proyecto:
```bash
cd ClimApi
streamlit run dashboard.py
```

### Las APIs no responden
1. Verifica tu conexión a internet
2. Revisa el archivo `.env` con las API keys correctas
3. Usa la página "✅ Verificación APIs" para diagnosticar

### No se muestran consultas previas
- Realiza al menos una consulta primero
- Verifica que exista el directorio `data/`
- Revisa que haya archivos `.json` en `data/`

---

## 📊 Capturas de Pantalla

### Página de Inicio
- Métricas: Total de consultas por API
- Gráfico: Histograma de consultas por fecha
- Tarjetas: Resumen de ubicaciones

### Verificación de APIs
- Estado visual: ✅ (OK), ❌ (Error), ⚠️ (Advertencia)
- Mensajes descriptivos de error
- Información de configuración

### Consultas Realizadas
- Selector de consultas con fecha y ubicación
- Métricas: Ubicación, Coordenadas, Altitud
- Pestañas por fuente de datos
- Gráficos interactivos de Plotly

---

## 🎨 Personalización

### Cambiar el Puerto
```bash
streamlit run dashboard.py --server.port 8080
```

### Modo Oscuro
En el dashboard, menú superior derecho → Settings → Theme → Dark

### Ocultar Menú de Streamlit
Edita `dashboard.py` y agrega en `st.set_page_config()`:
```python
menu_items={
    'Get Help': None,
    'Report a bug': None,
    'About': "CLIMAPI Dashboard v1.0"
}
```

---

## 🔗 Enlaces Útiles

- **Documentación Streamlit**: https://docs.streamlit.io
- **Plotly Gráficos**: https://plotly.com/python/
- **CLIMAPI GitHub**: [Tu repositorio]

---

## 📝 Notas

- El dashboard NO modifica archivos en `src/`
- Todas las consultas se guardan en `data/`
- Los logs se generan automáticamente
- Cache de Streamlit: Los datos se actualizan al recargar

---

**Versión**: 1.0.0  
**Última actualización**: Diciembre 2025
