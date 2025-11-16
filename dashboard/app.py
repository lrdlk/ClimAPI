"""
Dashboard interactivo para visualizar datos meteorológicos.

Este módulo crea un dashboard usando Streamlit para visualizar
temperatura, humedad, precipitación y velocidad del viento.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

# Agregar el directorio raíz al path para importar módulos
sys.path.append(str(Path(__file__).parent.parent))

from processing.storage import load_from_csv


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
    Función principal que configura y ejecuta el dashboard.
    """
    # Configuración de la página
    st.set_page_config(
        page_title="Dashboard Meteorológico",
        page_icon="🌤️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Título principal
    st.title("🌤️ Dashboard Meteorológico - Open-Meteo")
    st.markdown("---")
    
    # Sidebar para configuración
    st.sidebar.header("⚙️ Configuración")
    
    # Selector de archivo de datos
    data_file = st.sidebar.text_input(
        "📁 Archivo de datos",
        value="data/weather_data.csv",
        help="Ruta al archivo CSV con los datos meteorológicos"
    )
    
    # Cargar datos
    df = load_data(data_file)
    
    # Información general en el sidebar
    st.sidebar.markdown("### 📊 Información General")
    st.sidebar.metric("Total de registros", len(df))
    st.sidebar.metric(
        "Rango de fechas",
        f"{df.index.min().strftime('%Y-%m-%d')} a {df.index.max().strftime('%Y-%d-%m')}"
    )
    
    # Estadísticas básicas
    if 'temperatura_c' in df.columns:
        st.sidebar.metric("🌡️ Temp. Promedio", f"{df['temperatura_c'].mean():.1f} °C")
        st.sidebar.metric("🌡️ Temp. Máxima", f"{df['temperatura_c'].max():.1f} °C")
        st.sidebar.metric("🌡️ Temp. Mínima", f"{df['temperatura_c'].min():.1f} °C")
    
    # Selector de rango de fechas
    st.sidebar.markdown("### 📅 Filtro de Fechas")
    min_date = df.index.min().date()
    max_date = df.index.max().date()
    
    date_range = st.sidebar.date_input(
        "Selecciona el rango de fechas",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Validar que se seleccionaron dos fechas
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = min_date
        end_date = max_date
    
    # Convertir a datetime para el filtrado
    start_datetime = pd.Timestamp(start_date)
    end_datetime = pd.Timestamp(end_date) + pd.Timedelta(days=1)  # Incluir el día completo
    
    # Contenido principal
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
    
    # Botón para descargar datos filtrados
    csv = df_filtered.to_csv()
    st.download_button(
        label="📥 Descargar datos filtrados (CSV)",
        data=csv,
        file_name=f"weather_data_{start_date}_{end_date}.csv",
        mime="text/csv"
    )


if __name__ == "__main__":
    main()

