"""
CLIMAPI Dashboard - Streamlit
==============================

Dashboard interactivo para visualizar y consultar datos climáticos
de múltiples fuentes de APIs.

Ejecutar con: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json
from datetime import datetime, timedelta
import requests
from main import ClimAPIManager
import sys
import os

# Configuración de la página
st.set_page_config(
    page_title="CLIMAPI Dashboard",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .api-status-ok {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 4px;
    }
    .api-status-error {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 4px;
    }
    .api-status-warning {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 4px;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)


class APIDashboard:
    """Clase para gestionar el dashboard de APIs"""
    
    def __init__(self):
        self.data_dir = Path("data")
        self.manager = None
        
    def verificar_api_meteoblue(self, api_key, shared_secret):
        """Verifica el estado de la API de Meteoblue"""
        if not api_key or not shared_secret:
            return False, "Credenciales no configuradas"
        
        try:
            # Test endpoint básico
            url = "https://my.meteoblue.com/packages/basic-day"
            params = {
                "lat": 6.245,
                "lon": -75.5715,
                "asl": 1495,
                "format": "json",
                "METEOBLUE_API_KEY": api_key
                ,"SHARED_SECRET": shared_secret
            }
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return True, "Conexión exitosa"
            elif response.status_code == 401:
                return False, "Credenciales inválidas (401)"
            elif response.status_code == 429:
                return False, "Límite de llamadas excedido (429)"
            else:
                return False, f"Error HTTP {response.status_code}"
        except requests.exceptions.Timeout:
            return False, "Timeout de conexión"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def verificar_api_openmeteo(self):
        """Verifica el estado de la API de Open-Meteo"""
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": 6.245,
                "longitude": -75.5715,
                "current": "temperature_2m"
            }
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return True, "Conexión exitosa"
            else:
                return False, f"Error HTTP {response.status_code}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def verificar_api_openweather(self, api_key):
        """Verifica el estado de la API de OpenWeatherMap"""
        if not api_key:
            return False, "API key no configurada"
        
        try:
            url = "https://api.openweathermap.org/data/2.5/weather"
            params = {
                "lat": 6.245,
                "lon": -75.5715,
                "appid": api_key,
                "units": "metric"
            }
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return True, "Conexión exitosa"
            elif response.status_code == 401:
                return False, "API key inválida (401)"
            elif response.status_code == 429:
                return False, "Límite de llamadas excedido (429)"
            else:
                return False, f"Error HTTP {response.status_code}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def verificar_api_meteosource(self, api_key):
        """Verifica el estado de la API de Meteosource"""
        if not api_key:
            return False, "API key no configurada"
        
        try:
            url = "https://www.meteosource.com/api/v1/free/point"
            params = {
                "lat": 6.245,
                "lon": -75.5715,
                "sections": "current",
                "key": api_key
            }
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return True, "Conexión exitosa"
            elif response.status_code == 401:
                return False, "API key inválida (401)"
            elif response.status_code == 429:
                return False, "Límite de llamadas excedido (429)"
            else:
                return False, f"Error HTTP {response.status_code}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def verificar_api_ideam(self):
        """Verifica el estado de los datos de IDEAM en AWS"""
        try:
            import boto3
            from botocore.config import Config
            from botocore import UNSIGNED
            
            s3_client = boto3.client(
                's3',
                config=Config(signature_version=UNSIGNED),
                region_name='us-east-1'
            )
            
            # Intentar listar objetos del bucket
            response = s3_client.list_objects_v2(
                Bucket='s3-radaresideam',
                MaxKeys=1
            )
            
            if 'Contents' in response:
                return True, "Conexión exitosa a AWS S3"
            else:
                return False, "Bucket vacío o sin acceso"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def verificar_api_siata(self):
        """Verifica el estado del servidor SIATA"""
        try:
            url = "https://www.siata.gov.co/operacional/Meteorologia/"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return True, "Conexión exitosa"
            else:
                return False, f"Error HTTP {response.status_code}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def cargar_consultas_existentes(self):
        """Carga las consultas realizadas previamente"""
        consultas = []
        
        # Buscar archivos de consultas completas
        for file in self.data_dir.glob("consulta_completa_*.json"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['_file'] = file.name
                    data['_timestamp'] = datetime.fromtimestamp(file.stat().st_mtime)
                    consultas.append(data)
            except Exception as e:
                st.warning(f"Error cargando {file.name}: {e}")
        
        return sorted(consultas, key=lambda x: x['_timestamp'], reverse=True)
    
    def cargar_datos_meteoblue(self):
        """Carga datos de Meteoblue"""
        datos = []
        meteoblue_dir = self.data_dir / "data_meteoblue"
        
        if meteoblue_dir.exists():
            for file in meteoblue_dir.glob("forecast_*.json"):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        data['_file'] = file.name
                        data['_timestamp'] = datetime.fromtimestamp(file.stat().st_mtime)
                        datos.append(data)
                except Exception:
                    pass
        
        return sorted(datos, key=lambda x: x['_timestamp'], reverse=True)
    
    def cargar_datos_openmeteo(self):
        """Carga datos de Open-Meteo"""
        datos = []
        openmeteo_dir = self.data_dir / "data_openmeteo"
        
        if openmeteo_dir.exists():
            for file in openmeteo_dir.glob("*_metadata.json"):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        data['_file'] = file.name
                        data['_timestamp'] = datetime.fromtimestamp(file.stat().st_mtime)
                        
                        # Buscar archivos CSV asociados
                        base_name = file.stem.replace('_metadata', '')
                        hourly_file = file.parent / f"{base_name}_hourly.csv"
                        daily_file = file.parent / f"{base_name}_daily.csv"
                        
                        if hourly_file.exists():
                            data['_hourly_data'] = pd.read_csv(hourly_file)
                        if daily_file.exists():
                            data['_daily_data'] = pd.read_csv(daily_file)
                        
                        datos.append(data)
                except Exception:
                    pass
        
        return sorted(datos, key=lambda x: x['_timestamp'], reverse=True)
    
    def cargar_datos_openweather(self):
        """Carga datos de OpenWeatherMap"""
        datos = []
        openweather_dir = self.data_dir / "data_openweathermap"
        
        if openweather_dir.exists():
            for file in openweather_dir.glob("*.json"):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        data['_file'] = file.name
                        data['_timestamp'] = datetime.fromtimestamp(file.stat().st_mtime)
                        datos.append(data)
                except Exception:
                    pass
        
        return sorted(datos, key=lambda x: x['_timestamp'], reverse=True)
    
    def cargar_datos_meteosource(self):
        """Carga datos de Meteosource"""
        datos = []
        meteosource_dir = self.data_dir / "data_meteosource"
        
        if meteosource_dir.exists():
            for file in meteosource_dir.glob("*.json"):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        data['_file'] = file.name
                        data['_timestamp'] = datetime.fromtimestamp(file.stat().st_mtime)
                        datos.append(data)
                except Exception:
                    pass
        
        return sorted(datos, key=lambda x: x['_timestamp'], reverse=True)


def pagina_inicio():
    """Página principal del dashboard"""
    st.markdown('<div class="main-header">🌦️ CLIMAPI Dashboard</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Sistema Integrado de Consulta de Datos Climáticos
    
    Bienvenido al dashboard de CLIMAPI. Aquí puedes:
    - 📊 **Visualizar** consultas realizadas previamente
    - 🔍 **Realizar** nuevas consultas a múltiples APIs climáticas
    - ✅ **Verificar** el estado de las APIs en tiempo real
    - 📈 **Analizar** datos históricos y pronósticos
    """)
    
    # Estadísticas rápidas
    col1, col2, col3, col4 = st.columns(4)
    
    dashboard = APIDashboard()
    
    with col1:
        consultas = dashboard.cargar_consultas_existentes()
        st.metric("Consultas Completas", len(consultas))
    
    with col2:
        datos_mb = dashboard.cargar_datos_meteoblue()
        st.metric("Datos Meteoblue", len(datos_mb))
    
    with col3:
        datos_om = dashboard.cargar_datos_openmeteo()
        st.metric("Datos Open-Meteo", len(datos_om))
    
    with col4:
        datos_ow = dashboard.cargar_datos_openweather()
        st.metric("Datos OpenWeather", len(datos_ow))
    
    # Gráfico de consultas por fecha
    st.subheader("📅 Actividad Reciente")
    
    if consultas:
        df_actividad = pd.DataFrame([
            {
                'Fecha': c['_timestamp'].date(),
                'Hora': c['_timestamp'].time(),
                'Ubicación': c['location']
            }
            for c in consultas
        ])
        
        fig = px.histogram(
            df_actividad,
            x='Fecha',
            title='Consultas por Fecha',
            labels={'Fecha': 'Fecha', 'count': 'Número de Consultas'}
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay consultas registradas aún. ¡Realiza tu primera consulta!")


def pagina_verificacion_apis():
    """Página de verificación de APIs"""
    st.title("✅ Verificación de APIs")
    st.markdown("Verifica el estado y conectividad de todas las APIs climáticas")
    
    dashboard = APIDashboard()
    
    # Cargar variables de entorno
    from dotenv import load_dotenv
    load_dotenv()
    
    meteoblue_key = os.getenv("METEOBLUE_API_KEY", "")
    meteoblue_secret = os.getenv("METEOBLUE_SHARED_SECRET", "")
    openweather_key = os.getenv("OPENWEATHER_API_KEY", "")
    meteosource_key = os.getenv("METEOSOURCE_API_KEY", "")
    
    if st.button("🔄 Verificar Todas las APIs", type="primary"):
        with st.spinner("Verificando APIs..."):
            # Meteoblue
            st.subheader("1️⃣ Meteoblue")
            status, message = dashboard.verificar_api_meteoblue(meteoblue_key, meteoblue_secret)
            if status:
                st.markdown(f'<div class="api-status-ok">✅ {message}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="api-status-error">❌ {message}</div>', unsafe_allow_html=True)
            
            # Open-Meteo
            st.subheader("2️⃣ Open-Meteo")
            status, message = dashboard.verificar_api_openmeteo()
            if status:
                st.markdown(f'<div class="api-status-ok">✅ {message}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="api-status-error">❌ {message}</div>', unsafe_allow_html=True)
            
            # OpenWeatherMap
            st.subheader("3️⃣ OpenWeatherMap")
            status, message = dashboard.verificar_api_openweather(openweather_key)
            if status:
                st.markdown(f'<div class="api-status-ok">✅ {message}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="api-status-error">❌ {message}</div>', unsafe_allow_html=True)
            
            # Meteosource
            st.subheader("4️⃣ Meteosource")
            status, message = dashboard.verificar_api_meteosource(meteosource_key)
            if status:
                st.markdown(f'<div class="api-status-ok">✅ {message}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="api-status-error">❌ {message}</div>', unsafe_allow_html=True)
            
            # IDEAM
            st.subheader("5️⃣ IDEAM Radar (AWS)")
            status, message = dashboard.verificar_api_ideam()
            if status:
                st.markdown(f'<div class="api-status-ok">✅ {message}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="api-status-error">❌ {message}</div>', unsafe_allow_html=True)
            
            # SIATA
            st.subheader("6️⃣ SIATA")
            status, message = dashboard.verificar_api_siata()
            if status:
                st.markdown(f'<div class="api-status-ok">✅ {message}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="api-status-warning">⚠️ {message}</div>', unsafe_allow_html=True)
    
    # Información de configuración
    st.markdown("---")
    st.subheader("⚙️ Configuración")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**APIs Configuradas:**")
        st.write(f"- Meteoblue: {'✅' if meteoblue_key else '❌'}")
        st.write(f"- OpenWeatherMap: {'✅' if openweather_key else '❌'}")
        st.write(f"- Meteosource: {'✅' if meteosource_key else '❌'}")
    
    with col2:
        st.markdown("**APIs Públicas:**")
        st.write("- Open-Meteo: ✅ (Sin API key)")
        st.write("- IDEAM: ✅ (AWS público)")
        st.write("- SIATA: ✅ (Datos públicos)")


def pagina_consultas_existentes():
    """Página para ver consultas existentes"""
    st.title("📊 Consultas Realizadas")
    
    dashboard = APIDashboard()
    consultas = dashboard.cargar_consultas_existentes()
    
    if not consultas:
        st.info("No hay consultas registradas. Ve a 'Nueva Consulta' para realizar una.")
        return
    
    st.write(f"Total de consultas: **{len(consultas)}**")
    
    # Selector de consulta
    opciones = [
        f"{c['location']} - {c['_timestamp'].strftime('%Y-%m-%d %H:%M')}"
        for c in consultas
    ]
    
    seleccion = st.selectbox("Selecciona una consulta:", opciones)
    idx = opciones.index(seleccion)
    consulta = consultas[idx]
    
    # Información general
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Ubicación", consulta['location'])
    with col2:
        coords = consulta['coordinates']
        st.metric("Coordenadas", f"{coords['lat']:.4f}, {coords['lon']:.4f}")
    with col3:
        st.metric("Altitud", f"{coords.get('asl', 0)} m")
    
    # Tabs para cada fuente de datos
    tabs = st.tabs(["📋 Resumen", "☁️ Meteoblue", "🌐 Open-Meteo", "🌤️ OpenWeather", "🌦️ Meteosource"])
    
    with tabs[0]:
        st.subheader("Resumen de la Consulta")
        st.json({
            "Ubicación": consulta['location'],
            "Coordenadas": consulta['coordinates'],
            "Timestamp": consulta['timestamp'],
            "Archivo": consulta['_file']
        })
    
    with tabs[1]:
        st.subheader("Datos de Meteoblue")
        if consulta.get('meteoblue'):
            mb_data = consulta['meteoblue']
            if isinstance(mb_data, dict) and 'data_day' in mb_data:
                data_day = mb_data['data_day']
                
                # Crear DataFrame para visualización
                if 'time' in data_day:
                    df_mb = pd.DataFrame({
                        'Fecha': data_day.get('time', []),
                        'Temp Max (°C)': data_day.get('temperature_max', []),
                        'Temp Min (°C)': data_day.get('temperature_min', []),
                        'Precipitación (mm)': data_day.get('precipitation', [])
                    })
                    
                    st.dataframe(df_mb, use_container_width=True)
                    
                    # Gráfico de temperatura
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df_mb['Fecha'],
                        y=df_mb['Temp Max (°C)'],
                        name='Temp Máxima',
                        line=dict(color='red')
                    ))
                    fig.add_trace(go.Scatter(
                        x=df_mb['Fecha'],
                        y=df_mb['Temp Min (°C)'],
                        name='Temp Mínima',
                        line=dict(color='blue')
                    ))
                    fig.update_layout(title='Pronóstico de Temperatura')
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Datos de Meteoblue no disponibles")
        else:
            st.info("No hay datos de Meteoblue en esta consulta")
    
    with tabs[2]:
        st.subheader("Datos de Open-Meteo")
        if consulta.get('openmeteo'):
            st.info("Datos guardados en archivos CSV. Usa la sección 'Datos por API' para visualizar.")
        else:
            st.info("No hay datos de Open-Meteo en esta consulta")
    
    with tabs[3]:
        st.subheader("Datos de OpenWeatherMap")
        if consulta.get('openweather'):
            ow_data = consulta['openweather']
            
            if ow_data.get('current'):
                st.markdown("**Clima Actual:**")
                current = ow_data['current']
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Temperatura", f"{current['temperature']['current']:.1f}°C")
                with col2:
                    st.metric("Humedad", f"{current['humidity']}%")
                with col3:
                    st.metric("Viento", f"{current['wind']['speed']} m/s")
                with col4:
                    st.metric("Presión", f"{current['pressure']} hPa")
                
                st.write(f"**Descripción:** {current['weather']['description']}")
            
            if ow_data.get('air_quality'):
                st.markdown("**Calidad del Aire:**")
                aq = ow_data['air_quality']
                st.metric("AQI", f"{aq['aqi']['value']} - {aq['aqi']['label']}")
        else:
            st.info("No hay datos de OpenWeatherMap en esta consulta")
    
    with tabs[4]:
        st.subheader("Datos de Meteosource")
        if consulta.get('meteosource'):
            st.info("Datos de Meteosource disponibles. Implementa visualización según tu estructura.")
        else:
            st.info("No hay datos de Meteosource en esta consulta")


def pagina_nueva_consulta():
    """Página para realizar nuevas consultas"""
    st.title("🔍 Nueva Consulta")
    
    st.markdown("""
    Realiza una nueva consulta a las APIs climáticas. Los datos se guardarán automáticamente
    en el directorio `data/` para futuras visualizaciones.
    """)
    
    # Formulario de consulta
    with st.form("consulta_form"):
        st.subheader("📍 Ubicación")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Ubicaciones predefinidas
            ubicaciones = {
                "Medellin": {"lat": 6.245, "lon": -75.5715, "asl": 1495},
                "Bogota": {"lat": 4.711, "lon": -74.0721, "asl": 2640},
                "Cartagena": {"lat": 10.391, "lon": -75.4794, "asl": 2},
                "Cali": {"lat": 3.4516, "lon": -76.532, "asl": 995},
                "Barranquilla": {"lat": 10.9639, "lon": -74.7964, "asl": 18},
                "Personalizado": None
            }
            
            ubicacion_seleccionada = st.selectbox(
                "Selecciona una ubicación:",
                list(ubicaciones.keys())
            )
        
        with col2:
            tipo_consulta = st.selectbox(
                "Tipo de consulta:",
                ["Completa (todas las APIs)", "Meteoblue", "Open-Meteo", "OpenWeather", "Meteosource"]
            )
        
        # Si es personalizado, mostrar campos
        if ubicacion_seleccionada == "Personalizado":
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                nombre = st.text_input("Nombre:", value="Mi Ubicación")
            with col2:
                lat = st.number_input("Latitud:", value=6.245, format="%.4f")
            with col3:
                lon = st.number_input("Longitud:", value=-75.5715, format="%.4f")
            with col4:
                asl = st.number_input("Altitud (m):", value=1495)
        else:
            if ubicaciones[ubicacion_seleccionada]:
                nombre = ubicacion_seleccionada
                lat = ubicaciones[ubicacion_seleccionada]["lat"]
                lon = ubicaciones[ubicacion_seleccionada]["lon"]
                asl = ubicaciones[ubicacion_seleccionada]["asl"]
                
                st.info(f"📍 {nombre}: {lat}°N, {lon}°W, {asl}m")
        
        # Botón de envío
        submitted = st.form_submit_button("🚀 Realizar Consulta", type="primary")
        
        if submitted:
            with st.spinner("Consultando APIs..."):
                try:
                    manager = ClimAPIManager()
                    
                    if tipo_consulta == "Completa (todas las APIs)":
                        resultado = manager.consulta_completa(lat, lon, nombre, asl)
                        st.success("✅ Consulta completa realizada exitosamente!")
                        
                    elif tipo_consulta == "Meteoblue":
                        resultado = manager.consultar_meteoblue(lat, lon, nombre, asl)
                        st.success("✅ Consulta a Meteoblue exitosa!")
                        
                    elif tipo_consulta == "Open-Meteo":
                        resultado = manager.consultar_openmeteo(lat, lon, nombre)
                        st.success("✅ Consulta a Open-Meteo exitosa!")
                        
                    elif tipo_consulta == "OpenWeather":
                        resultado = manager.consultar_openweather(lat, lon, nombre)
                        st.success("✅ Consulta a OpenWeather exitosa!")
                        
                    elif tipo_consulta == "Meteosource":
                        resultado = manager.consultar_meteosource(lat, lon, nombre)
                        st.success("✅ Consulta a Meteosource exitosa!")
                    
                    st.balloons()
                    st.info("Los datos se han guardado en el directorio `data/`. Revísalos en la sección 'Consultas Realizadas'.")
                    
                except Exception as e:
                    st.error(f"❌ Error al realizar la consulta: {str(e)}")
                    st.exception(e)


def pagina_datos_por_api():
    """Página para ver datos separados por API"""
    st.title("📁 Datos por API")
    
    dashboard = APIDashboard()
    
    api_seleccionada = st.selectbox(
        "Selecciona una API:",
        ["Meteoblue", "Open-Meteo", "OpenWeatherMap", "Meteosource"]
    )
    
    if api_seleccionada == "Meteoblue":
        datos = dashboard.cargar_datos_meteoblue()
        st.subheader(f"☁️ Datos de Meteoblue ({len(datos)} archivos)")
        
        if datos:
            for dato in datos[:10]:  # Mostrar primeros 10
                with st.expander(f"{dato['_file']} - {dato['_timestamp'].strftime('%Y-%m-%d %H:%M')}"):
                    st.json(dato)
        else:
            st.info("No hay datos de Meteoblue disponibles")
    
    elif api_seleccionada == "Open-Meteo":
        datos = dashboard.cargar_datos_openmeteo()
        st.subheader(f"🌐 Datos de Open-Meteo ({len(datos)} archivos)")
        
        if datos:
            for dato in datos[:10]:
                with st.expander(f"{dato['location']} - {dato['_timestamp'].strftime('%Y-%m-%d %H:%M')}"):
                    if '_daily_data' in dato:
                        st.subheader("Datos Diarios")
                        st.dataframe(dato['_daily_data'])
                    
                    if '_hourly_data' in dato:
                        st.subheader("Datos Horarios (primeras 24 horas)")
                        st.dataframe(dato['_hourly_data'].head(24))
        else:
            st.info("No hay datos de Open-Meteo disponibles")
    
    elif api_seleccionada == "OpenWeatherMap":
        datos = dashboard.cargar_datos_openweather()
        st.subheader(f"🌤️ Datos de OpenWeatherMap ({len(datos)} archivos)")
        
        if datos:
            for dato in datos[:10]:
                with st.expander(f"{dato['_file']} - {dato['_timestamp'].strftime('%Y-%m-%d %H:%M')}"):
                    st.json(dato)
        else:
            st.info("No hay datos de OpenWeatherMap disponibles")
    
    elif api_seleccionada == "Meteosource":
        datos = dashboard.cargar_datos_meteosource()
        st.subheader(f"🌦️ Datos de Meteosource ({len(datos)} archivos)")
        
        if datos:
            for dato in datos[:10]:
                with st.expander(f"{dato['_file']} - {dato['_timestamp'].strftime('%Y-%m-%d %H:%M')}"):
                    st.json(dato)
        else:
            st.info("No hay datos de Meteosource disponibles")


def pagina_roadmap():
    """Página de roadmap del proyecto"""
    st.title("🗺️ Roadmap del Proyecto CLIMAPI")
    
    # Leer roadmap
    roadmap_path = Path("ROADMAP.md")
    
    if not roadmap_path.exists():
        st.error("❌ Archivo ROADMAP.md no encontrado")
        return
    
    with open(roadmap_path, 'r', encoding='utf-8') as f:
        roadmap_content = f.read()
    
    # Estado general
    st.header("📊 Estado General")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Progreso Total", "30%", delta="En desarrollo")
    
    with col2:
        st.metric("Etapas Completadas", "2/8")
    
    with col3:
        st.metric("Tareas Completadas", "6/16")
    
    with col4:
        st.metric("Tiempo Estimado", "8-14 semanas")
    
    st.markdown("---")
    
    # Progreso por etapa
    st.header("🎯 Progreso por Etapa")
    
    etapas = [
        {"nombre": "1. Recolección de datos", "progreso": 85, "estado": "🟢 Avanzado"},
        {"nombre": "2. Procesamiento y limpieza", "progreso": 40, "estado": "🟡 En desarrollo"},
        {"nombre": "3. Análisis exploratorio", "progreso": 5, "estado": "🟡 Inicial"},
        {"nombre": "4. Entrenamiento de modelos", "progreso": 0, "estado": "⚪ Pendiente"},
        {"nombre": "5. Integración MLflow", "progreso": 0, "estado": "⚪ Pendiente"},
        {"nombre": "6. API FastAPI", "progreso": 0, "estado": "⚪ Pendiente"},
        {"nombre": "7. Dashboard Streamlit", "progreso": 80, "estado": "🟢 Avanzado"},
        {"nombre": "8. Despliegue y pruebas", "progreso": 0, "estado": "⚪ Pendiente"}
    ]
    
    for etapa in etapas:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.write(f"**{etapa['nombre']}**")
            st.progress(etapa['progreso'] / 100)
        
        with col2:
            st.write(etapa['estado'])
            st.write(f"{etapa['progreso']}%")
    
    st.markdown("---")
    
    # Checklist
    st.header("✅ Checklist General")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✅ Completado")
        st.markdown("""
        - ✅ Configurar cuentas y claves de APIs climáticas
        - ✅ Desarrollar scripts de extracción
        - ✅ Implementar clientes para 6 APIs
        - ✅ Sistema de logs automático
        - ✅ Dashboard de visualización
        - ✅ Unificar datasets en DataFrame normalizado (tipos y timestamps)
        - ✅ Correlaciones iniciales (temperatura vs humedad)
        """)
    
    with col2:
        st.subheader("⏳ Pendiente")
        st.markdown("""
        - ⏳ Finalizar normalizador (`data_normalizer.py`)
        - ⏳ Esquemas JSON comunes y validaciones
        - ⏳ Manejo de nulos/outliers y estandarización de unidades
        - ⏳ Persistencia en base de datos (PostgreSQL/MongoDB)
        - ⏳ EDA avanzado (estacionalidad, outliers)
        - ⏳ Entrenamiento de modelos y métricas
        - ⏳ Integración MLflow
        - ⏳ API con FastAPI
        - ⏳ Despliegue Docker
        """)
    
    st.markdown("---")
    
    # Próximos pasos
    st.header("🚀 Próximos Pasos Inmediatos")
    
    st.info("""
    **Prioridad ALTA:**
    1. Finalizar `data_normalizer.py` consolidando la lógica actual del notebook
    2. Crear y validar esquemas JSON comunes contra el DataFrame unificado
    3. Persistir el DataFrame consolidado en PostgreSQL/MongoDB
    
    **Prioridad MEDIA:**
    1. Extender EDA a estacionalidad y detección de outliers
    2. Documentar decisiones de limpieza y normalización
    3. Preparar pipeline ETL y baseline de métricas
    """)
    
    st.markdown("---")
    
    # Scripts de visualización
    st.header("📊 Scripts de Visualización Disponibles")
    
    scripts = [
        {"api": "Meteoblue", "script": "meteoblue_visualizer.py", "icon": "☁️"},
        {"api": "Open-Meteo", "script": "open_meteo_visualizer.py", "icon": "🌐"},
        {"api": "OpenWeatherMap", "script": "openweather_visualizer.py", "icon": "🌤️"},
        {"api": "Meteosource", "script": "meteosource_visualizer.py", "icon": "🌦️"},
        {"api": "IDEAM Radar", "script": "ideam_visualizer.py", "icon": "📡"},
        {"api": "SIATA", "script": "siata_visualizer.py", "icon": "🌐"}
    ]
    
    st.write("Nuevos scripts de procesamiento y visualización en `src/visualizers/`:")
    
    cols = st.columns(3)
    
    for i, script in enumerate(scripts):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="
                background-color: #f0f2f6;
                border-left: 4px solid #1f77b4;
                padding: 1rem;
                margin: 0.5rem 0;
                border-radius: 4px;
            ">
                <h4>{script['icon']} {script['api']}</h4>
                <code>{script['script']}</code>
                <br><br>
                <small>pandas • numpy • matplotlib • sklearn</small>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Roadmap completo
    with st.expander("📄 Ver Roadmap Completo"):
        st.markdown(roadmap_content)
    
    # Enlaces útiles
    st.header("🔗 Enlaces Útiles")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("📋 [Roadmap Interactivo Phind](https://interactive.phind.com/streaming-preview/session_1765509468704/index.html)")
    
    with col2:
        st.markdown("📖 [Documentación README](README.md)")
    
    with col3:
        st.markdown("🔄 [Actualizar Roadmap](actualizar_roadmap.py)")


def main():
    """Función principal del dashboard"""
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/clouds/100/000000/cloud.png", width=100)
        st.title("CLIMAPI")
        st.markdown("---")
        
        pagina = st.radio(
            "Navegación:",
            [
                "🏠 Inicio",
                "✅ Verificación APIs",
                "📊 Consultas Realizadas",
                "🔍 Nueva Consulta",
                "📁 Datos por API",
                "🗺️ Roadmap"
            ]
        )
        
        st.markdown("---")
        st.markdown("### Información")
        st.info("""
        **CLIMAPI Dashboard v1.0.1**
        
        Sistema integrado para consulta
        y visualización de datos climáticos.
        
        Diciembre 2025
        """)
        
        # Mostrar APIs disponibles
        st.markdown("### APIs Integradas")
        st.markdown("""
        - ☁️ Meteoblue
        - 🌐 Open-Meteo
        - 🌤️ OpenWeatherMap
        - 🌦️ Meteosource
        - 📡 IDEAM Radar
        - 🌐 SIATA
        """)
    
    # Renderizar página seleccionada
    if pagina == "🏠 Inicio":
        pagina_inicio()
    elif pagina == "✅ Verificación APIs":
        pagina_verificacion_apis()
    elif pagina == "📊 Consultas Realizadas":
        pagina_consultas_existentes()
    elif pagina == "🔍 Nueva Consulta":
        pagina_nueva_consulta()
    elif pagina == "📁 Datos por API":
        pagina_datos_por_api()
    elif pagina == "🗺️ Roadmap":
        pagina_roadmap()


if __name__ == "__main__":
    main()
