"""
Script para descargar datos de radares meteorológicos IDEAM desde AWS Open Data
Guarda datos en data/Radar_IDEAM y logs en logs/ideam
"""
import os
import boto3
import gzip
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import logging
from botocore import UNSIGNED
from botocore.config import Config
import json

# Configuración de logging
log_dir = Path("logs/ideam")
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f'radar_ideam_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class IDEAMRadarDownloader:
    """Clase para descargar y procesar datos de radares IDEAM"""
    
    # Información de radares disponibles en AWS (solo 4 radares actualmente)
    RADARES_DISPONIBLES = {
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
    
    def __init__(self, base_dir="data/Radar_IDEAM"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar cliente S3 sin credenciales (bucket público)
        self.s3_client = boto3.client(
            's3',
            config=Config(signature_version=UNSIGNED),
            region_name='us-east-1'
        )
        
        # Bucket correcto según documentación oficial
        self.bucket_name = 's3-radaresideam'
        
        logger.info("IDEAMRadarDownloader inicializado")
        logger.info(f"Bucket AWS: s3://{self.bucket_name}")
        logger.info(f"Directorio de datos: {self.base_dir}")
    
    def listar_radares(self):
        """Muestra la lista de radares disponibles"""
        print("\n" + "="*80)
        print("RADARES METEOROLÓGICOS IDEAM DISPONIBLES EN AWS")
        print("="*80)
        print("\n⚠️  NOTA: Santa Elena NO está disponible en AWS Open Data")
        print("Los datos disponibles son de 4 radares con delay de 24 horas:")
        
        # Ordenar por distancia a Medellín
        radares_ordenados = sorted(
            self.RADARES_DISPONIBLES.items(),
            key=lambda x: x[1]['distancia_medellin_km']
        )
        
        for idx, (codigo, info) in enumerate(radares_ordenados, 1):
            print(f"\n{idx}. {codigo}")
            print(f"   Ubicación: {info['ubicacion']}")
            print(f"   Coordenadas: {info['lat']:.4f}°N, {info['lon']:.4f}°W")
            print(f"   Distancia a Medellín: ~{info['distancia_medellin_km']} km")
            print(f"   Prefijo archivos: {info['prefijo']}")
            
            # Destacar el más cercano
            if idx == 1:
                print(f"   ⭐ MÁS CERCANO A MEDELLÍN ⭐")
        
        print("\n" + "="*80)
        print("📅 Datos disponibles: 2018 - presente (con 24h de delay)")
        print("🔄 Actualización: Datos agregados con 1 día de retraso")
        print("="*80)
        
        return self.RADARES_DISPONIBLES
    
    def seleccionar_radar(self, codigo=None):
        """Permite seleccionar un radar interactivamente o por código"""
        if codigo and codigo in self.RADARES_DISPONIBLES:
            logger.info(f"Radar seleccionado: {codigo}")
            return codigo
        
        self.listar_radares()
        
        print("\nOpciones de selección:")
        print("1. Ingrese el nombre del radar (ej: Barrancabermeja)")
        print("2. Presione ENTER para usar Barrancabermeja (más cercano a Medellín)")
        
        seleccion = input("\nSelección: ").strip()
        
        if not seleccion:
            seleccion = 'Barrancabermeja'
            logger.info("Usando radar por defecto: Barrancabermeja")
        
        if seleccion not in self.RADARES_DISPONIBLES:
            logger.warning(f"Radar '{seleccion}' no encontrado. Usando Barrancabermeja")
            seleccion = 'Barrancabermeja'
        
        logger.info(f"Radar seleccionado: {seleccion}")
        return seleccion
    
    def crear_query_prefix(self, radar, fecha):
        """Crea el prefijo de búsqueda según formato IDEAM"""
        # Formato: l2_data/YYYY/MM/DD/Radar_name/PREFIJO
        prefijo_radar = self.RADARES_DISPONIBLES[radar]['prefijo']
        prefix = f"l2_data/{fecha.year}/{fecha.month:02d}/{fecha.day:02d}/{radar}/{prefijo_radar}{fecha:%y%m%d}"
        return prefix
    
    def listar_archivos_disponibles(self, radar, fecha=None, limite=1000):
        """Lista archivos disponibles en S3 para un radar específico"""
        if fecha is None:
            # Por defecto, buscar ayer (los datos tienen 24h de delay)
            fecha = datetime.now() - timedelta(days=1)
        
        prefix = self.crear_query_prefix(radar, fecha)
        
        logger.info(f"Buscando archivos en: s3://{self.bucket_name}/{prefix}")
        
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=limite
            )
            
            archivos = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    archivos.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'],
                        'filename': os.path.basename(obj['Key'])
                    })
                
                logger.info(f"✅ Encontrados {len(archivos)} archivos para {radar} en {fecha.date()}")
            else:
                logger.warning(f"⚠️  No se encontraron archivos para {radar} en {fecha.date()}")
                logger.info(f"💡 Sugerencia: Los datos tienen 24h de delay. Intente con fechas anteriores.")
            
            return archivos
            
        except Exception as e:
            logger.error(f"❌ Error listando archivos: {e}")
            return []
    
    def descargar_archivo(self, radar, archivo_key, fecha=None):
        """Descarga un archivo específico del radar"""
        if fecha is None:
            fecha = datetime.now() - timedelta(days=1)
        
        # Crear directorio para el radar y fecha
        radar_dir = self.base_dir / radar / fecha.strftime("%Y%m%d")
        radar_dir.mkdir(parents=True, exist_ok=True)
        
        filename = os.path.basename(archivo_key)
        local_path = radar_dir / filename
        
        # Verificar si ya existe
        if local_path.exists():
            logger.info(f"⏭️  Archivo ya existe: {filename}")
            return local_path
        
        try:
            logger.info(f"⬇️  Descargando: {filename}")
            self.s3_client.download_file(
                self.bucket_name,
                archivo_key,
                str(local_path)
            )
            file_size_mb = local_path.stat().st_size / (1024 * 1024)
            logger.info(f"✅ Descargado: {filename} ({file_size_mb:.2f} MB)")
            return local_path
            
        except Exception as e:
            logger.error(f"❌ Error descargando {filename}: {e}")
            return None
    
    def descargar_rango_fechas(self, radar, fecha_inicio, fecha_fin, max_archivos=None):
        """Descarga archivos de un radar en un rango de fechas"""
        logger.info(f"📡 Iniciando descarga para {radar}")
        logger.info(f"📅 Rango: {fecha_inicio.date()} a {fecha_fin.date()}")
        
        # Advertencia sobre delay de datos
        fecha_limite = datetime.now() - timedelta(days=1)
        if fecha_fin > fecha_limite:
            logger.warning(f"⚠️  Los datos tienen 24h de delay. Ajustando fecha fin a {fecha_limite.date()}")
            fecha_fin = fecha_limite
        
        archivos_descargados = []
        fecha_actual = fecha_inicio
        total_archivos = 0
        
        while fecha_actual <= fecha_fin:
            logger.info(f"📅 Procesando fecha: {fecha_actual.date()}")
            
            # Listar archivos disponibles
            archivos = self.listar_archivos_disponibles(radar, fecha_actual)
            
            if archivos:
                for archivo in archivos:
                    if max_archivos and total_archivos >= max_archivos:
                        logger.info(f"🛑 Límite de {max_archivos} archivos alcanzado")
                        return archivos_descargados
                    
                    # Descargar archivo
                    local_path = self.descargar_archivo(radar, archivo['key'], fecha_actual)
                    if local_path:
                        archivos_descargados.append({
                            'radar': radar,
                            'fecha': fecha_actual,
                            'archivo': archivo['filename'],
                            'ruta_local': str(local_path),
                            'tamaño_mb': archivo['size'] / (1024 * 1024)
                        })
                        total_archivos += 1
            
            fecha_actual += timedelta(days=1)
        
        logger.info(f"✅ Descarga completada. Total archivos: {len(archivos_descargados)}")
        return archivos_descargados
    
    def generar_inventario(self, radar=None):
        """Genera un inventario de todos los archivos descargados"""
        logger.info("📋 Generando inventario de archivos descargados")
        
        inventario = []
        
        # Si se especifica radar, solo ese
        if radar:
            radares_a_inventariar = [radar]
        else:
            radares_a_inventariar = [d.name for d in self.base_dir.iterdir() if d.is_dir()]
        
        for radar_nombre in radares_a_inventariar:
            radar_path = self.base_dir / radar_nombre
            
            if not radar_path.exists():
                continue
            
            for fecha_dir in radar_path.iterdir():
                if fecha_dir.is_dir():
                    for archivo in fecha_dir.iterdir():
                        if archivo.is_file() and not archivo.name.endswith('.txt'):
                            info_radar = self.RADARES_DISPONIBLES.get(radar_nombre, {})
                            inventario.append({
                                'radar': radar_nombre,
                                'ubicacion': info_radar.get('ubicacion', 'N/A'),
                                'distancia_medellin_km': info_radar.get('distancia_medellin_km', 0),
                                'fecha_directorio': fecha_dir.name,
                                'archivo': archivo.name,
                                'ruta_completa': str(archivo),
                                'tamaño_mb': archivo.stat().st_size / (1024 * 1024),
                                'fecha_modificacion': datetime.fromtimestamp(archivo.stat().st_mtime)
                            })
        
        df_inventario = pd.DataFrame(inventario)
        
        if not df_inventario.empty:
            # Guardar inventario
            inventario_path = self.base_dir / 'inventario_radares.csv'
            df_inventario.to_csv(inventario_path, index=False)
            logger.info(f"💾 Inventario guardado en: {inventario_path}")
            
            # Generar resumen
            resumen_path = self.base_dir / 'resumen_radares.txt'
            with open(resumen_path, 'w', encoding='utf-8') as f:
                f.write("="*80 + "\n")
                f.write("RESUMEN DE DATOS DE RADARES IDEAM\n")
                f.write("="*80 + "\n\n")
                f.write(f"Generado: {datetime.now()}\n")
                f.write(f"Total de archivos: {len(df_inventario)}\n")
                f.write(f"Espacio total: {df_inventario['tamaño_mb'].sum():.2f} MB\n\n")
                
                f.write("Archivos por radar:\n")
                f.write("-" * 80 + "\n")
                resumen_radar = df_inventario.groupby('radar').agg({
                    'archivo': 'count',
                    'tamaño_mb': 'sum'
                }).round(2)
                resumen_radar.columns = ['Archivos', 'Tamaño_MB']
                f.write(resumen_radar.to_string())
                f.write("\n\n")
                
                f.write("Información de radares disponibles en AWS:\n")
                f.write("-" * 80 + "\n")
                for radar, info in sorted(self.RADARES_DISPONIBLES.items(), 
                                        key=lambda x: x[1]['distancia_medellin_km']):
                    tiene_datos = radar in df_inventario['radar'].values
                    f.write(f"\n{radar} {'✓' if tiene_datos else '✗'}:\n")
                    f.write(f"  Ubicación: {info['ubicacion']}\n")
                    f.write(f"  Coordenadas: {info['lat']:.4f}°N, {info['lon']:.4f}°W\n")
                    f.write(f"  Distancia a Medellín: {info['distancia_medellin_km']} km\n")
                    f.write(f"  Prefijo: {info['prefijo']}\n")
                    if tiene_datos:
                        n_archivos = len(df_inventario[df_inventario['radar'] == radar])
                        f.write(f"  Archivos descargados: {n_archivos}\n")
            
            logger.info(f"📄 Resumen guardado en: {resumen_path}")
            
            # Mostrar resumen en consola
            print("\n" + "="*80)
            print("📊 RESUMEN DE DESCARGA")
            print("="*80)
            print(f"\nArchivos por radar:")
            print(resumen_radar.to_string())
            print(f"\nEspacio total: {df_inventario['tamaño_mb'].sum():.2f} MB")
        
        return df_inventario
    
    def descargar_ultimos_datos(self, radar=None, dias=2, max_archivos=100):
        """Descarga los datos más recientes de un radar"""
        if radar is None:
            radar = 'Barrancabermeja'  # Por defecto el más cercano a Medellín
        
        # Los datos tienen 24h de delay, así que empezamos desde hace 2 días
        fecha_fin = datetime.now() - timedelta(days=1)
        fecha_inicio = fecha_fin - timedelta(days=dias)
        
        logger.info(f"📡 Descargando últimos {dias} días de datos para {radar}")
        logger.info(f"💡 Nota: Los datos IDEAM tienen 24 horas de retraso")
        
        return self.descargar_rango_fechas(
            radar, 
            fecha_inicio, 
            fecha_fin,
            max_archivos=max_archivos
        )
    
    def verificar_disponibilidad(self, radar, fecha):
        """Verifica si hay datos disponibles para una fecha específica"""
        archivos = self.listar_archivos_disponibles(radar, fecha)
        return len(archivos) > 0


def menu_interactivo():
    """Menú interactivo para el usuario"""
    print("\n" + "="*80)
    print("🌧️ DESCARGADOR DE DATOS DE RADARES METEOROLÓGICOS IDEAM 🌧️")
    print("="*80)
    
    downloader = IDEAMRadarDownloader()
    
    while True:
        print("\n📋 MENÚ PRINCIPAL:")
        print("1. Listar radares disponibles")
        print("2. Descargar últimos datos disponibles (2-3 días)")
        print("3. Descargar rango de fechas")
        print("4. Verificar disponibilidad de fecha")
        print("5. Generar inventario de archivos descargados")
        print("6. Salir")
        
        opcion = input("\nSeleccione una opción (1-6): ").strip()
        
        if opcion == '1':
            downloader.listar_radares()
            input("\nPresione Enter para continuar...")
            
        elif opcion == '2':
            radar = downloader.seleccionar_radar()
            dias = input("¿Cuántos días hacia atrás? (por defecto 2): ").strip()
            dias = int(dias) if dias.isdigit() else 2
            
            archivos = downloader.descargar_ultimos_datos(radar, dias=dias)
            print(f"\n✅ Descargados {len(archivos)} archivos")
            input("\nPresione Enter para continuar...")
            
        elif opcion == '3':
            radar = downloader.seleccionar_radar()
            
            print("\n💡 Recuerde: Los datos tienen 24h de delay")
            fecha_inicio_str = input("Fecha inicio (YYYY-MM-DD): ").strip()
            fecha_fin_str = input("Fecha fin (YYYY-MM-DD): ").strip()
            
            try:
                fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d")
                fecha_fin = datetime.strptime(fecha_fin_str, "%Y-%m-%d")
                
                max_archivos = input("Límite de archivos (Enter para sin límite): ").strip()
                max_archivos = int(max_archivos) if max_archivos.isdigit() else None
                
                archivos = downloader.descargar_rango_fechas(
                    radar, fecha_inicio, fecha_fin, max_archivos
                )
                print(f"\n✅ Descargados {len(archivos)} archivos")
                input("\nPresione Enter para continuar...")
                
            except ValueError as e:
                print(f"❌ Error en formato de fecha: {e}")
                
        elif opcion == '4':
            radar = downloader.seleccionar_radar()
            fecha_str = input("Fecha a verificar (YYYY-MM-DD): ").strip()
            try:
                fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
                if downloader.verificar_disponibilidad(radar, fecha):
                    print(f"✅ Hay datos disponibles para {fecha.date()}")
                else:
                    print(f"❌ No hay datos disponibles para {fecha.date()}")
                input("\nPresione Enter para continuar...")
            except ValueError:
                print("❌ Formato de fecha inválido")
                
        elif opcion == '5':
            radar = input("Radar específico (Enter para todos): ").strip() or None
            inventario = downloader.generar_inventario(radar)
            if not inventario.empty:
                print(f"\n✅ Inventario generado con {len(inventario)} archivos")
            else:
                print("\n⚠️  No hay archivos descargados todavía")
            input("\nPresione Enter para continuar...")
            
        elif opcion == '6':
            print("\n👋 ¡Hasta luego!")
            break
            
        else:
            print("❌ Opción no válida")


def main():
    """Función principal - modo automático"""
    print("🌧️ DESCARGADOR DE RADARES IDEAM - MODO AUTOMÁTICO 🌧️")
    
    # Crear descargador
    downloader = IDEAMRadarDownloader()
    
    # Descargar últimos datos de Barrancabermeja (más cercano a Medellín)
    print("\n📡 Descargando datos del Radar Barrancabermeja (más cercano a Medellín)...")
    archivos = downloader.descargar_ultimos_datos(
        radar='Barrancabermeja',
        dias=2,
        max_archivos=50
    )
    
    # Generar inventario
    if archivos:
        print("\n📊 Generando inventario...")
        inventario = downloader.generar_inventario('Barrancabermeja')
        
        print("\n" + "="*80)
        print("✅ DESCARGA COMPLETADA")
        print("="*80)
        print(f"Archivos descargados: {len(archivos)}")
        print(f"Directorio: {downloader.base_dir / 'Barrancabermeja'}")
        print(f"Logs: logs/ideam/")
    else:
        print("\n⚠️ No se descargaron archivos. Verifique:")
        print("  • Que los datos estén disponibles para las fechas solicitadas")
        print("  • Los datos IDEAM tienen 24 horas de retraso")
        print("  • Intente con fechas de hace 2-3 días")


if __name__ == "__main__":
    # Modo interactivo por defecto
    menu_interactivo()
    # main()  # Descomentar para modo automático