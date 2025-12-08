# ClimAPI Dashboard

Dashboard integrado para visualización de datos meteorológicos combinando:
- 📊 **Datos en tiempo real** (múltiples fuentes)
- 📈 **Datos históricos** (CSV)
- 📋 **Comparativas** (entre fuentes)
- ℹ️ **Información del sistema**

## 🚀 Ejecución

### Opción 1: Solo Dashboard (Recomendado)
```bash
streamlit run dashboard/app.py
```

### Opción 2: Con Backend API
```bash
# Terminal 1
python main.py api

# Terminal 2
streamlit run dashboard/app.py
```

**Acceso:**
- Dashboard: http://localhost:8501
- API: http://localhost:8000/docs

## 📊 Pestañas Disponibles

### 📊 Tiempo Real
- Selector de ubicación (Medellín, Bogotá, Cali, personalizado)
- Obtiene datos de 5 fuentes simultáneamente
- Indicadores de estado por fuente
- Agregación de estadísticas
- Gráficos interactivos

### 📈 Datos Históricos
- Carga CSV con histórico
- Filtro de fechas
- Gráficos de temperatura, humedad, precipitación, viento
- Tabla de datos detallados
- Exportación a CSV

### 📋 Comparativa
- Comparación entre fuentes de datos
- Valores de temperatura, humedad, viento
- Estado de cada fuente

### ℹ️ Información
- Descripción del sistema
- Estado de fuentes disponibles
- Estado del caché
- Datos JSON

## 🌍 Fuentes de Datos

| Fuente | Icono | Estado | Datos |
|--------|-------|--------|-------|
| Open-Meteo | 🌐 | ✅ Activo | Global |
| SIATA | 🏙️ | ✅ Activo | Medellín |
| OpenWeatherMap | ☁️ | ⏸️ API key | Global |
| MeteoBlue | 🎯 | ⏸️ API key | Premium |
| Radar IDEAM | 📡 | ⏸️ Limitado | Colombia |

## ⚙️ Configuración

### Variables de Entorno (backend/.env)
```env
CACHE_TTL=15
OPENWEATHERMAP_API_KEY=your_key
METEOBLUE_API_KEY=your_key
```

### Ubicaciones Predefinidas
- **Medellín:** 6.2442, -75.5812
- **Bogotá:** 4.7110, -74.0721
- **Cali:** 3.4372, -76.5225

## 📈 Características

✅ Actualización en tiempo real  
✅ Caché inteligente (15 min TTL)  
✅ Manejo de errores robusto  
✅ Interfaz responsive  
✅ Gráficos interactivos  
✅ Exportación de datos  
✅ Multi-ubicación  
✅ Historial de datos  

## 🧪 Testing

```bash
# Pruebas de integración
python streamlit_dashboard/test_integration.py
```

## 📞 Soporte

- 📖 Documentación: `../README.md`
- 🐛 Issues: https://github.com/lrdlk/ClimAPI/issues
- 💬 Discussions: https://github.com/lrdlk/ClimAPI/discussions

## 📜 Licencia

MIT License - Ver LICENSE para detalles
