"""
Dashboard Streamlit para ClimAPI
Visualización interactiva de datos meteorológicos de múltiples fuentes.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import asyncio
from datetime import datetime
from pathlib import Path
import sys

# Agregar backend al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.app.services.aggregator import WeatherAggregator
from backend.app.processors.storage import CacheManager
from backend.app.processors.transform import calculate_statistics

# Configuración de Streamlit
st.set_page_config(
    page_title="ClimAPI Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .source-active {
        color: #00AA00;
        font-weight: bold;
    }
    .source-inactive {
        color: #AAAAAA;
        font-style: italic;
    }
    .source-error {
        color: #FF5555;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar sesión
if "aggregator" not in st.session_state:
    st.session_state.aggregator = WeatherAggregator()
    st.session_state.cache_manager = CacheManager(ttl_minutes=15)

@st.cache_resource
def get_aggregator():
    """Retorna instancia de agregador (cacheada)."""
    return st.session_state.aggregator

@st.cache_resource
def get_cache():
    """Retorna instancia de cache (cacheada)."""
    return st.session_state.cache_manager


def main():
    """Función principal del dashboard."""
    
    # Header
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.image("https://via.placeholder.com/100?text=🌍", width=80)
    with col2:
        st.title("🌍 ClimAPI Dashboard")
        st.markdown("**Sistema de monitoreo meteorológico con múltiples fuentes**")
    with col3:
        st.markdown(f"""
        ⏰ **Última actualización:**  
        {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """)
    
    st.divider()
    
    # Sidebar - Configuración
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        # Seleccionar ubicación
        location_option = st.radio(
            "Selecciona ubicación:",
            ["Medellín", "Bogotá", "Cali", "Coordinatas personalizadas"]
        )
        
        if location_option == "Medellín":
            latitude, longitude = 6.2442, -75.5812
            location_name = "Medellín"
        elif location_option == "Bogotá":
            latitude, longitude = 4.7110, -74.0721
            location_name = "Bogotá"
        elif location_option == "Cali":
            latitude, longitude = 3.4372, -76.5225
            location_name = "Cali"
        else:
            latitude = st.number_input("Latitud", value=6.2442, format="%.4f")
            longitude = st.number_input("Longitud", value=-75.5812, format="%.4f")
            location_name = f"({latitude:.4f}, {longitude:.4f})"
        
        st.markdown(f"**📍 Ubicación:** {location_name}")
        
        # Opciones de actualización
        refresh_interval = st.slider(
            "Intervalo de actualización (segundos):",
            min_value=5,
            max_value=300,
            value=60,
            step=5
        )
        
        # Botón de actualización manual
        if st.button("🔄 Actualizar datos ahora", key="refresh_btn"):
            st.session_state.force_refresh = True
            st.rerun()
        
        st.divider()
        
        # Fuentes disponibles
        st.subheader("📊 Fuentes disponibles")
        aggregator = get_aggregator()
        sources_status = aggregator.get_sources_status()
        
        for source_name, status in sources_status.items():
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                st.write(status["icon"])
            with col2:
                st.write(f"**{status['name']}**")
            with col3:
                if status["active"]:
                    st.markdown("🟢 Activa")
                else:
                    st.markdown("🔴 Inactiva")
        
        st.divider()
        
        # Información del sistema
        st.subheader("ℹ️ Información")
        st.markdown(f"""
        **ClimAPI v1.0.0**
        
        - 🏗️ Backend: FastAPI
        - 📊 Frontend: Streamlit
        - 💾 Cache: 15 minutos
        - 🔄 Actualización: {refresh_interval}s
        
        [📚 Documentación](http://localhost:8000/docs)
        """)
    
    # Contenido principal
    
    # Tab 1: Datos actuales
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📊 Datos Actuales", "📈 Gráficos", "📋 Detalles", "ℹ️ Información"]
    )
    
    with tab1:
        st.subheader("Datos meteorológicos en tiempo real")
        
        # Obtener datos
        aggregator = get_aggregator()
        
        with st.spinner("Obteniendo datos de todas las fuentes..."):
            # Ejecutar agregador en evento asyncio
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                sources = loop.run_until_complete(
                    aggregator.fetch_all_sources(latitude, longitude)
                )
                loop.close()
            except RuntimeError:
                # En Streamlit, usar asyncio diferente
                try:
                    sources = asyncio.run(
                        aggregator.fetch_all_sources(latitude, longitude)
                    )
                except:
                    # Fallback
                    sources = aggregator.sources
        
        # Mostrar datos de cada fuente
        st.write("**Fuentes de datos:**")
        
        cols = st.columns(2)
        col_idx = 0
        
        for source_name, source in sources.items():
            with cols[col_idx % 2]:
                with st.container(border=True):
                    st.markdown(f"### {source.icon} {source.name}")
                    
                    if source.data:
                        st.success("✅ Datos disponibles")
                        
                        # Mostrar datos principales
                        if isinstance(source.data, dict):
                            # Crear columnas para mostrar valores
                            data_cols = st.columns(2)
                            
                            data_items = list(source.data.items())
                            for idx, (key, value) in enumerate(data_items[:4]):
                                with data_cols[idx % 2]:
                                    if isinstance(value, (int, float)):
                                        st.metric(label=key.replace("_", " ").title(), value=f"{value:.2f}")
                                    else:
                                        st.write(f"**{key}:** {value}")
                        
                        if source.cached:
                            st.info("💾 Datos en caché")
                        if source.timestamp:
                            st.caption(f"⏱️ {source.timestamp}")
                    
                    elif source.error:
                        st.error(f"❌ Error: {source.error}")
                    
                    else:
                        st.warning("⏸️ Fuente inactiva")
                
                col_idx += 1
        
        # Datos agregados
        st.divider()
        st.subheader("📊 Datos Agregados")
        
        aggregated = aggregator.normalize_data(latitude, longitude)
        
        if aggregated["statistics"]:
            stat_cols = st.columns(3)
            
            if "temperature" in aggregated["statistics"]:
                temp_stat = aggregated["statistics"]["temperature"]
                with stat_cols[0]:
                    st.metric(
                        label="🌡️ Temperatura Promedio",
                        value=f"{temp_stat['average']}°C",
                        delta=f"Min: {temp_stat['min']}°C, Max: {temp_stat['max']}°C"
                    )
            
            if "humidity" in aggregated["statistics"]:
                hum_stat = aggregated["statistics"]["humidity"]
                with stat_cols[1]:
                    st.metric(
                        label="💧 Humedad Promedio",
                        value=f"{hum_stat['average']}%",
                        delta=f"Min: {hum_stat['min']}%, Max: {hum_stat['max']}%"
                    )
            
            if "wind_speed" in aggregated["statistics"]:
                wind_stat = aggregated["statistics"]["wind_speed"]
                with stat_cols[2]:
                    st.metric(
                        label="💨 Viento Promedio",
                        value=f"{wind_stat['average']} m/s",
                        delta=f"Min: {wind_stat['min']}, Max: {wind_stat['max']}"
                    )
    
    with tab2:
        st.subheader("Visualizaciones")
        
        # Preparar datos para gráficos
        aggregator = get_aggregator()
        sources_status = aggregator.get_sources_status()
        
        # Gráfico de fuentes activas vs inactivas
        col1, col2 = st.columns(2)
        
        with col1:
            active_count = sum(1 for s in sources_status.values() if s["active"])
            inactive_count = len(sources_status) - active_count
            
            fig = go.Figure(data=[
                go.Pie(
                    labels=["Activas", "Inactivas"],
                    values=[active_count, inactive_count],
                    hole=0.3,
                    marker=dict(colors=["#00AA00", "#AAAAAA"])
                )
            ])
            fig.update_layout(title="Estado de Fuentes")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            sources_with_data = sum(1 for s in sources_status.values() if s["has_data"])
            sources_with_error = sum(1 for s in sources_status.values() if s["error"])
            
            fig = go.Figure(data=[
                go.Pie(
                    labels=["Con datos", "Con error"],
                    values=[sources_with_data, sources_with_error],
                    hole=0.3,
                    marker=dict(colors=["#4CAF50", "#FF5252"])
                )
            ])
            fig.update_layout(title="Disponibilidad de Datos")
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Detalles técnicos")
        
        # Estado del sistema
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Cache Manager:**")
            cache = get_cache()
            cache_stats = cache.get_stats()
            st.json(cache_stats)
        
        with col2:
            st.write("**Estado de Fuentes:**")
            aggregator = get_aggregator()
            sources_status = aggregator.get_sources_status()
            st.json(sources_status)
        
        # Datos JSON
        st.write("**Datos Agregados (JSON):**")
        aggregated = aggregator.normalize_data(latitude, longitude)
        st.json(aggregated)
    
    with tab4:
        st.subheader("Información del Sistema")
        
        st.markdown("""
        ### 🌍 ClimAPI Dashboard
        
        Sistema de monitoreo meteorológico integrado con múltiples fuentes de datos en tiempo real.
        
        #### Características principales:
        - 📊 **Agregación de datos:** Obtiene datos de múltiples fuentes simultáneamente
        - 🔄 **Caché inteligente:** TTL configurable para optimizar consultas
        - 📈 **Visualizaciones:** Gráficos interactivos con Plotly
        - 🚀 **API REST:** Backend FastAPI con documentación automática
        - 🔗 **Integración:** Open-Meteo, SIATA, OpenWeatherMap, MeteoBlue, Radar IDEAM
        
        #### Fuentes disponibles:
        1. **Open-Meteo** 🌐 - Datos globales (siempre disponible)
        2. **SIATA** 🏙️ - Específico de Medellín
        3. **OpenWeatherMap** ☁️ - Requiere API key
        4. **MeteoBlue** 🎯 - Requiere API key
        5. **Radar IDEAM** 📡 - Datos limitados
        
        #### Próximos pasos:
        - [ ] Agregar más ciudades
        - [ ] Pronóstico a 7 días
        - [ ] Alertas meteorológicas
        - [ ] Historial de datos
        - [ ] Exportación de datos
        
        #### Contacto y Soporte:
        - 📖 [Documentación API](http://localhost:8000/docs)
        - 🐛 [Reportar problemas](https://github.com/lrdlk/ClimAPI/issues)
        - 💬 [Sugerencias](https://github.com/lrdlk/ClimAPI/discussions)
        """)


if __name__ == "__main__":
    main()
