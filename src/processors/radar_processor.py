"""
Procesador y visualizador de datos de radares IDEAM
Procesa archivos descargados y genera visualizaciones
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
from datetime import datetime
import logging
import sys

logger = logging.getLogger(__name__)

# Información de radares (copiada para independencia del módulo)
RADARES_IDEAM = {
    'Guaviare': {
        'codigo': 'Guaviare',
        'prefijo': 'GUA',
        'ubicacion': 'San José del Guaviare',
        'lat': 2.5694,
        'lon': -72.6411,
        'descripcion': 'Radar meteorológico en San José del Guaviare',
        'distancia_medellin_km': 440
    },
    'Munchique': {
        'codigo': 'Munchique',
        'prefijo': 'MUN',
        'ubicacion': 'Popayán - Cauca',
        'lat': 2.5458,
        'lon': -76.9631,
        'descripcion': 'Radar meteorológico en Munchique',
        'distancia_medellin_km': 310
    },
    'Barrancabermeja': {
        'codigo': 'Barrancabermeja',
        'prefijo': 'BAR',
        'ubicacion': 'Barrancabermeja - Santander',
        'lat': 7.0653,
        'lon': -73.8547,
        'descripcion': 'Radar meteorológico en Barrancabermeja (más cercano a Medellín)',
        'distancia_medellin_km': 230
    },
    'Carimagua': {
        'codigo': 'Carimagua',
        'prefijo': 'CAR',
        'ubicacion': 'Puerto Gaitán - Meta',
        'lat': 4.5694,
        'lon': -71.3292,
        'descripcion': 'Radar meteorológico en Carimagua',
        'distancia_medellin_km': 270
    }
}


class RadarDataProcessor:
    """Procesa y visualiza datos de radar IDEAM"""
    
    def __init__(self, data_dir="data/Radar_IDEAM"):
        self.data_dir = Path(data_dir)
        self.productos_radar = {
            'CAPPI': 'Constant Altitude Plan Position Indicator',
            'MAX': 'Reflectividad Máxima',
            'PCAPPI': 'Pseudo-CAPPI',
            'RAIN': 'Acumulado de Precipitación',
            'VIL': 'Vertically Integrated Liquid'
        }
    
    def leer_inventario(self):
        """Lee el inventario de archivos disponibles"""
        inventario_path = self.data_dir / 'inventario_radares.csv'
        
        if not inventario_path.exists():
            logger.warning("No se encuentra inventario. Ejecute primero el descargador.")
            return None
        
        return pd.read_csv(inventario_path)
    
    def analizar_disponibilidad(self, radar='Barrancabermeja'):
        """Analiza la disponibilidad de datos por fecha"""
        inventario = self.leer_inventario()
        
        if inventario is None or inventario.empty:
            print("⚠️  No hay datos disponibles")
            return None
        
        # Filtrar por radar
        datos_radar = inventario[inventario['radar'] == radar].copy()
        
        if datos_radar.empty:
            print(f"⚠️  No hay datos para el radar {radar}")
            print(f"Radares disponibles: {inventario['radar'].unique().tolist()}")
            return None
        
        # Convertir fechas
        datos_radar['fecha'] = pd.to_datetime(datos_radar['fecha_directorio'])
        
        # Resumen
        resumen = datos_radar.groupby('fecha').agg({
            'archivo': 'count',
            'tamaño_mb': 'sum'
        }).reset_index()
        
        resumen.columns = ['fecha', 'num_archivos', 'tamaño_total_mb']
        
        return resumen
    
    def visualizar_disponibilidad(self, radar='Barrancabermeja'):
        """Crea visualización de disponibilidad de datos"""
        resumen = self.analizar_disponibilidad(radar)
        
        if resumen is None:
            return None
        
        # Crear figura con subplots
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=resumen['fecha'],
            y=resumen['num_archivos'],
            name='Número de archivos',
            marker_color='rgb(55, 83, 109)',
            hovertemplate='<b>Fecha:</b> %{x|%Y-%m-%d}<br>' +
                         '<b>Archivos:</b> %{y}<br>' +
                         '<extra></extra>'
        ))
        
        fig.update_layout(
            title=f'Disponibilidad de Datos - Radar {radar}',
            xaxis_title='Fecha',
            yaxis_title='Número de Archivos',
            hovermode='x unified',
            template='plotly_white',
            height=500
        )
        
        return fig
    
    def crear_mapa_cobertura(self):
        """Crea mapa de cobertura de radares"""
        # Preparar datos para el mapa
        radar_data = []
        for codigo, info in RADARES_IDEAM.items():
            radar_data.append({
                'Radar': codigo,
                'Ubicación': info['ubicacion'],
                'Latitud': info['lat'],
                'Longitud': info['lon'],
                'Descripción': info['descripcion'],
                'Distancia_Medellin': info['distancia_medellin_km']
            })
        
        df_radares = pd.DataFrame(radar_data)
        
        # Crear mapa con Plotly
        fig = go.Figure()
        
        # Agregar radares
        fig.add_trace(go.Scattergeo(
            lon=df_radares['Longitud'],
            lat=df_radares['Latitud'],
            text=df_radares.apply(
                lambda x: f"<b>{x['Radar']}</b><br>{x['Ubicación']}<br>~{x['Distancia_Medellin']} km a Medellín", 
                axis=1
            ),
            mode='markers+text',
            marker=dict(
                size=15,
                color=df_radares['Distancia_Medellin'],
                colorscale='RdYlGn_r',
                showscale=True,
                colorbar=dict(title="Distancia<br>a Medellín<br>(km)"),
                symbol='circle',
                line=dict(width=2, color='white')
            ),
            textposition='top center',
            textfont=dict(size=10, color='black'),
            name='Radares IDEAM',
            hovertemplate='%{text}<extra></extra>'
        ))
        
        # Destacar Medellín
        fig.add_trace(go.Scattergeo(
            lon=[-75.5636],
            lat=[6.2442],
            text=['<b>Medellín</b>'],
            mode='markers+text',
            marker=dict(
                size=20,
                color='blue',
                symbol='star',
                line=dict(width=2, color='white')
            ),
            textposition='bottom center',
            textfont=dict(size=12, color='blue'),
            name='Medellín',
            hovertemplate='<b>Medellín</b><br>Capital de Antioquia<extra></extra>'
        ))
        
        # Configurar vista del mapa
        fig.update_geos(
            center=dict(lon=-74, lat=4),
            projection_scale=4.5,
            showcountries=True,
            showcoastlines=True,
            showland=True,
            landcolor='rgb(243, 243, 243)',
            coastlinecolor='rgb(204, 204, 204)',
            countrycolor='rgb(204, 204, 204)'
        )
        
        fig.update_layout(
            title={
                'text': 'Red de Radares Meteorológicos IDEAM - Colombia<br>' +
                        '<sub>Disponibles en AWS Open Data</sub>',
                'x': 0.5,
                'xanchor': 'center'
            },
            height=700,
            showlegend=True,
            geo=dict(
                scope='south america',
                center=dict(lon=-74, lat=4)
            )
        )
        
        return fig
    
    def resumen_estadistico(self, radar='Barrancabermeja'):
        """Genera resumen estadístico de los datos"""
        inventario = self.leer_inventario()
        
        if inventario is None:
            return None
        
        datos_radar = inventario[inventario['radar'] == radar]
        
        print("\n" + "="*80)
        print(f"RESUMEN ESTADÍSTICO - RADAR {radar}")
        print("="*80)
        
        if datos_radar.empty:
            print("⚠️  No hay datos disponibles para este radar")
            print(f"Radares con datos: {inventario['radar'].unique().tolist()}")
            return None
        
        print(f"\n📊 Estadísticas Generales:")
        print(f"   Total de archivos: {len(datos_radar)}")
        print(f"   Espacio total: {datos_radar['tamaño_mb'].sum():.2f} MB")
        print(f"   Tamaño promedio: {datos_radar['tamaño_mb'].mean():.2f} MB")
        print(f"   Tamaño máximo: {datos_radar['tamaño_mb'].max():.2f} MB")
        print(f"   Tamaño mínimo: {datos_radar['tamaño_mb'].min():.2f} MB")
        
        # Fechas disponibles
        fechas_unicas = datos_radar['fecha_directorio'].unique()
        print(f"\n📅 Cobertura Temporal:")
        print(f"   Fechas disponibles: {len(fechas_unicas)}")
        print(f"   Primera fecha: {min(fechas_unicas)}")
        print(f"   Última fecha: {max(fechas_unicas)}")
        
        # Archivos por fecha
        archivos_por_fecha = datos_radar.groupby('fecha_directorio').size()
        print(f"\n📁 Archivos por Fecha:")
        print(f"   Promedio: {archivos_por_fecha.mean():.1f}")
        print(f"   Máximo: {archivos_por_fecha.max()}")
        print(f"   Mínimo: {archivos_por_fecha.min()}")
        
        # Información del radar
        if 'distancia_medellin_km' in datos_radar.columns:
            dist = datos_radar['distancia_medellin_km'].iloc[0]
            print(f"\n📍 Ubicación:")
            print(f"   Distancia a Medellín: ~{dist} km")
        
        return datos_radar
    
    def listar_radares_con_datos(self):
        """Lista los radares que tienen datos descargados"""
        inventario = self.leer_inventario()
        
        if inventario is None or inventario.empty:
            print("⚠️  No hay datos descargados")
            return []
        
        radares = inventario['radar'].unique().tolist()
        return radares


class EnhancedClimateDashboard:
    """Dashboard climático mejorado con datos de radar"""
    
    def __init__(self):
        self.processor = RadarDataProcessor()
    
    def create_complete_dashboard(self):
        """Crea dashboard completo con todas las visualizaciones"""
        print("\n🌤️📡 GENERANDO DASHBOARD COMPLETO 📡🌤️")
        print("="*80)
        
        output_path = Path("visualizaciones")
        output_path.mkdir(exist_ok=True)
        
        # 1. Mapa de cobertura de radares (siempre disponible)
        print("\n1️⃣ Generando mapa de cobertura de radares...")
        try:
            fig_mapa = self.processor.crear_mapa_cobertura()
            if fig_mapa:
                fig_mapa.write_html(output_path / "mapa_radares_ideam.html")
                print(f"   ✅ Guardado en: visualizaciones/mapa_radares_ideam.html")
        except Exception as e:
            print(f"   ❌ Error generando mapa: {e}")
        
        # 2. Verificar si hay datos descargados
        radares_disponibles = self.processor.listar_radares_con_datos()
        
        if not radares_disponibles:
            print("\n⚠️  No hay datos descargados todavía.")
            print("💡 Ejecute primero el descargador de radares:")
            print("   python ideam_radar_downloader.py")
            print("\n" + "="*80)
            return
        
        print(f"\n✅ Radares con datos: {', '.join(radares_disponibles)}")
        
        # Usar el primer radar disponible
        radar_principal = radares_disponibles[0]
        
        # 3. Resumen estadístico
        print(f"\n2️⃣ Generando resumen estadístico del Radar {radar_principal}...")
        self.processor.resumen_estadistico(radar_principal)
        
        # 4. Disponibilidad de datos
        print(f"\n3️⃣ Analizando disponibilidad de datos...")
        try:
            fig_disponibilidad = self.processor.visualizar_disponibilidad(radar_principal)
            if fig_disponibilidad:
                fig_disponibilidad.write_html(
                    output_path / f"disponibilidad_{radar_principal.lower()}.html"
                )
                print(f"   ✅ Guardado en: visualizaciones/disponibilidad_{radar_principal.lower()}.html")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # 5. Comparación de radares
        print("\n4️⃣ Generando comparación entre radares...")
        try:
            self.comparar_radares()
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print("\n" + "="*80)
        print("✅ DASHBOARD COMPLETADO")
        print("="*80)
        print("\n📁 Archivos generados en: visualizaciones/")
        print("   • mapa_radares_ideam.html")
        
        if radares_disponibles:
            print(f"   • disponibilidad_{radar_principal.lower()}.html")
            print("   • comparacion_radares.html")
    
    def comparar_radares(self):
        """Compara estadísticas entre diferentes radares"""
        inventario = self.processor.leer_inventario()
        
        if inventario is None or inventario.empty:
            print("   ⚠️ No hay datos disponibles para comparar")
            return
        
        # Agrupar por radar
        comparacion = inventario.groupby('radar').agg({
            'archivo': 'count',
            'tamaño_mb': 'sum'
        }).reset_index()
        
        comparacion.columns = ['Radar', 'Archivos', 'Tamaño_MB']
        comparacion['Tamaño_MB'] = comparacion['Tamaño_MB'].round(2)
        
        # Crear visualización
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=comparacion['Radar'],
            y=comparacion['Archivos'],
            name='Número de Archivos',
            marker_color='indianred',
            text=comparacion['Archivos'],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>' +
                         'Archivos: %{y}<br>' +
                         '<extra></extra>'
        ))
        
        fig.update_layout(
            title='Comparación de Datos entre Radares IDEAM',
            xaxis_title='Radar',
            yaxis_title='Número de Archivos',
            template='plotly_white',
            height=500,
            showlegend=False
        )
        
        output_path = Path("visualizaciones")
        output_path.mkdir(exist_ok=True)
        fig.write_html(output_path / "comparacion_radares.html")
        
        print("   ✅ Comparación generada exitosamente")
        
        # Mostrar tabla
        print("\n   📊 Tabla de Comparación:")
        print(comparacion.to_string(index=False))


def menu_interactivo():
    """Menú interactivo para procesamiento"""
    processor = RadarDataProcessor()
    
    while True:
        print("\n" + "="*80)
        print("📊 PROCESADOR Y VISUALIZADOR DE DATOS RADAR IDEAM")
        print("="*80)
        
        print("\n1. Generar dashboard completo")
        print("2. Ver resumen estadístico de un radar")
        print("3. Visualizar disponibilidad de datos")
        print("4. Listar radares con datos")
        print("5. Salir")
        
        opcion = input("\nSeleccione una opción: ").strip()
        
        if opcion == '1':
            dashboard = EnhancedClimateDashboard()
            dashboard.create_complete_dashboard()
            input("\nPresione Enter para continuar...")
            
        elif opcion == '2':
            radares = processor.listar_radares_con_datos()
            if radares:
                print(f"\nRadares disponibles: {', '.join(radares)}")
                radar = input("Ingrese el radar: ").strip()
                if radar in radares:
                    processor.resumen_estadistico(radar)
                else:
                    print("❌ Radar no válido")
            else:
                print("⚠️  No hay datos descargados")
            input("\nPresione Enter para continuar...")
            
        elif opcion == '3':
            radares = processor.listar_radares_con_datos()
            if radares:
                print(f"\nRadares disponibles: {', '.join(radares)}")
                radar = input("Ingrese el radar: ").strip()
                if radar in radares:
                    fig = processor.visualizar_disponibilidad(radar)
                    if fig:
                        output = Path("visualizaciones")
                        output.mkdir(exist_ok=True)
                        path = output / f"disponibilidad_{radar.lower()}.html"
                        fig.write_html(path)
                        print(f"\n✅ Guardado en: {path}")
                else:
                    print("❌ Radar no válido")
            else:
                print("⚠️  No hay datos descargados")
            input("\nPresione Enter para continuar...")
            
        elif opcion == '4':
            radares = processor.listar_radares_con_datos()
            if radares:
                print("\n📡 Radares con datos descargados:")
                for radar in radares:
                    info = RADARES_IDEAM.get(radar, {})
                    print(f"  • {radar}")
                    print(f"    Ubicación: {info.get('ubicacion', 'N/A')}")
                    print(f"    Distancia a Medellín: {info.get('distancia_medellin_km', 'N/A')} km")
            else:
                print("\n⚠️  No hay datos descargados todavía")
                print("💡 Ejecute primero: python ideam_radar_downloader.py")
            input("\nPresione Enter para continuar...")
            
        elif opcion == '5':
            print("\n👋 ¡Hasta luego!")
            break
            
        else:
            print("❌ Opción no válida")


def main():
    """Función principal para procesamiento"""
    print("📊 PROCESADOR DE DATOS DE RADAR IDEAM 📊")
    
    # Crear dashboard
    dashboard = EnhancedClimateDashboard()
    dashboard.create_complete_dashboard()


if __name__ == "__main__":
    # Modo interactivo por defecto
    menu_interactivo()
    # main()  # Descomentar para modo automático