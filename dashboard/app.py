"""
Dashboard meteorológico integrado - ClimAPI.

Combina:
1. Datos históricos (CSV)
2. Datos en tiempo real (APIs multi-fuente)
3. Pronósticos
4. Análisis comparativos

Fuentes de datos:
- Open-Meteo (tiempo real, gratuito)
- SIATA (Medellín, tiempo real)
- OpenWeatherMap (requiere API key)
- MeteoBlue (requiere API key)
- Radar IDEAM (Colombia)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
import asyncio
from datetime import datetime

# Agregar el directorio raíz al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importar del procesamiento existente
from processing.storage import load_from_csv

# Importar del nuevo backend
from backend.app.services.aggregator import WeatherAggregator
from backend.app.processors.storage import CacheManager
from backend.app.processors.transform import calculate_statistics


def load_data(filepath: str = "data/weather_data.csv") -> pd.DataFrame:
    """
    Carga los datos meteorológicos desde un archivo CSV.
    
    Args:
        filepath: Ruta del archivo CSV
    
    Returns:
        pd.DataFrame: DataFrame con los datos meteorológicos
    """
    try:
        df = load_from_csv(filepath)
        return df
    except FileNotFoundError:
        st.error(f"❌ No se encontró el archivo {filepath}. Por favor, ejecuta main.py primero para obtener datos.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error al cargar los datos: {e}")
        st.stop()


def create_temperature_chart(df: pd.DataFrame, date_range: tuple) -> go.Figure:
    """
    Crea un gráfico de línea para la temperatura.
    
    Args:
        df: DataFrame con los datos meteorológicos
        date_range: Tupla con (fecha_inicio, fecha_fin)
    
    Returns:
        go.Figure: Gráfico de Plotly
    """
    df_filtered = df.loc[date_range[0]:date_range[1]]
    
    fig = px.line(
        df_filtered,
        x=df_filtered.index,
        y='temperatura_c',
        title='🌡️ Temperatura (°C)',
        labels={'temperatura_c': 'Temperatura (°C)', 'index': 'Fecha y Hora'},
        color_discrete_sequence=['#FF6B6B']
    )
    fig.update_layout(
        xaxis_title="Fecha y Hora",
        yaxis_title="Temperatura (°C)",
        hovermode='x unified'
    )
    return fig


def create_humidity_chart(df: pd.DataFrame, date_range: tuple) -> go.Figure:
    """
    Crea un gráfico de línea para la humedad.
    
    Args:
        df: DataFrame con los datos meteorológicos
        date_range: Tupla con (fecha_inicio, fecha_fin)
    
    Returns:
        go.Figure: Gráfico de Plotly
    """
    df_filtered = df.loc[date_range[0]:date_range[1]]
    
    fig = px.line(
        df_filtered,
        x=df_filtered.index,
        y='humedad_porcentaje',
        title='💧 Humedad Relativa (%)',
        labels={'humedad_porcentaje': 'Humedad (%)', 'index': 'Fecha y Hora'},
        color_discrete_sequence=['#4ECDC4']
    )
    fig.update_layout(
        xaxis_title="Fecha y Hora",
        yaxis_title="Humedad (%)",
        hovermode='x unified'
    )
    return fig


def create_precipitation_chart(df: pd.DataFrame, date_range: tuple) -> go.Figure:
    """
    Crea un gráfico de barras para la precipitación.
    
    Args:
        df: DataFrame con los datos meteorológicos
        date_range: Tupla con (fecha_inicio, fecha_fin)
    
    Returns:
        go.Figure: Gráfico de Plotly
    """
    df_filtered = df.loc[date_range[0]:date_range[1]]
    
    fig = px.bar(
        df_filtered,
        x=df_filtered.index,
        y='precipitacion_mm',
        title='🌧️ Precipitación (mm)',
        labels={'precipitacion_mm': 'Precipitación (mm)', 'index': 'Fecha y Hora'},
        color_discrete_sequence=['#95E1D3']
    )
    fig.update_layout(
        xaxis_title="Fecha y Hora",
        yaxis_title="Precipitación (mm)",
        hovermode='x unified'
    )
    return fig


def create_wind_speed_chart(df: pd.DataFrame, date_range: tuple) -> go.Figure:
    """
    Crea un gráfico de línea para la velocidad del viento.
    
    Args:
        df: DataFrame con los datos meteorológicos
        date_range: Tupla con (fecha_inicio, fecha_fin)
    
    Returns:
        go.Figure: Gráfico de Plotly
    """
    df_filtered = df.loc[date_range[0]:date_range[1]]
    
    fig = px.line(
        df_filtered,
        x=df_filtered.index,
        y='velocidad_viento_kmh',
        title='💨 Velocidad del Viento (km/h)',
        labels={'velocidad_viento_kmh': 'Velocidad (km/h)', 'index': 'Fecha y Hora'},
        color_discrete_sequence=['#F38181']
    )
    fig.update_layout(
        xaxis_title="Fecha y Hora",
        yaxis_title="Velocidad del Viento (km/h)",
        hovermode='x unified'
    )
    return fig


def main():
    """
    Función principal que configura y ejecuta el dashboard integrado.
    """
    # Configuración de la página
    st.set_page_config(
        page_title="ClimAPI Dashboard",
        page_icon="🌍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Aplicar tema personalizado
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
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.image("https://via.placeholder.com/100?text=🌍", width=80)
    with col2:
        st.title("🌍 ClimAPI Dashboard")
        st.markdown("**Sistema integrado de monitoreo meteorológico**")
    with col3:
        st.markdown(f"⏰ Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    st.divider()
    
    # Inicializar sesión
    if "aggregator" not in st.session_state:
        st.session_state.aggregator = WeatherAggregator()
        st.session_state.cache_manager = CacheManager(ttl_minutes=15)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        # Pestañas de modo
        tab_mode = st.radio(
            "Selecciona vista:",
            ["📊 Tiempo Real", "📈 Datos Históricos", "📋 Comparativa", "ℹ️ Información"]
        )
        
        st.divider()
        
        if tab_mode == "📊 Tiempo Real":
            st.subheader("Ubicación")
            location_option = st.radio(
                "Selecciona ubicación:",
                ["Medellín", "Bogotá", "Cali", "Personalizado"]
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
            
            # Controles de actualización
            refresh_interval = st.slider(
                "Intervalo de actualización (seg):",
                min_value=5,
                max_value=300,
                value=60,
                step=5
            )
            
            if st.button("🔄 Actualizar ahora"):
                st.session_state.force_refresh = True
                st.rerun()
        
        elif tab_mode == "📈 Datos Históricos":
            st.subheader("Datos")
            data_file = st.text_input(
                "📁 Archivo de datos",
                value="data/weather_data.csv",
                help="Ruta al archivo CSV con los datos meteorológicos"
            )
        
        st.divider()
        
        # Fuentes disponibles
        st.subheader("📊 Fuentes Disponibles")
        aggregator = st.session_state.aggregator
        sources_status = aggregator.get_sources_status()
        
        for source_name, status in sources_status.items():
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                st.write(status["icon"])
            with col2:
                st.write(f"**{status['name']}**")
            with col3:
                st.markdown("🟢" if status["active"] else "🔴")
    
    # Contenido principal según tab seleccionada
    if tab_mode == "📊 Tiempo Real":
        show_realtime_dashboard(latitude, longitude, location_name)
    
    elif tab_mode == "📈 Datos Históricos":
        show_historical_dashboard(data_file)
    
    elif tab_mode == "📋 Comparativa":
        show_comparison_dashboard()
    
    else:
        show_info_dashboard()


def show_realtime_dashboard(latitude: float, longitude: float, location_name: str):
    """Muestra dashboard de tiempo real con datos de múltiples fuentes."""
    
    st.subheader(f"📊 Datos en Tiempo Real - {location_name}")
    
    # Obtener datos
    aggregator = st.session_state.aggregator
    
    with st.spinner("Obteniendo datos de todas las fuentes..."):
        try:
            # Ejecutar agregador
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            sources = loop.run_until_complete(
                aggregator.fetch_all_sources(latitude, longitude)
            )
            loop.close()
        except:
            try:
                sources = asyncio.run(
                    aggregator.fetch_all_sources(latitude, longitude)
                )
            except:
                sources = aggregator.sources
    
    # Mostrar datos por fuente en columnas
    st.write("**Fuentes de datos:**")
    
    cols = st.columns(2)
    col_idx = 0
    
    for source_name, source in sources.items():
        with cols[col_idx % 2]:
            with st.container(border=True):
                st.markdown(f"### {source.icon} {source.name}")
                
                if source.data:
                    st.success("✅ Datos disponibles")
                    
                    if isinstance(source.data, dict):
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
    
    # Gráficos
    st.divider()
    st.subheader("📈 Visualizaciones")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sources_status = aggregator.get_sources_status()
        active_count = sum(1 for s in sources_status.values() if s["active"])
        
        fig = go.Figure(data=[
            go.Pie(
                labels=["Activas", "Inactivas"],
                values=[active_count, len(sources_status) - active_count],
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


def show_historical_dashboard(data_file: str):
    """Muestra dashboard con datos históricos de CSV."""
    
    st.subheader("📈 Datos Históricos")
    
    try:
        df = load_from_csv(data_file)
    except FileNotFoundError:
        st.error(f"❌ No se encontró el archivo {data_file}. Por favor, ejecuta main.py primero.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error al cargar los datos: {e}")
        st.stop()
    
    # Información general
    st.metric("Total de registros", len(df))
    col1, col2, col3 = st.columns(3)
    
    if 'temperatura_c' in df.columns:
        with col1:
            st.metric("🌡️ Temp. Promedio", f"{df['temperatura_c'].mean():.1f} °C")
        with col2:
            st.metric("🌡️ Temp. Máxima", f"{df['temperatura_c'].max():.1f} °C")
        with col3:
            st.metric("🌡️ Temp. Mínima", f"{df['temperatura_c'].min():.1f} °C")
    
    # Filtro de fechas
    st.markdown("### 📅 Filtro de Fechas")
    min_date = df.index.min().date()
    max_date = df.index.max().date()
    
    date_range = st.date_input(
        "Selecciona el rango de fechas",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = min_date
        end_date = max_date
    
    start_datetime = pd.Timestamp(start_date)
    end_datetime = pd.Timestamp(end_date) + pd.Timedelta(days=1)
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        if 'temperatura_c' in df.columns:
            st.plotly_chart(
                create_temperature_chart(df, (start_datetime, end_datetime)),
                use_container_width=True
            )
        
        if 'precipitacion_mm' in df.columns:
            st.plotly_chart(
                create_precipitation_chart(df, (start_datetime, end_datetime)),
                use_container_width=True
            )
    
    with col2:
        if 'humedad_porcentaje' in df.columns:
            st.plotly_chart(
                create_humidity_chart(df, (start_datetime, end_datetime)),
                use_container_width=True
            )
        
        if 'velocidad_viento_kmh' in df.columns:
            st.plotly_chart(
                create_wind_speed_chart(df, (start_datetime, end_datetime)),
                use_container_width=True
            )
    
    # Tabla de datos
    st.markdown("---")
    st.subheader("📋 Datos Detallados")
    df_filtered = df.loc[start_datetime:end_datetime]
    st.dataframe(df_filtered, use_container_width=True)
    
    # Descargar datos
    csv = df_filtered.to_csv()
    st.download_button(
        label="📥 Descargar datos filtrados (CSV)",
        data=csv,
        file_name=f"weather_data_{start_date}_{end_date}.csv",
        mime="text/csv"
    )


def show_comparison_dashboard():
    """Muestra comparativa entre fuentes de datos."""
    
    st.subheader("📋 Comparativa de Fuentes")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        location_option = st.selectbox(
            "Ubicación:",
            ["Medellín", "Bogotá", "Cali"]
        )
    
    if location_option == "Medellín":
        latitude, longitude = 6.2442, -75.5812
    elif location_option == "Bogotá":
        latitude, longitude = 4.7110, -74.0721
    else:
        latitude, longitude = 3.4372, -76.5225
    
    if st.button("Comparar fuentes"):
        aggregator = st.session_state.aggregator
        
        with st.spinner("Obteniendo datos..."):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                sources = loop.run_until_complete(
                    aggregator.fetch_all_sources(latitude, longitude)
                )
                loop.close()
            except:
                sources = aggregator.sources
        
        # Tabla comparativa
        comparison_data = []
        for source_name, source in sources.items():
            if source.data and isinstance(source.data, dict):
                row = {
                    "Fuente": source.name,
                    "Temperatura": source.data.get("temperature", "-"),
                    "Humedad": source.data.get("humidity", "-"),
                    "Viento": source.data.get("wind_speed", "-"),
                    "Estado": "✅" if source.data else "❌"
                }
                comparison_data.append(row)
        
        if comparison_data:
            df_comparison = pd.DataFrame(comparison_data)
            st.dataframe(df_comparison, use_container_width=True)
        else:
            st.info("No hay datos disponibles para comparar")


def show_info_dashboard():
    """Muestra información del sistema."""
    
    st.subheader("ℹ️ Información del Sistema")
    
    st.markdown("""
    ### 🌍 ClimAPI Dashboard
    
    Sistema integrado de monitoreo meteorológico que combina:
    
    #### Características principales:
    - 📊 **Datos en tiempo real:** Obtiene de múltiples fuentes simultáneamente
    - 📈 **Datos históricos:** Análisis de CSV almacenados
    - 🔄 **Caché inteligente:** TTL de 15 minutos
    - 📱 **Interfaz responsive:** Compatible con escritorio y móvil
    - 🔗 **Multi-fuente:** Open-Meteo, SIATA, OpenWeatherMap, MeteoBlue, Radar IDEAM
    
    #### Fuentes disponibles:
    1. **Open-Meteo** 🌐 - Datos globales (siempre disponible)
    2. **SIATA** 🏙️ - Específico de Medellín
    3. **OpenWeatherMap** ☁️ - Requiere API key
    4. **MeteoBlue** 🎯 - Requiere API key
    5. **Radar IDEAM** 📡 - Datos limitados
    
    #### Próximos pasos:
    - [ ] Pronóstico a 7 días
    - [ ] Historial de 30 días
    - [ ] Alertas meteorológicas
    - [ ] Exportación de datos
    - [ ] Más ubicaciones
    
    #### Contacto y Soporte:
    - 📖 [Documentación](../README.md)
    - 🐛 [Reportar problemas](https://github.com/lrdlk/ClimAPI/issues)
    """)
    
    st.divider()
    
    # Estado del sistema
    st.subheader("📊 Estado del Sistema")
    
    cache = st.session_state.cache_manager
    cache_stats = cache.get_stats()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Items en caché", cache_stats["size"])
    with col2:
        st.metric("Capacidad máxima", cache_stats["max_size"])
    with col3:
        st.metric("Utilización", cache_stats["utilization"])
    
    st.markdown("---")
    
    # Datos agregados
    st.subheader("📋 Datos JSON")
    
    aggregator = st.session_state.aggregator
    sources_status = aggregator.get_sources_status()
    
    st.json(sources_status)


if __name__ == "__main__":
    main()

