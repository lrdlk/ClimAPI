"""
Procesador Avanzado de Archivos de Radar usando PyART
Requiere: pip install arm-pyart
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Intentar importar PyART
try:
    import pyart
    PYART_AVAILABLE = True
    logger.info("✅ PyART disponible")
except ImportError:
    PYART_AVAILABLE = False
    logger.warning("⚠️  PyART no disponible. Instale con: pip install arm-pyart")


class RadarAdvancedProcessor:
    """Procesador avanzado usando PyART para archivos de radar"""
    
    def __init__(self, data_dir="data/Radar_IDEAM"):
        self.data_dir = Path(data_dir)
        
        if not PYART_AVAILABLE:
            logger.error("PyART no está instalado. Funcionalidad limitada.")
            self.pyart_enabled = False
        else:
            self.pyart_enabled = True
        
        # Productos y sus configuraciones
        self.productos_config = {
            'reflectivity': {
                'nombre': 'Reflectividad',
                'unidad': 'dBZ',
                'vmin': -20,
                'vmax': 70,
                'cmap': 'pyart_NWSRef'
            },
            'velocity': {
                'nombre': 'Velocidad Radial',
                'unidad': 'm/s',
                'vmin': -30,
                'vmax': 30,
                'cmap': 'pyart_NWSVel'
            },
            'spectrum_width': {
                'nombre': 'Ancho Espectral',
                'unidad': 'm/s',
                'vmin': 0,
                'vmax': 10,
                'cmap': 'pyart_NWS_SPW'
            }
        }
    
    def leer_con_pyart(self, ruta_archivo):
        """Lee archivo de radar usando PyART"""
        if not self.pyart_enabled:
            logger.error("PyART no está disponible")
            return None
        
        try:
            logger.info(f"Leyendo con PyART: {ruta_archivo}")
            
            # PyART puede leer varios formatos
            radar = pyart.io.read(str(ruta_archivo))
            
            logger.info(f"✅ Archivo leído exitosamente")
            logger.info(f"   Sweeps: {radar.nsweeps}")
            logger.info(f"   Campos disponibles: {list(radar.fields.keys())}")
            
            return radar
            
        except Exception as e:
            logger.error(f"Error leyendo archivo con PyART: {e}")
            return None
    
    def extraer_informacion(self, radar):
        """Extrae información del objeto radar de PyART"""
        if radar is None:
            return None
        
        info = {
            'metadata': {
                'nombre_instrumento': radar.metadata.get('instrument_name', 'N/A'),
                'nombre_sitio': radar.metadata.get('site_name', 'N/A'),
                'latitud': radar.latitude['data'][0] if 'data' in radar.latitude else None,
                'longitud': radar.longitude['data'][0] if 'data' in radar.longitude else None,
                'altitud': radar.altitude['data'][0] if 'data' in radar.altitude else None,
            },
            'estructura': {
                'numero_sweeps': radar.nsweeps,
                'numero_rayos': radar.nrays,
                'numero_gates': radar.ngates,
            },
            'campos_disponibles': list(radar.fields.keys()),
            'tiempo': {
                'tiempo_inicio': datetime.utcfromtimestamp(radar.time['data'][0]),
                'tiempo_fin': datetime.utcfromtimestamp(radar.time['data'][-1]),
            }
        }
        
        return info
    
    def generar_ppi(self, radar, campo='reflectivity', sweep=0, output_path=None):
        """
        Genera visualización PPI (Plan Position Indicator)
        """
        if not self.pyart_enabled or radar is None:
            logger.error("No se puede generar PPI")
            return None
        
        try:
            # Obtener configuración del campo
            config = self.productos_config.get(campo, {
                'nombre': campo,
                'unidad': '',
                'vmin': None,
                'vmax': None,
                'cmap': 'viridis'
            })
            
            # Crear display
            display = pyart.graph.RadarDisplay(radar)
            
            fig = plt.figure(figsize=(12, 10))
            
            # Plotear PPI
            display.plot_ppi(
                campo,
                sweep=sweep,
                vmin=config['vmin'],
                vmax=config['vmax'],
                cmap=config['cmap'],
                title=f"{config['nombre']} - Sweep {sweep}"
            )
            
            # Agregar anillos de rango
            display.plot_range_rings([50, 100, 150, 200])
            
            # Agregar líneas de azimuth
            display.plot_cross_hair(5)
            
            plt.tight_layout()
            
            # Guardar si se especifica ruta
            if output_path:
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                plt.savefig(output_path, dpi=150, bbox_inches='tight')
                logger.info(f"PPI guardado en: {output_path}")
            
            return fig
            
        except Exception as e:
            logger.error(f"Error generando PPI: {e}")
            return None
    
    def generar_cappi(self, radar, campo='reflectivity', altura=3000, output_path=None):
        """
        Genera CAPPI (Constant Altitude PPI)
        """
        if not self.pyart_enabled or radar is None:
            return None
        
        try:
            # Crear grid
            grid = pyart.map.grid_from_radars(
                radar,
                grid_shape=(20, 241, 241),
                grid_limits=((0, 20000), (-150000, 150000), (-150000, 150000))
            )
            
            config = self.productos_config.get(campo, {
                'nombre': campo,
                'vmin': None,
                'vmax': None,
                'cmap': 'viridis'
            })
            
            # Encontrar índice de altura más cercano
            alturas = grid.z['data']
            idx_altura = np.argmin(np.abs(alturas - altura))
            
            # Extraer datos en esa altura
            datos = grid.fields[campo]['data'][idx_altura, :, :]
            
            # Plotear
            fig, ax = plt.subplots(figsize=(12, 10))
            
            im = ax.pcolormesh(
                grid.x['data'][0] / 1000,  # Convertir a km
                grid.y['data'][0] / 1000,
                datos,
                vmin=config['vmin'],
                vmax=config['vmax'],
                cmap=config['cmap']
            )
            
            plt.colorbar(im, ax=ax, label=config['nombre'])
            ax.set_xlabel('Distancia Este-Oeste (km)')
            ax.set_ylabel('Distancia Norte-Sur (km)')
            ax.set_title(f"CAPPI - {config['nombre']} a {altura}m")
            ax.set_aspect('equal')
            
            if output_path:
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                plt.savefig(output_path, dpi=150, bbox_inches='tight')
                logger.info(f"CAPPI guardado en: {output_path}")
            
            return fig
            
        except Exception as e:
            logger.error(f"Error generando CAPPI: {e}")
            return None
    
    def calcular_precipitacion(self, radar, campo='reflectivity'):
        """
        Calcula tasa de precipitación usando relación Z-R
        Z = aR^b, típicamente Z = 200R^1.6
        """
        if not self.pyart_enabled or radar is None:
            return None
        
        try:
            # Obtener datos de reflectividad
            if campo not in radar.fields:
                logger.error(f"Campo {campo} no disponible")
                return None
            
            z_data = radar.fields[campo]['data']
            
            # Convertir dBZ a Z (lineal)
            z_linear = 10 ** (z_data / 10.0)
            
            # Aplicar relación Z-R: Z = 200R^1.6
            a = 200
            b = 1.6
            
            # R = (Z/a)^(1/b)
            rain_rate = (z_linear / a) ** (1 / b)
            
            # Enmascarar valores inválidos
            rain_rate = np.ma.masked_where(z_data.mask, rain_rate)
            
            # Crear campo de precipitación
            rain_dict = {
                'data': rain_rate,
                'units': 'mm/h',
                'long_name': 'Tasa de precipitación',
                'standard_name': 'rainfall_rate'
            }
            
            # Agregar al radar
            radar.add_field('rainfall_rate', rain_dict, replace_existing=True)
            
            logger.info("✅ Tasa de precipitación calculada")
            
            return rain_rate
            
        except Exception as e:
            logger.error(f"Error calculando precipitación: {e}")
            return None
    
    def exportar_a_netcdf(self, radar, output_path):
        """Exporta datos de radar a formato NetCDF"""
        if not self.pyart_enabled or radar is None:
            return False
        
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            pyart.io.write_cfradial(str(output_path), radar)
            logger.info(f"✅ Datos exportados a NetCDF: {output_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error exportando a NetCDF: {e}")
            return False
    
    def procesar_archivo_completo(self, ruta_archivo, output_dir=None):
        """Procesa un archivo completo y genera todos los productos"""
        logger.info(f"🔄 Procesando archivo completo: {ruta_archivo}")
        
        # Leer archivo
        radar = self.leer_con_pyart(ruta_archivo)
        
        if radar is None:
            logger.error("No se pudo leer el archivo")
            return None
        
        # Extraer información
        info = self.extraer_informacion(radar)
        
        # Crear directorio de salida
        if output_dir is None:
            output_dir = Path("productos_radar") / Path(ruta_archivo).stem
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        resultados = {
            'archivo': ruta_archivo,
            'info': info,
            'productos_generados': []
        }
        
        # Generar productos para cada campo disponible
        for campo in radar.fields.keys():
            try:
                # PPI para sweep 0
                fig_ppi = self.generar_ppi(
                    radar,
                    campo=campo,
                    sweep=0,
                    output_path=output_dir / f"ppi_{campo}.png"
                )
                
                if fig_ppi:
                    plt.close(fig_ppi)
                    resultados['productos_generados'].append(f"ppi_{campo}.png")
                
            except Exception as e:
                logger.error(f"Error generando PPI para {campo}: {e}")
        
        # Calcular precipitación si hay reflectividad
        if 'reflectivity' in radar.fields:
            rain_rate = self.calcular_precipitacion(radar)
            
            if rain_rate is not None:
                # Generar PPI de precipitación
                fig_rain = self.generar_ppi(
                    radar,
                    campo='rainfall_rate',
                    sweep=0,
                    output_path=output_dir / "ppi_rainfall.png"
                )
                
                if fig_rain:
                    plt.close(fig_rain)
                    resultados['productos_generados'].append("ppi_rainfall.png")
        
        # Exportar a NetCDF
        netcdf_path = output_dir / f"{Path(ruta_archivo).stem}.nc"
        if self.exportar_a_netcdf(radar, netcdf_path):
            resultados['productos_generados'].append(str(netcdf_path.name))
        
        # Guardar información en JSON
        import json
        info_path = output_dir / "info.json"
        with open(info_path, 'w') as f:
            # Convertir datetime a string para JSON
            info_serializable = info.copy()
            if 'tiempo' in info_serializable:
                info_serializable['tiempo'] = {
                    'tiempo_inicio': str(info['tiempo']['tiempo_inicio']),
                    'tiempo_fin': str(info['tiempo']['tiempo_fin'])
                }
            json.dump(info_serializable, f, indent=2)
        
        logger.info(f"✅ Procesamiento completo. Productos en: {output_dir}")
        
        return resultados


def menu_avanzado():
    """Menú interactivo para procesamiento avanzado"""
    if not PYART_AVAILABLE:
        print("\n" + "="*80)
        print("⚠️  PyART NO ESTÁ INSTALADO")
        print("="*80)
        print("\nPara usar el procesador avanzado, instale PyART:")
        print("  pip install arm-pyart")
        print("\nPresione Enter para salir...")
        input()
        return
    
    processor = RadarAdvancedProcessor()
    
    while True:
        print("\n" + "="*80)
        print("🔬 PROCESADOR AVANZADO DE RADAR CON PYART")
        print("="*80)
        
        print("\n1. Listar archivos RAW disponibles")
        print("2. Analizar archivo con PyART")
        print("3. Generar PPI de reflectividad")
        print("4. Generar CAPPI")
        print("5. Calcular tasa de precipitación")
        print("6. Procesar archivo completo (todos los productos)")
        print("7. Exportar a NetCDF")
        print("8. Salir")
        
        opcion = input("\nSeleccione una opción: ").strip()
        
        if opcion == '1':
            from radar_raw_processor import RadarRawProcessor
            proc = RadarRawProcessor()
            archivos = proc.listar_archivos_raw()
            
            if archivos.empty:
                print("⚠️  No hay archivos disponibles")
            else:
                print(f"\n✅ Encontrados {len(archivos)} archivos:")
                print(archivos[['radar', 'fecha', 'archivo']].to_string(index=False))
            
            input("\nPresione Enter para continuar...")
        
        elif opcion == '2':
            from radar_raw_processor import RadarRawProcessor
            proc = RadarRawProcessor()
            archivos = proc.listar_archivos_raw()
            
            if archivos.empty:
                print("⚠️  No hay archivos disponibles")
            else:
                print("\n📂 Archivos disponibles:")
                for idx, row in archivos.head(10).iterrows():
                    print(f"{idx}. {row['archivo']}")
                
                try:
                    idx = int(input("\nSeleccione archivo: "))
                    ruta = archivos.iloc[idx]['ruta']
                    
                    radar = processor.leer_con_pyart(ruta)
                    
                    if radar:
                        info = processor.extraer_informacion(radar)
                        
                        print("\n" + "="*80)
                        print("INFORMACIÓN DEL RADAR")
                        print("="*80)
                        print(f"\n📍 Metadata:")
                        for k, v in info['metadata'].items():
                            print(f"   {k}: {v}")
                        print(f"\n📊 Estructura:")
                        for k, v in info['estructura'].items():
                            print(f"   {k}: {v}")
                        print(f"\n🔧 Campos disponibles:")
                        for campo in info['campos_disponibles']:
                            print(f"   • {campo}")
                
                except (ValueError, IndexError):
                    print("❌ Selección inválida")
            
            input("\nPresione Enter para continuar...")
        
        elif opcion == '6':
            from radar_raw_processor import RadarRawProcessor
            proc = RadarRawProcessor()
            archivos = proc.listar_archivos_raw()
            
            if archivos.empty:
                print("⚠️  No hay archivos disponibles")
            else:
                print("\n📂 Archivos disponibles:")
                for idx, row in archivos.head(10).iterrows():
                    print(f"{idx}. {row['archivo']}")
                
                try:
                    idx = int(input("\nSeleccione archivo: "))
                    ruta = archivos.iloc[idx]['ruta']
                    
                    print("\n⏳ Procesando archivo completo...")
                    resultados = processor.procesar_archivo_completo(ruta)
                    
                    if resultados:
                        print(f"\n✅ Procesamiento completado")
                        print(f"📁 Productos generados: {len(resultados['productos_generados'])}")
                        for prod in resultados['productos_generados']:
                            print(f"   • {prod}")
                
                except (ValueError, IndexError):
                    print("❌ Selección inválida")
                except Exception as e:
                    print(f"❌ Error: {e}")
            
            input("\nPresione Enter para continuar...")
        
        elif opcion == '8':
            print("\n👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción no válida o no implementada")
            input("\nPresione Enter para continuar...")


def main():
    """Función principal"""
    print("🔬 PROCESADOR AVANZADO DE RADAR CON PYART 🔬")
    menu_avanzado()


if __name__ == "__main__":
    main()