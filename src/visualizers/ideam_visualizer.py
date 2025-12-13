"""
IDEAM Radar Data Visualizer & Processor - OPTIMIZADO v2.1
==========================================================

Procesa y visualiza datos de radar IDEAM con DataFrames trabajables y gráficas precisas.
Integración con PyART, xradar y acceso directo a AWS S3.

Basado en mejores prácticas de:
- Project Pythia Radar Cookbook
- xradar documentation  
- IDEAM AWS Public Dataset

Referencias:
- https://projectpythia.org/radar-cookbook/
- https://docs.openradarscience.org/projects/xradar/
- https://registry.opendata.aws/ideam-radares/
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import json
from datetime import datetime
from PIL import Image
import io
import warnings
import logging
import re

warnings.filterwarnings('ignore')

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Intentar importar seaborn
try:
    import seaborn as sns
    sns.set_palette("viridis")
    SEABORN_AVAILABLE = True
except ImportError:
    SEABORN_AVAILABLE = False
    logger.warning("⚠️  Seaborn no disponible. Usando matplotlib puro.")

# Intentar importar xradar para procesamiento avanzado
try:
    import xradar as xd
    XRADAR_AVAILABLE = True
    logger.info("✅ xradar disponible para lectura de archivos Sigmet")
except ImportError:
    XRADAR_AVAILABLE = False
    logger.warning("⚠️  xradar no disponible.")

# Intentar importar PyART para procesamiento avanzado
try:
    import pyart
    PYART_AVAILABLE = True
    logger.info("✅ PyART disponible para análisis avanzado")
except ImportError:
    PYART_AVAILABLE = False
    logger.warning("⚠️  PyART no disponible. Funcionalidad limitada.")

# Intentar importar fsspec y boto3 para AWS S3
try:
    import fsspec
    import boto3
    import botocore
    from botocore.client import Config
    AWS_AVAILABLE = True
    logger.info("✅ boto3/fsspec disponibles para acceso a AWS S3")
except ImportError:
    AWS_AVAILABLE = False
    logger.warning("⚠️  boto3/fsspec no disponibles. Acceso a AWS deshabilitado.")

# Configurar estilo de matplotlib
try:
    plt.style.use('seaborn-v0_8-darkgrid')
except:
    plt.style.use('ggplot')


class IDEAMRadarVisualizer:
    """Procesador y visualizador optimizado de datos de radar IDEAM
    
    Soporta:
    - Archivos locales (formato RAW Sigmet)
    - Acceso directo a AWS S3 (s3://s3-radaresideam/)
    - Procesamiento con PyART y xradar
    - DataFrames trabajables con pandas
    """
    
    def __init__(self, data_dir="data/Radar_IDEAM", enable_aws=False):
        self.data_dir = Path(data_dir)
        self.archivos_radar = []
        self.df_radar = None  # DataFrame principal con todos los datos
        self.df_metadata = None  # DataFrame con metadata
        self.radares_info = self._cargar_info_radares()
        self.enable_aws = enable_aws and AWS_AVAILABLE
        
        # Configurar AWS S3 si está habilitado
        if self.enable_aws:
            self._setup_aws()
        
        # Productos disponibles de radar según IDEAM
        self.productos_radar = {
            'DBZH': {'nombre': 'Reflectividad', 'unidad': 'dBZ', 'vmin': -20, 'vmax': 70},
            'VRADH': {'nombre': 'Velocidad Radial', 'unidad': 'm/s', 'vmin': -30, 'vmax': 30},
            'WRADH': {'nombre': 'Ancho Espectral', 'unidad': 'm/s', 'vmin': 0, 'vmax': 10},
            'ZDR': {'nombre': 'Reflectividad Diferencial', 'unidad': 'dB', 'vmin': -2, 'vmax': 5},
            'RHOHV': {'nombre': 'Coeficiente de Correlación', 'unidad': 'adim', 'vmin': 0.5, 'vmax': 1.0},
            'PHIDP': {'nombre': 'Fase Diferencial', 'unidad': '°', 'vmin': 0, 'vmax': 180},
            'KDP': {'nombre': 'Fase Diferencial Específica', 'unidad': '°/km', 'vmin': 0, 'vmax': 10}
        }
    
    def _setup_aws(self):
        """Configura conexión a AWS S3"""
        try:
            self.s3_bucket = "s3-radaresideam"
            self.s3_base_path = "l2_data"
            
            self.s3 = boto3.resource(
                "s3",
                config=Config(signature_version=botocore.UNSIGNED, user_agent_extra="Resource"),
            )
            self.bucket = self.s3.Bucket(self.s3_bucket)
            logger.info("✅ Conexión AWS S3 configurada")
        except Exception as e:
            logger.error(f"❌ Error configurando AWS: {e}")
            self.enable_aws = False
    
    def create_aws_query(self, date, radar_site):
        """
        Crea query para archivos de radar IDEAM en AWS bucket
        
        Args:
            date: datetime object con la fecha/hora
            radar_site: nombre del radar
        
        Returns:
            str: query string para el bucket
        """
        if (date.hour != 0) and (date.minute != 0):
            return f"{self.s3_base_path}/{date:%Y}/{date:%m}/{date:%d}/{radar_site}/{radar_site[:3].upper()}{date:%y%m%d%H%M}"
        elif (date.hour != 0) and (date.minute == 0):
            return f"{self.s3_base_path}/{date:%Y}/{date:%m}/{date:%d}/{radar_site}/{radar_site[:3].upper()}{date:%y%m%d%H}"
        else:
            return f"{self.s3_base_path}/{date:%Y}/{date:%m}/{date:%d}/{radar_site}/{radar_site[:3].upper()}{date:%y%m%d}"
    
    def listar_archivos_aws(self, date, radar_site):
        """
        Lista archivos disponibles en AWS S3 para una fecha y radar
        
        Args:
            date: datetime object
            radar_site: nombre del radar
        
        Returns:
            list: lista de rutas S3
        """
        if not self.enable_aws:
            logger.error("❌ AWS no está habilitado")
            return []
        
        query = self.create_aws_query(date, radar_site)
        logger.info(f"🔍 Buscando en AWS: {query}")
        
        files = [f"s3://{self.s3_bucket}/{i.key}" 
                for i in self.bucket.objects.filter(Prefix=query)]
        
        logger.info(f"📂 Encontrados {len(files)} archivos en AWS")
        return files
    
    def _cargar_info_radares(self):
        """Carga información de radares disponibles"""
        radares = {
            'Barrancabermeja': {'lat': 7.0653, 'lon': -73.8547, 'prefijo': 'BAR'},
            'Carimagua': {'lat': 4.5694, 'lon': -71.3292, 'prefijo': 'CAR'},
            'Munchique': {'lat': 2.5458, 'lon': -76.9631, 'prefijo': 'MUN'},
            'Guaviare': {'lat': 2.5694, 'lon': -72.6411, 'prefijo': 'GUA'}
        }
        return radares
    
    def listar_radares(self):
        """Lista los radares disponibles"""
        if not self.data_dir.exists():
            logger.error(f"❌ Directorio {self.data_dir} no existe")
            return []
        
        radares = [d.name for d in self.data_dir.iterdir() if d.is_dir()]
        
        print(f"\n📡 Radares disponibles: {len(radares)}")
        for radar in radares:
            info = self.radares_info.get(radar, {})
            print(f"  - {radar}", end="")
            if info:
                print(f" (Lat: {info.get('lat')}, Lon: {info.get('lon')})")
            else:
                print()
        
        return radares
    
    def cargar_datos_radar(self, radar_name, limite=None):
        """
        Carga y procesa archivos de radar en DataFrame trabajable
        
        Args:
            radar_name: Nombre del radar (ej: Barrancabermeja)
            limite: Número máximo de archivos a procesar (None = todos)
        
        Returns:
            DataFrame con datos procesados del radar
        """
        radar_path = self.data_dir / radar_name
        
        if not radar_path.exists():
            logger.error(f"❌ Radar {radar_name} no encontrado")
            return None
        
        logger.info(f"\n📡 Procesando radar: {radar_name}")
        
        # Buscar archivos RAW del IDEAM
        archivos_raw = []
        for fecha_dir in radar_path.iterdir():
            if fecha_dir.is_dir():
                archivos_raw.extend(list(fecha_dir.glob("*.RAW*")))
        
        if limite:
            archivos_raw = sorted(archivos_raw)[:limite]
        else:
            archivos_raw = sorted(archivos_raw)
        
        logger.info(f"📂 Archivos encontrados: {len(archivos_raw)}")
        
        # Procesar archivos y crear DataFrame
        datos = []
        
        for i, archivo in enumerate(archivos_raw):
            if i % 50 == 0 and i > 0:
                logger.info(f"  Procesados {i}/{len(archivos_raw)} archivos...")
            
            try:
                info = self._extraer_info_archivo(archivo, radar_name)
                datos.append(info)
                
            except Exception as e:
                logger.warning(f"⚠️  Error procesando {archivo.name}: {e}")
        
        if datos:
            self.df_radar = pd.DataFrame(datos)
            self._enriquecer_dataframe()
            logger.info(f"✅ DataFrame creado con {len(self.df_radar)} registros")
            return self.df_radar
        
        logger.warning("❌ No se pudieron cargar datos")
        return None
    
    def _extraer_info_archivo(self, archivo, radar_name):
        """Extrae información completa del archivo de radar"""
        info = {
            'radar': radar_name,
            'archivo': archivo.name,
            'ruta': str(archivo),
            'tamaño_bytes': archivo.stat().st_size,
            'tamaño_mb': archivo.stat().st_size / (1024 * 1024)
        }
        
        # Extraer timestamp del nombre (formato: BARYYMMDDHHMMSSsss)
        timestamp = self._extraer_timestamp_ideam(archivo.name)
        info['timestamp'] = timestamp
        
        if timestamp:
            info['fecha'] = timestamp.date()
            info['hora'] = timestamp.hour
            info['minuto'] = timestamp.minute
            info['segundo'] = timestamp.second
        
        # Extraer prefijo de radar
        prefijo_match = re.match(r'^([A-Z]{3})', archivo.name)
        if prefijo_match:
            info['prefijo'] = prefijo_match.group(1)
        
        # Si PyART está disponible, intentar extraer datos meteorológicos
        if PYART_AVAILABLE:
            try:
                radar_data = pyart.io.read(str(archivo))
                info['campos_disponibles'] = list(radar_data.fields.keys())
                info['num_sweeps'] = radar_data.nsweeps
                
                # Extraer estadísticas de reflectividad si está disponible
                field_name = None
                for possible_name in ['reflectivity', 'DBZH', 'DBZ', 'REF']:
                    if possible_name in radar_data.fields:
                        field_name = possible_name
                        break
                
                if field_name:
                    reflectividad = radar_data.fields[field_name]['data']
                    info['reflectividad_max'] = float(np.ma.max(reflectividad))
                    info['reflectividad_mean'] = float(np.ma.mean(reflectividad))
                    info['reflectividad_std'] = float(np.ma.std(reflectividad))
                    info['cobertura_pct'] = (np.ma.count(reflectividad) / reflectividad.size) * 100
                    
            except Exception as e:
                logger.debug(f"No se pudo leer con PyART: {e}")
        
        return info
    
    def _extraer_timestamp_ideam(self, filename):
        """Extrae timestamp del formato IDEAM (BARYYMMDDHHMMSSsss)"""
        try:
            # Formato: BAR251209000005 -> BAR + YYMMDD + HHMMSS
            match = re.search(r'([A-Z]{3})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})', filename)
            if match:
                prefijo, yy, mm, dd, hh, mi, ss = match.groups()
                year = 2000 + int(yy)
                return datetime(year, int(mm), int(dd), int(hh), int(mi), int(ss))
        except Exception as e:
            logger.debug(f"Error extrayendo timestamp: {e}")
        
        return None
    
    def _enriquecer_dataframe(self):
        """Agrega columnas calculadas al DataFrame"""
        if self.df_radar is None:
            return
        
        # Ordenar por timestamp
        if 'timestamp' in self.df_radar.columns:
            self.df_radar = self.df_radar.sort_values('timestamp').reset_index(drop=True)
            
            # Agregar información temporal
            self.df_radar['dia_semana'] = self.df_radar['timestamp'].dt.day_name()
            self.df_radar['es_dia'] = (self.df_radar['hora'] >= 6) & (self.df_radar['hora'] < 18)
            self.df_radar['periodo'] = pd.cut(self.df_radar['hora'], 
                                              bins=[0, 6, 12, 18, 24],
                                              labels=['Madrugada', 'Mañana', 'Tarde', 'Noche'])
        
        # Categorizar por intensidad de reflectividad
        if 'reflectividad_max' in self.df_radar.columns:
            self.df_radar['intensidad'] = pd.cut(self.df_radar['reflectividad_max'],
                                                  bins=[-np.inf, 20, 40, 50, np.inf],
                                                  labels=['Débil', 'Moderada', 'Fuerte', 'Muy Fuerte'])
    
    def obtener_dataframe_trabajable(self):
        """Retorna el DataFrame principal con datos procesados"""
        if self.df_radar is None:
            logger.warning("❌ No hay datos cargados. Use cargar_datos_radar() primero")
            return None
        
        # Seleccionar columnas más relevantes
        columnas_relevantes = ['radar', 'timestamp', 'fecha', 'hora', 'periodo',
                               'tamaño_mb', 'archivo']
        
        # Agregar columnas de reflectividad si existen
        if 'reflectividad_max' in self.df_radar.columns:
            columnas_relevantes.extend(['reflectividad_max', 'reflectividad_mean', 
                                       'intensidad', 'cobertura_pct'])
        
        # Filtrar columnas que existan
        columnas_existentes = [col for col in columnas_relevantes if col in self.df_radar.columns]
        
        return self.df_radar[columnas_existentes].copy()
    
    def estadisticas_completas(self):
        """Estadísticas detalladas de los datos de radar"""
        if self.df_radar is None or len(self.df_radar) == 0:
            logger.error("❌ No hay datos cargados")
            return None
        
        print("\n" + "="*70)
        print("📊 ESTADÍSTICAS COMPLETAS - RADAR IDEAM")
        print("="*70)
        
        radar_name = self.df_radar['radar'].iloc[0]
        print(f"\n📡 Radar: {radar_name}")
        print(f"📂 Total de archivos: {len(self.df_radar)}")
        
        # Estadísticas de tamaño
        print(f"\n💾 Tamaño de archivos:")
        print(f"  - Total: {self.df_radar['tamaño_mb'].sum():.2f} MB")
        print(f"  - Promedio: {self.df_radar['tamaño_mb'].mean():.2f} MB")
        print(f"  - Máximo: {self.df_radar['tamaño_mb'].max():.2f} MB")
        print(f"  - Mínimo: {self.df_radar['tamaño_mb'].min():.2f} MB")
        
        # Estadísticas temporales
        if 'timestamp' in self.df_radar.columns:
            print(f"\n📅 Rango temporal:")
            print(f"  - Desde: {self.df_radar['timestamp'].min()}")
            print(f"  - Hasta: {self.df_radar['timestamp'].max()}")
            print(f"  - Duración: {self.df_radar['timestamp'].max() - self.df_radar['timestamp'].min()}")
            
            duration_hours = (self.df_radar['timestamp'].max() - self.df_radar['timestamp'].min()).total_seconds() / 3600
            if duration_hours > 0:
                print(f"  - Archivos por hora: {len(self.df_radar) / duration_hours:.1f}")
        
        # Estadísticas de reflectividad
        if 'reflectividad_max' in self.df_radar.columns:
            print(f"\n⚡ Reflectividad (dBZ):")
            print(f"  - Máxima: {self.df_radar['reflectividad_max'].max():.2f}")
            print(f"  - Promedio: {self.df_radar['reflectividad_mean'].mean():.2f}")
            print(f"  - Desviación: {self.df_radar['reflectividad_std'].mean():.2f}")
            
            if 'intensidad' in self.df_radar.columns:
                print(f"\n🌧️  Distribución por intensidad:")
                intensidad_counts = self.df_radar['intensidad'].value_counts()
                for intensidad, count in intensidad_counts.items():
                    pct = (count / len(self.df_radar)) * 100
                    print(f"  - {intensidad}: {count} archivos ({pct:.1f}%)")
        
        # Retornar también como dict para uso programático
        stats = {
            'radar': radar_name,
            'total_archivos': len(self.df_radar),
            'tamaño_total_mb': self.df_radar['tamaño_mb'].sum(),
            'periodo_inicio': self.df_radar['timestamp'].min() if 'timestamp' in self.df_radar.columns else None,
            'periodo_fin': self.df_radar['timestamp'].max() if 'timestamp' in self.df_radar.columns else None
        }
        
        return stats
    
    def grafica_serie_temporal_reflectividad(self, save_path=None):
        """Gráfica de serie temporal de reflectividad"""
        if self.df_radar is None or 'reflectividad_max' not in self.df_radar.columns:
            logger.error("❌ No hay datos de reflectividad disponibles")
            return
        
        fig, axes = plt.subplots(2, 1, figsize=(15, 10))
        radar_name = self.df_radar['radar'].iloc[0]
        
        # Gráfica 1: Reflectividad máxima y promedio
        axes[0].plot(self.df_radar['timestamp'], self.df_radar['reflectividad_max'], 
                    label='Reflectividad Máxima', linewidth=2, alpha=0.8)
        axes[0].plot(self.df_radar['timestamp'], self.df_radar['reflectividad_mean'], 
                    label='Reflectividad Promedio', linewidth=2, alpha=0.6)
        
        # Líneas de referencia
        axes[0].axhline(y=20, color='yellow', linestyle='--', alpha=0.5, label='Lluvia débil')
        axes[0].axhline(y=40, color='orange', linestyle='--', alpha=0.5, label='Lluvia moderada')
        axes[0].axhline(y=50, color='red', linestyle='--', alpha=0.5, label='Lluvia fuerte')
        
        axes[0].set_xlabel('Tiempo', fontsize=12)
        axes[0].set_ylabel('Reflectividad (dBZ)', fontsize=12)
        axes[0].set_title(f'Serie Temporal de Reflectividad - Radar {radar_name}', 
                         fontsize=14, fontweight='bold')
        axes[0].legend(loc='best')
        axes[0].grid(True, alpha=0.3)
        
        # Gráfica 2: Cobertura del radar
        if 'cobertura_pct' in self.df_radar.columns:
            axes[1].fill_between(self.df_radar['timestamp'], self.df_radar['cobertura_pct'], 
                                alpha=0.6, color='steelblue')
            axes[1].set_xlabel('Tiempo', fontsize=12)
            axes[1].set_ylabel('Cobertura (%)', fontsize=12)
            axes[1].set_title('Cobertura del Radar', fontsize=14, fontweight='bold')
            axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"✅ Gráfica guardada en {save_path}")
        
        plt.show()
    
    def grafica_distribucion_intensidad(self, save_path=None):
        """Gráfica de distribución de intensidades de reflectividad"""
        if self.df_radar is None or 'reflectividad_max' not in self.df_radar.columns:
            logger.error("❌ No hay datos de reflectividad disponibles")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        radar_name = self.df_radar['radar'].iloc[0]
        
        # Histograma de reflectividad máxima
        axes[0, 0].hist(self.df_radar['reflectividad_max'], bins=30, 
                       color='steelblue', alpha=0.7, edgecolor='black')
        axes[0, 0].axvline(self.df_radar['reflectividad_max'].mean(), 
                          color='red', linestyle='--', linewidth=2, label='Media')
        axes[0, 0].set_xlabel('Reflectividad Máxima (dBZ)', fontsize=11)
        axes[0, 0].set_ylabel('Frecuencia', fontsize=11)
        axes[0, 0].set_title('Distribución de Reflectividad Máxima', fontsize=12, fontweight='bold')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Boxplot de reflectividad promedio
        axes[0, 1].boxplot([self.df_radar['reflectividad_mean'].dropna()], 
                          labels=['Reflectividad Promedio'])
        axes[0, 1].set_ylabel('dBZ', fontsize=11)
        axes[0, 1].set_title('Boxplot de Reflectividad Promedio', fontsize=12, fontweight='bold')
        axes[0, 1].grid(True, alpha=0.3, axis='y')
        
        # Distribución por periodo del día
        if 'periodo' in self.df_radar.columns:
            periodo_stats = self.df_radar.groupby('periodo')['reflectividad_max'].agg(['mean', 'std'])
            axes[1, 0].bar(range(len(periodo_stats)), periodo_stats['mean'], 
                          yerr=periodo_stats['std'], capsize=5, 
                          color='coral', alpha=0.7, edgecolor='black')
            axes[1, 0].set_xticks(range(len(periodo_stats)))
            axes[1, 0].set_xticklabels(periodo_stats.index, rotation=45)
            axes[1, 0].set_ylabel('Reflectividad Promedio (dBZ)', fontsize=11)
            axes[1, 0].set_title('Reflectividad por Periodo del Día', fontsize=12, fontweight='bold')
            axes[1, 0].grid(True, alpha=0.3, axis='y')
        
        # Distribución de categorías de intensidad
        if 'intensidad' in self.df_radar.columns:
            intensidad_counts = self.df_radar['intensidad'].value_counts().sort_index()
            colors = ['lightblue', 'yellow', 'orange', 'red']
            axes[1, 1].pie(intensidad_counts.values, labels=intensidad_counts.index, 
                          autopct='%1.1f%%', colors=colors[:len(intensidad_counts)],
                          startangle=90)
            axes[1, 1].set_title('Distribución de Intensidades', fontsize=12, fontweight='bold')
        
        fig.suptitle(f'Análisis de Intensidad - Radar {radar_name}', 
                    fontsize=16, fontweight='bold', y=0.995)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"✅ Gráfica guardada en {save_path}")
        
        plt.show()
    
    def grafica_patron_temporal(self, save_path=None):
        """Gráfica de patrones temporales de actividad del radar"""
        if self.df_radar is None or 'hora' not in self.df_radar.columns:
            logger.error("❌ No hay datos temporales disponibles")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        radar_name = self.df_radar['radar'].iloc[0]
        
        # Actividad por hora
        hora_counts = self.df_radar.groupby('hora').size()
        axes[0, 0].bar(hora_counts.index, hora_counts.values, 
                      color='steelblue', alpha=0.7, edgecolor='black')
        axes[0, 0].set_xlabel('Hora del día', fontsize=11)
        axes[0, 0].set_ylabel('Número de archivos', fontsize=11)
        axes[0, 0].set_title('Distribución de Archivos por Hora', fontsize=12, fontweight='bold')
        axes[0, 0].set_xticks(range(0, 24, 2))
        axes[0, 0].grid(True, alpha=0.3, axis='y')
        
        # Timeline con reflectividad
        if 'reflectividad_max' in self.df_radar.columns:
            scatter = axes[0, 1].scatter(self.df_radar['timestamp'], 
                                        self.df_radar['hora'],
                                        c=self.df_radar['reflectividad_max'],
                                        cmap='viridis', s=50, alpha=0.6)
            plt.colorbar(scatter, ax=axes[0, 1], label='Reflectividad (dBZ)')
            axes[0, 1].set_xlabel('Fecha', fontsize=11)
            axes[0, 1].set_ylabel('Hora del día', fontsize=11)
            axes[0, 1].set_title('Timeline con Intensidad', fontsize=12, fontweight='bold')
            axes[0, 1].grid(True, alpha=0.3)
        
        # Heatmap hora vs fecha
        if 'fecha' in self.df_radar.columns:
            pivot_data = self.df_radar.groupby(['fecha', 'hora']).size().reset_index(name='count')
            pivot_table = pivot_data.pivot(index='hora', columns='fecha', values='count').fillna(0)
            
            if len(pivot_table.columns) > 0:
                if SEABORN_AVAILABLE:
                    import seaborn as sns
                    sns.heatmap(pivot_table, cmap='YlOrRd', ax=axes[1, 0], 
                               cbar_kws={'label': 'Número de archivos'})
                else:
                    # Usar imshow de matplotlib si seaborn no está disponible
                    im = axes[1, 0].imshow(pivot_table.values, cmap='YlOrRd', aspect='auto')
                    axes[1, 0].set_yticks(range(len(pivot_table.index)))
                    axes[1, 0].set_yticklabels(pivot_table.index)
                    plt.colorbar(im, ax=axes[1, 0], label='Número de archivos')
                
                axes[1, 0].set_xlabel('Fecha', fontsize=11)
                axes[1, 0].set_ylabel('Hora', fontsize=11)
                axes[1, 0].set_title('Heatmap de Actividad', fontsize=12, fontweight='bold')
        
        # Reflectividad promedio por hora
        if 'reflectividad_mean' in self.df_radar.columns:
            hora_refl = self.df_radar.groupby('hora')['reflectividad_mean'].agg(['mean', 'std'])
            axes[1, 1].errorbar(hora_refl.index, hora_refl['mean'], 
                               yerr=hora_refl['std'], fmt='o-', 
                               capsize=5, capthick=2, linewidth=2,
                               color='darkorange', alpha=0.7)
            axes[1, 1].set_xlabel('Hora del día', fontsize=11)
            axes[1, 1].set_ylabel('Reflectividad Promedio (dBZ)', fontsize=11)
            axes[1, 1].set_title('Reflectividad Promedio por Hora', fontsize=12, fontweight='bold')
            axes[1, 1].set_xticks(range(0, 24, 2))
            axes[1, 1].grid(True, alpha=0.3)
        
        fig.suptitle(f'Análisis de Patrones Temporales - Radar {radar_name}', 
                    fontsize=16, fontweight='bold', y=0.995)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"✅ Gráfica guardada en {save_path}")
        
        plt.show()
    
    def grafica_resumen_completo(self, save_path=None):
        """Genera dashboard completo con todas las métricas principales"""
        if self.df_radar is None:
            logger.error("❌ No hay datos cargados")
            return
        
        fig = plt.figure(figsize=(18, 12))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        radar_name = self.df_radar['radar'].iloc[0]
        
        # Serie temporal principal
        ax1 = fig.add_subplot(gs[0, :])
        if 'reflectividad_max' in self.df_radar.columns:
            ax1.plot(self.df_radar['timestamp'], self.df_radar['reflectividad_max'], 
                    linewidth=2, color='darkblue', alpha=0.7)
            ax1.fill_between(self.df_radar['timestamp'], self.df_radar['reflectividad_max'], 
                           alpha=0.3, color='steelblue')
            ax1.set_ylabel('Reflectividad Máxima (dBZ)', fontsize=12, fontweight='bold')
            ax1.set_title(f'Dashboard Completo - Radar {radar_name}', 
                         fontsize=16, fontweight='bold')
            ax1.grid(True, alpha=0.3)
        
        # Distribución de intensidad
        ax2 = fig.add_subplot(gs[1, 0])
        if 'intensidad' in self.df_radar.columns:
            intensidad_counts = self.df_radar['intensidad'].value_counts()
            colors = ['lightblue', 'yellow', 'orange', 'red']
            ax2.pie(intensidad_counts.values, labels=intensidad_counts.index,
                   autopct='%1.1f%%', colors=colors[:len(intensidad_counts)])
            ax2.set_title('Distribución de Intensidades', fontsize=12, fontweight='bold')
        
        # Actividad por hora
        ax3 = fig.add_subplot(gs[1, 1])
        if 'hora' in self.df_radar.columns:
            hora_counts = self.df_radar.groupby('hora').size()
            ax3.bar(hora_counts.index, hora_counts.values, color='coral', alpha=0.7)
            ax3.set_xlabel('Hora', fontsize=10)
            ax3.set_ylabel('Archivos', fontsize=10)
            ax3.set_title('Actividad por Hora', fontsize=12, fontweight='bold')
            ax3.grid(True, alpha=0.3, axis='y')
        
        # Estadísticas textuales
        ax4 = fig.add_subplot(gs[1, 2])
        ax4.axis('off')
        stats_text = f"""ESTADÍSTICAS GENERALES
        
Total archivos: {len(self.df_radar)}
Tamaño total: {self.df_radar['tamaño_mb'].sum():.1f} MB
"""
        
        if 'reflectividad_max' in self.df_radar.columns:
            stats_text += f"""
Refl. máxima: {self.df_radar['reflectividad_max'].max():.1f} dBZ
Refl. promedio: {self.df_radar['reflectividad_mean'].mean():.1f} dBZ
"""
        
        if 'timestamp' in self.df_radar.columns:
            duration = self.df_radar['timestamp'].max() - self.df_radar['timestamp'].min()
            stats_text += f"""
Periodo: {duration}
Desde: {self.df_radar['timestamp'].min().strftime('%Y-%m-%d %H:%M')}
Hasta: {self.df_radar['timestamp'].max().strftime('%Y-%m-%d %H:%M')}
"""
        
        ax4.text(0.1, 0.9, stats_text, transform=ax4.transAxes, 
                fontsize=10, verticalalignment='top', family='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        # Histograma de reflectividad
        ax5 = fig.add_subplot(gs[2, 0:2])
        if 'reflectividad_max' in self.df_radar.columns:
            ax5.hist(self.df_radar['reflectividad_max'], bins=40, 
                    color='steelblue', alpha=0.7, edgecolor='black')
            ax5.set_xlabel('Reflectividad Máxima (dBZ)', fontsize=11)
            ax5.set_ylabel('Frecuencia', fontsize=11)
            ax5.set_title('Distribución de Reflectividad', fontsize=12, fontweight='bold')
            ax5.grid(True, alpha=0.3, axis='y')
        
        # Cobertura
        ax6 = fig.add_subplot(gs[2, 2])
        if 'cobertura_pct' in self.df_radar.columns:
            ax6.boxplot([self.df_radar['cobertura_pct'].dropna()], labels=['Cobertura'])
            ax6.set_ylabel('Cobertura (%)', fontsize=11)
            ax6.set_title('Cobertura del Radar', fontsize=12, fontweight='bold')
            ax6.grid(True, alpha=0.3, axis='y')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"✅ Dashboard guardado en {save_path}")
        
        plt.show()
    
    def exportar_datos(self, formato='csv', ruta=None):
        """Exporta DataFrame procesado a archivo
        
        Args:
            formato: 'csv', 'excel', 'json', 'parquet'
            ruta: Ruta de salida (None = auto)
        """
        if self.df_radar is None:
            logger.error("❌ No hay datos para exportar")
            return
        
        if ruta is None:
            radar_name = self.df_radar['radar'].iloc[0]
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            ruta = Path(f"data/processed/ideam_radar_{radar_name}_{timestamp}.{formato}")
        else:
            ruta = Path(ruta)
        
        ruta.parent.mkdir(parents=True, exist_ok=True)
        
        if formato == 'csv':
            self.df_radar.to_csv(ruta, index=False)
        elif formato == 'excel':
            self.df_radar.to_excel(ruta, index=False)
        elif formato == 'json':
            self.df_radar.to_json(ruta, orient='records', date_format='iso', indent=2)
        elif formato == 'parquet':
            self.df_radar.to_parquet(ruta, index=False)
        else:
            logger.error(f"Formato {formato} no soportado")
            return
        
        logger.info(f"✅ Datos exportados a {ruta}")
        return ruta


def main():
    """Función principal de demostración"""
    print("\n" + "="*70)
    print("📡 IDEAM RADAR VISUALIZER - VERSIÓN OPTIMIZADA")
    print("="*70)
    
    visualizer = IDEAMRadarVisualizer()
    
    # Listar radares disponibles
    radares = visualizer.listar_radares()
    
    if radares:
        # Usar el primer radar disponible
        radar = radares[0]
        logger.info(f"\n🔄 Procesando radar: {radar}")
        
        # Cargar datos (limitar a 100 archivos para demo)
        df = visualizer.cargar_datos_radar(radar, limite=100)
        
        if df is not None:
            # Mostrar estadísticas
            visualizer.estadisticas_completas()
            
            # Obtener DataFrame trabajable
            df_trabajable = visualizer.obtener_dataframe_trabajable()
            print("\n📊 Vista del DataFrame trabajable:")
            print(df_trabajable.head(10))
            print(f"\nColumnas disponibles: {list(df_trabajable.columns)}")
            
            # Generar gráficas
            output_dir = Path("visualizaciones/ideam")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info("\n📈 Generando visualizaciones...")
            
            # Dashboard completo
            visualizer.grafica_resumen_completo(
                save_path=output_dir / f"dashboard_{radar}.png"
            )
            
            # Serie temporal de reflectividad
            if 'reflectividad_max' in df_trabajable.columns:
                visualizer.grafica_serie_temporal_reflectividad(
                    save_path=output_dir / f"serie_temporal_{radar}.png"
                )
            
            # Distribución de intensidad
            if 'reflectividad_max' in df_trabajable.columns:
                visualizer.grafica_distribucion_intensidad(
                    save_path=output_dir / f"distribucion_{radar}.png"
                )
            
            # Patrones temporales
            if 'hora' in df_trabajable.columns:
                visualizer.grafica_patron_temporal(
                    save_path=output_dir / f"patrones_temporales_{radar}.png"
                )
            
            # Exportar datos
            visualizer.exportar_datos(formato='csv')
            visualizer.exportar_datos(formato='json')
            
            logger.info("\n✅ Procesamiento completado exitosamente")
            logger.info(f"📁 Visualizaciones guardadas en: {output_dir}")
    else:
        logger.error("❌ No se encontraron radares disponibles")


if __name__ == "__main__":
    main()
