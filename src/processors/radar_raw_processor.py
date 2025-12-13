"""
Procesador de archivos RAW de radares IDEAM
Lee y procesa datos en formato IRIS/Sigmet
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
import struct
import gzip
import logging

logger = logging.getLogger(__name__)

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class RadarRawProcessor:
    """Procesador de archivos RAW de radar meteorológico"""
    
    def __init__(self, data_dir="data/Radar_IDEAM"):
        self.data_dir = Path(data_dir)
        
        # Productos de radar disponibles
        self.productos = {
            'dBZ': {'nombre': 'Reflectividad', 'unidad': 'dBZ', 'cmap': 'jet'},
            'VEL': {'nombre': 'Velocidad Radial', 'unidad': 'm/s', 'cmap': 'RdBu_r'},
            'WIDTH': {'nombre': 'Ancho Espectral', 'unidad': 'm/s', 'cmap': 'viridis'},
            'ZDR': {'nombre': 'Reflectividad Diferencial', 'unidad': 'dB', 'cmap': 'RdYlGn'},
            'RHOHV': {'nombre': 'Coeficiente de Correlación', 'unidad': '', 'cmap': 'plasma'},
            'KDP': {'nombre': 'Fase Diferencial Específica', 'unidad': '°/km', 'cmap': 'coolwarm'}
        }
        
        logger.info(f"RadarRawProcessor inicializado para: {self.data_dir}")
    
    def listar_archivos_raw(self, radar=None):
        """Lista todos los archivos RAW disponibles"""
        archivos = []
        
        if radar:
            radar_dirs = [self.data_dir / radar]
        else:
            radar_dirs = [d for d in self.data_dir.iterdir() if d.is_dir()]
        
        for radar_dir in radar_dirs:
            if not radar_dir.exists():
                continue
                
            for fecha_dir in radar_dir.iterdir():
                if fecha_dir.is_dir():
                    for archivo in fecha_dir.iterdir():
                        if archivo.suffix.upper() in ['.RAW', '.GZ', ''] and archivo.is_file():
                            archivos.append({
                                'radar': radar_dir.name,
                                'fecha': fecha_dir.name,
                                'archivo': archivo.name,
                                'ruta': archivo,
                                'tamaño_mb': archivo.stat().st_size / (1024 * 1024)
                            })
        
        return pd.DataFrame(archivos)
    
    def leer_archivo_raw(self, ruta_archivo):
        """
        Lee un archivo RAW de radar
        Intenta diferentes métodos de lectura
        """
        ruta = Path(ruta_archivo)
        
        if not ruta.exists():
            logger.error(f"Archivo no encontrado: {ruta}")
            return None
        
        logger.info(f"Leyendo archivo: {ruta.name}")
        
        try:
            # Verificar si está comprimido
            if ruta.suffix == '.gz':
                with gzip.open(ruta, 'rb') as f:
                    datos = f.read()
            else:
                with open(ruta, 'rb') as f:
                    datos = f.read()
            
            logger.info(f"Archivo leído exitosamente: {len(datos)} bytes")
            
            # Intentar parsear header básico
            metadata = self.extraer_metadata_basica(datos)
            
            return {
                'datos_raw': datos,
                'metadata': metadata,
                'ruta': ruta,
                'tamaño': len(datos)
            }
            
        except Exception as e:
            logger.error(f"Error leyendo archivo: {e}")
            return None
    
    def extraer_metadata_basica(self, datos):
        """
        Extrae metadata básica del archivo RAW
        Formato IRIS tiene estructura específica
        """
        metadata = {
            'formato': 'Desconocido',
            'tamaño_bytes': len(datos),
            'timestamp': None,
            'radar': None
        }
        
        try:
            # Los primeros bytes suelen contener información del formato
            # Formato IRIS típicamente empieza con identificadores específicos
            
            # Buscar patrones comunes en nombres de archivo
            # Ejemplo: BAR241211010000.RAW
            # Donde: BAR = radar, 241211 = YYMMDD, 010000 = HHMMSS
            
            header_bytes = datos[:100]
            
            # Intentar detectar timestamp en los primeros bytes
            # (esto depende del formato específico IRIS/Sigmet)
            
            metadata['formato'] = 'IRIS/Sigmet (tentativo)'
            metadata['header_sample'] = header_bytes.hex()[:50]
            
        except Exception as e:
            logger.debug(f"Error extrayendo metadata: {e}")
        
        return metadata
    
    def parsear_nombre_archivo(self, nombre_archivo):
        """
        Parsea el nombre del archivo para extraer información
        Formato típico: PREFIJOYYMMDDHHMMSS.RAW[.gz]
        """
        info = {
            'prefijo': None,
            'fecha': None,
            'hora': None,
            'timestamp': None
        }
        
        try:
            # Remover extensiones
            nombre = nombre_archivo.replace('.gz', '').replace('.RAW', '').replace('.raw', '')
            
            # Formato esperado: PREFIJO + YYMMDD + HHMMSS
            if len(nombre) >= 15:
                prefijo = nombre[:3]  # Primeros 3 caracteres (BAR, GUA, etc.)
                fecha_str = nombre[3:9]  # YYMMDD
                hora_str = nombre[9:15]  # HHMMSS
                
                # Parsear fecha
                año = 2000 + int(fecha_str[:2])
                mes = int(fecha_str[2:4])
                dia = int(fecha_str[4:6])
                
                hora = int(hora_str[:2])
                minuto = int(hora_str[2:4])
                segundo = int(hora_str[4:6])
                
                timestamp = datetime(año, mes, dia, hora, minuto, segundo)
                
                info['prefijo'] = prefijo
                info['fecha'] = f"{año}-{mes:02d}-{dia:02d}"
                info['hora'] = f"{hora:02d}:{minuto:02d}:{segundo:02d}"
                info['timestamp'] = timestamp
                
        except Exception as e:
            logger.debug(f"Error parseando nombre: {e}")
        
        return info
    
    def analizar_estructura(self, archivo_raw):
        """Analiza la estructura básica del archivo RAW"""
        datos = archivo_raw['datos_raw']
        
        analisis = {
            'tamaño_total': len(datos),
            'primeros_bytes': datos[:50].hex(),
            'patron_detectado': None,
            'bloques_posibles': []
        }
        
        # Buscar patrones comunes en archivos de radar
        # Los archivos IRIS suelen tener estructuras repetitivas
        
        # Analizar cada 512 bytes (tamaño común de bloques)
        tamaño_bloque = 512
        num_bloques = len(datos) // tamaño_bloque
        
        analisis['bloques_detectados'] = num_bloques
        analisis['tamaño_bloque_estimado'] = tamaño_bloque
        
        return analisis
    
    def extraer_reflectividad_simple(self, archivo_raw, max_intentos=10):
        """
        Intenta extraer datos de reflectividad de forma simple
        Busca patrones típicos de datos de radar
        """
        datos = archivo_raw['datos_raw']
        
        # Los datos de reflectividad típicamente están en rangos específicos
        # Valores típicos: -32 a 95 dBZ
        
        reflectividad = []
        
        try:
            # Intentar leer como valores de 8 bits o 16 bits
            for offset in range(0, min(len(datos), 10000), 100):
                try:
                    # Leer como unsigned byte
                    valor = struct.unpack('B', datos[offset:offset+1])[0]
                    
                    # Convertir a dBZ (factor de escala típico)
                    dbz = (valor - 32) / 2.0  # Ejemplo de conversión común
                    
                    if -32 <= dbz <= 95:  # Rango válido
                        reflectividad.append({
                            'offset': offset,
                            'valor_raw': valor,
                            'dbz': dbz
                        })
                        
                        if len(reflectividad) >= max_intentos:
                            break
                            
                except:
                    continue
            
            if reflectividad:
                logger.info(f"Extraídos {len(reflectividad)} valores de reflectividad")
                return pd.DataFrame(reflectividad)
            else:
                logger.warning("No se pudieron extraer valores de reflectividad")
                return None
                
        except Exception as e:
            logger.error(f"Error extrayendo reflectividad: {e}")
            return None
    
    def generar_reporte_archivo(self, ruta_archivo):
        """Genera un reporte completo de un archivo RAW"""
        archivo_raw = self.leer_archivo_raw(ruta_archivo)
        
        if not archivo_raw:
            return None
        
        # Parsear nombre
        info_nombre = self.parsear_nombre_archivo(Path(ruta_archivo).name)
        
        # Analizar estructura
        estructura = self.analizar_estructura(archivo_raw)
        
        # Intentar extraer datos
        reflectividad = self.extraer_reflectividad_simple(archivo_raw)
        
        reporte = {
            'archivo': Path(ruta_archivo).name,
            'ruta': str(ruta_archivo),
            'tamaño_mb': archivo_raw['tamaño'] / (1024 * 1024),
            'info_nombre': info_nombre,
            'metadata': archivo_raw['metadata'],
            'estructura': estructura,
            'reflectividad_extraida': reflectividad is not None,
            'num_valores_reflectividad': len(reflectividad) if reflectividad is not None else 0
        }
        
        return reporte
    
    def procesar_lote(self, radar=None, limite=10):
        """Procesa un lote de archivos RAW"""
        archivos = self.listar_archivos_raw(radar)
        
        if archivos.empty:
            logger.warning("No se encontraron archivos RAW")
            return None
        
        logger.info(f"Procesando {min(len(archivos), limite)} archivos...")
        
        reportes = []
        
        for idx, row in archivos.head(limite).iterrows():
            logger.info(f"Procesando archivo {idx+1}/{min(len(archivos), limite)}: {row['archivo']}")
            
            reporte = self.generar_reporte_archivo(row['ruta'])
            
            if reporte:
                reportes.append(reporte)
        
        return pd.DataFrame(reportes)


class RadarVisualizador:
    """Visualizador de datos de radar"""
    
    def __init__(self):
        self.colormaps = {
            'reflectividad': 'jet',
            'velocidad': 'RdBu_r',
            'precipitacion': 'Blues'
        }
    
    def crear_ppi_simple(self, datos, titulo="Radar PPI"):
        """
        Crea visualización PPI (Plan Position Indicator) simple
        """
        if datos is None or len(datos) == 0:
            logger.warning("No hay datos para visualizar")
            return None
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        # Crear visualización polar simple
        # (requiere datos en formato específico)
        
        ax.set_title(titulo)
        
        return fig
    
    def visualizar_reporte(self, reporte):
        """Visualiza el reporte de un archivo"""
        if not reporte:
            return None
        
        print("\n" + "="*80)
        print(f"REPORTE DE ARCHIVO RAW: {reporte['archivo']}")
        print("="*80)
        
        print(f"\n📁 Información del Archivo:")
        print(f"   Tamaño: {reporte['tamaño_mb']:.2f} MB")
        print(f"   Ruta: {reporte['ruta']}")
        
        if reporte['info_nombre']['timestamp']:
            print(f"\n📅 Información Temporal:")
            print(f"   Fecha: {reporte['info_nombre']['fecha']}")
            print(f"   Hora: {reporte['info_nombre']['hora']}")
            print(f"   Prefijo: {reporte['info_nombre']['prefijo']}")
        
        print(f"\n🔍 Estructura:")
        print(f"   Tamaño total: {reporte['estructura']['tamaño_total']:,} bytes")
        print(f"   Bloques detectados: {reporte['estructura']['bloques_detectados']}")
        
        if reporte['reflectividad_extraida']:
            print(f"\n📊 Datos Extraídos:")
            print(f"   Valores de reflectividad: {reporte['num_valores_reflectividad']}")
        else:
            print(f"\n⚠️  No se pudieron extraer datos de reflectividad")
        
        print("\n" + "="*80)


def menu_analisis():
    """Menú interactivo para análisis de archivos RAW"""
    processor = RadarRawProcessor()
    visualizador = RadarVisualizador()
    
    while True:
        print("\n" + "="*80)
        print("🔬 ANÁLISIS DE ARCHIVOS RAW DE RADAR")
        print("="*80)
        
        print("\n1. Listar archivos RAW disponibles")
        print("2. Analizar un archivo específico")
        print("3. Procesar lote de archivos")
        print("4. Extraer información temporal")
        print("5. Generar reporte completo")
        print("6. Salir")
        
        opcion = input("\nSeleccione una opción: ").strip()
        
        if opcion == '1':
            print("\n📂 Listando archivos RAW...")
            archivos = processor.listar_archivos_raw()
            
            if archivos.empty:
                print("⚠️  No se encontraron archivos RAW")
                print("💡 Descargue archivos primero con: python ideam_radar_downloader.py")
            else:
                print(f"\n✅ Encontrados {len(archivos)} archivos:")
                print(archivos[['radar', 'fecha', 'archivo', 'tamaño_mb']].to_string(index=False))
            
            input("\nPresione Enter para continuar...")
        
        elif opcion == '2':
            archivos = processor.listar_archivos_raw()
            
            if archivos.empty:
                print("⚠️  No hay archivos disponibles")
            else:
                print("\n📂 Archivos disponibles:")
                for idx, row in archivos.head(10).iterrows():
                    print(f"{idx}. {row['radar']}/{row['fecha']}/{row['archivo']}")
                
                try:
                    idx = int(input("\nSeleccione número de archivo: "))
                    if 0 <= idx < len(archivos):
                        ruta = archivos.iloc[idx]['ruta']
                        print(f"\n🔍 Analizando: {archivos.iloc[idx]['archivo']}")
                        
                        reporte = processor.generar_reporte_archivo(ruta)
                        visualizador.visualizar_reporte(reporte)
                    else:
                        print("❌ Índice inválido")
                except ValueError:
                    print("❌ Entrada inválida")
            
            input("\nPresione Enter para continuar...")
        
        elif opcion == '3':
            radar = input("Radar (Enter para todos): ").strip() or None
            limite = input("Número de archivos a procesar (default 5): ").strip()
            limite = int(limite) if limite.isdigit() else 5
            
            print(f"\n⏳ Procesando {limite} archivos...")
            reportes = processor.procesar_lote(radar, limite)
            
            if reportes is not None:
                print(f"\n✅ Procesados {len(reportes)} archivos")
                
                # Guardar reportes
                output_dir = Path("analisis")
                output_dir.mkdir(exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = output_dir / f"reportes_radar_{timestamp}.csv"
                
                reportes.to_csv(output_file, index=False)
                print(f"💾 Reportes guardados en: {output_file}")
            
            input("\nPresione Enter para continuar...")
        
        elif opcion == '4':
            archivos = processor.listar_archivos_raw()
            
            if not archivos.empty:
                print("\n📅 Información temporal de archivos:")
                
                for idx, row in archivos.head(20).iterrows():
                    info = processor.parsear_nombre_archivo(row['archivo'])
                    if info['timestamp']:
                        print(f"   {row['archivo']}: {info['timestamp']}")
            else:
                print("⚠️  No hay archivos disponibles")
            
            input("\nPresione Enter para continuar...")
        
        elif opcion == '5':
            archivos = processor.listar_archivos_raw()
            
            if not archivos.empty:
                print(f"\n📊 REPORTE GENERAL")
                print("="*80)
                print(f"Total de archivos RAW: {len(archivos)}")
                print(f"Espacio total: {archivos['tamaño_mb'].sum():.2f} MB")
                print(f"\nArchivos por radar:")
                print(archivos.groupby('radar').size().to_string())
                print(f"\nArchivos por fecha:")
                print(archivos.groupby('fecha').size().head(10).to_string())
            else:
                print("⚠️  No hay archivos disponibles")
            
            input("\nPresione Enter para continuar...")
        
        elif opcion == '6':
            print("\n👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción inválida")


def main():
    """Función principal"""
    print("🔬 PROCESADOR DE ARCHIVOS RAW DE RADAR IDEAM 🔬")
    menu_analisis()


if __name__ == "__main__":
    main()