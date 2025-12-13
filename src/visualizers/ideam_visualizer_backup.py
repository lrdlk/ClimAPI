"""
IDEAM Radar Data Visualizer & Processor - OPTIMIZADO
=====================================================

Procesa y visualiza datos de radar IDEAM con DataFrames trabajables y gráficas precisas.
Integración con PyART para análisis meteorológico avanzado.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
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

# Intentar importar PyART para procesamiento avanzado
try:
    import pyart
    PYART_AVAILABLE = True
    logger.info("✅ PyART disponible para análisis avanzado")
except ImportError:
    PYART_AVAILABLE = False
    logger.warning("⚠️  PyART no disponible. Funcionalidad limitada.")

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("viridis")


class IDEAMRadarVisualizer:
    """Procesador y visualizador de datos de radar IDEAM"""
    
    def __init__(self, data_dir="data/Radar_IDEAM"):
        self.data_dir = Path(data_dir)
        self.imagenes = []
        self.metadata = []
        
    def listar_radares(self):
        """Lista los radares disponibles"""
        if not self.data_dir.exists():
            print(f"❌ Directorio {self.data_dir} no existe")
            return []
        
        radares = [d.name for d in self.data_dir.iterdir() if d.is_dir()]
        
        print(f"\n📡 Radares disponibles: {len(radares)}")
        for radar in radares:
            print(f"  - {radar}")
        
        return radares
    
    def cargar_imagenes_radar(self, radar_name):
        """
        Carga imágenes de un radar específico
        
        Args:
            radar_name: Nombre del radar (ej: Barrancabermeja)
        """
        radar_path = self.data_dir / radar_name
        
        if not radar_path.exists():
            print(f"❌ Radar {radar_name} no encontrado")
            return None
        
        # Buscar imágenes
        image_files = list(radar_path.glob("*.png")) + list(radar_path.glob("*.jpg"))
        
        print(f"\n📡 Radar: {radar_name}")
        print(f"📂 Imágenes encontradas: {len(image_files)}")
        
        self.imagenes = []
        self.metadata = []
        
        for img_file in image_files:
            try:
                # Extraer timestamp del nombre del archivo si es posible
                timestamp = self._extraer_timestamp(img_file.name)
                
                self.imagenes.append(img_file)
                self.metadata.append({
                    'radar': radar_name,
                    'archivo': img_file.name,
                    'ruta': str(img_file),
                    'timestamp': timestamp,
                    'tamaño_bytes': img_file.stat().st_size
                })
                
            except Exception as e:
                print(f"⚠️ Error procesando {img_file.name}: {e}")
        
        if self.metadata:
            self.df_metadata = pd.DataFrame(self.metadata)
            print(f"✅ Cargadas {len(self.imagenes)} imágenes")
            return self.df_metadata
        
        return None
    
    def _extraer_timestamp(self, filename):
        """Intenta extraer timestamp del nombre del archivo"""
        try:
            # Formato común: YYYYMMDD_HHMM
            import re
            match = re.search(r'(\d{8})_(\d{4})', filename)
            if match:
                date_str = match.group(1)
                time_str = match.group(2)
                return datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M")
        except:
            pass
        
        # Si no se puede extraer, usar fecha de modificación
        return None
    
    def estadisticas_basicas(self):
        """Estadísticas de las imágenes de radar"""
        if not self.metadata:
            print("❌ Primero carga imágenes con cargar_imagenes_radar()")
            return
        
        print("\n" + "="*60)
        print("📊 ESTADÍSTICAS - IDEAM RADAR")
        print("="*60)
        
        print(f"\n📡 Radar: {self.metadata[0]['radar']}")
        print(f"📂 Total imágenes: {len(self.metadata)}")
        
        tamaños = [m['tamaño_bytes'] for m in self.metadata]
        print(f"\n💾 Tamaño de archivos:")
        print(f"  - Total: {sum(tamaños) / (1024*1024):.2f} MB")
        print(f"  - Promedio: {np.mean(tamaños) / 1024:.2f} KB")
        print(f"  - Máximo: {max(tamaños) / 1024:.2f} KB")
        print(f"  - Mínimo: {min(tamaños) / 1024:.2f} KB")
        
        # Timestamps si existen
        timestamps = [m['timestamp'] for m in self.metadata if m['timestamp']]
        if timestamps:
            print(f"\n📅 Rango temporal:")
            print(f"  - Desde: {min(timestamps)}")
            print(f"  - Hasta: {max(timestamps)}")
            print(f"  - Duración: {max(timestamps) - min(timestamps)}")
    
    def visualizar_galeria(self, max_images=9, save_path=None):
        """
        Crea una galería con las imágenes de radar
        
        Args:
            max_images: Número máximo de imágenes a mostrar
            save_path: Ruta para guardar la galería
        """
        if not self.imagenes:
            print("❌ No hay imágenes cargadas")
            return
        
        n_images = min(len(self.imagenes), max_images)
        cols = 3
        rows = (n_images + cols - 1) // cols
        
        fig, axes = plt.subplots(rows, cols, figsize=(15, 5*rows))
        if rows == 1 and cols == 1:
            axes = np.array([axes])
        axes = axes.flatten()
        
        fig.suptitle(f'Galería de Imágenes - Radar {self.metadata[0]["radar"]}', 
                     fontsize=16, fontweight='bold')
        
        for i in range(n_images):
            try:
                img = Image.open(self.imagenes[i])
                axes[i].imshow(img)
                axes[i].axis('off')
                
                # Título con timestamp si existe
                title = self.metadata[i]['archivo']
                if self.metadata[i]['timestamp']:
                    title = self.metadata[i]['timestamp'].strftime('%Y-%m-%d %H:%M')
                
                axes[i].set_title(title, fontsize=10)
                
            except Exception as e:
                axes[i].text(0.5, 0.5, f'Error: {e}', ha='center', va='center')
                axes[i].axis('off')
        
        # Ocultar ejes sobrantes
        for i in range(n_images, len(axes)):
            axes[i].axis('off')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=200, bbox_inches='tight')
            print(f"✅ Galería guardada en {save_path}")
        
        plt.show()
    
    def analisis_intensidad(self, num_samples=5):
        """
        Analiza la intensidad de píxeles en las imágenes
        
        Args:
            num_samples: Número de imágenes a analizar
        """
        if not self.imagenes:
            print("❌ No hay imágenes cargadas")
            return
        
        print("\n🔍 ANÁLISIS DE INTENSIDAD")
        print("="*60)
        
        intensidades = []
        
        for i, img_path in enumerate(self.imagenes[:num_samples]):
            try:
                img = Image.open(img_path).convert('L')  # Convertir a escala de grises
                img_array = np.array(img)
                
                intensidad_promedio = img_array.mean()
                intensidad_std = img_array.std()
                intensidad_max = img_array.max()
                
                intensidades.append({
                    'archivo': self.metadata[i]['archivo'],
                    'promedio': intensidad_promedio,
                    'std': intensidad_std,
                    'max': intensidad_max
                })
                
                print(f"\n📊 {self.metadata[i]['archivo']}")
                print(f"  - Intensidad promedio: {intensidad_promedio:.2f}")
                print(f"  - Desviación estándar: {intensidad_std:.2f}")
                print(f"  - Máximo: {intensidad_max}")
                
            except Exception as e:
                print(f"⚠️ Error en {img_path.name}: {e}")
        
        return pd.DataFrame(intensidades)
    
    def comparar_imagenes(self, indices=[0, 1], save_path=None):
        """
        Compara dos imágenes lado a lado
        
        Args:
            indices: Lista con los índices de las imágenes a comparar
            save_path: Ruta para guardar la comparación
        """
        if len(self.imagenes) < 2:
            print("❌ Se necesitan al menos 2 imágenes")
            return
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle('Comparación de Imágenes de Radar', fontsize=14, fontweight='bold')
        
        for i, idx in enumerate(indices[:2]):
            if idx < len(self.imagenes):
                try:
                    img = Image.open(self.imagenes[idx])
                    axes[i].imshow(img)
                    axes[i].axis('off')
                    
                    title = self.metadata[idx]['archivo']
                    if self.metadata[idx]['timestamp']:
                        title = self.metadata[idx]['timestamp'].strftime('%Y-%m-%d %H:%M')
                    
                    axes[i].set_title(title)
                    
                except Exception as e:
                    axes[i].text(0.5, 0.5, f'Error: {e}', ha='center', va='center')
                    axes[i].axis('off')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=200, bbox_inches='tight')
            print(f"✅ Comparación guardada en {save_path}")
        
        plt.show()
    
    def timeline_imagenes(self, save_path=None):
        """Genera línea de tiempo de imágenes disponibles"""
        if not self.metadata:
            print("❌ No hay imágenes cargadas")
            return
        
        timestamps = [(m['timestamp'], m['archivo']) for m in self.metadata if m['timestamp']]
        
        if not timestamps:
            print("⚠️ No hay timestamps disponibles")
            return
        
        timestamps.sort()
        
        plt.figure(figsize=(14, 6))
        
        dates = [t[0] for t in timestamps]
        y_pos = range(len(dates))
        
        plt.scatter(dates, y_pos, alpha=0.6, s=100, c='steelblue')
        
        plt.xlabel('Fecha y Hora')
        plt.ylabel('Índice de Imagen')
        plt.title(f'Timeline de Capturas - Radar {self.metadata[0]["radar"]}', 
                 fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3, axis='x')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ Timeline guardado en {save_path}")
        
        plt.show()
    
    def exportar_metadata(self):
        """Exporta metadata a CSV"""
        if not self.metadata:
            print("❌ No hay metadata para exportar")
            return
        
        output_path = Path("data/processed/ideam_radar_metadata.csv")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        df = pd.DataFrame(self.metadata)
        df.to_csv(output_path, index=False)
        print(f"✅ Metadata exportada a {output_path}")


def main():
    """Función principal"""
    print("📡 IDEAM RADAR VISUALIZER")
    print("="*60)
    
    visualizer = IDEAMRadarVisualizer()
    
    # Listar radares disponibles
    radares = visualizer.listar_radares()
    
    if radares:
        # Usar el primer radar disponible
        radar = radares[0]
        visualizer.cargar_imagenes_radar(radar)
        
        if visualizer.metadata:
            visualizer.estadisticas_basicas()
            visualizer.visualizar_galeria(save_path=f"data/images/ideam_galeria_{radar}.png")
            visualizer.analisis_intensidad()
            visualizer.timeline_imagenes(save_path=f"data/images/ideam_timeline_{radar}.png")
            visualizer.exportar_metadata()


if __name__ == "__main__":
    main()
