"""
Script para descargar datos históricos de SIATA
Organiza los archivos en data/siata_historico según formato
"""

import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import pandas as pd
import io
from datetime import datetime
import time
from pathlib import Path
import logging

# Configuración de logging
log_dir = Path("logs/siata")
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'siata_download.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class SIATADownloader:
    """Clase para descargar datos históricos de SIATA"""
    
    def __init__(self, base_dir="data/siata_historico"):
        self.base_url = "https://www.siata.gov.co/operacional/Meteorologia/"
        self.base_dir = Path(base_dir)
        self.timeout = 30
        self.delay = 1  # Segundos entre peticiones para no sobrecargar el servidor
        
        # Extensiones de archivos de datos
        self.data_extensions = ['.txt', '.csv', '.xlsx', '.json', '.zip', '.xml', '.kmz', '.tgz', '.gz']
        
        # Crear directorio base
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
    def get_page_content(self, url):
        """Obtiene el contenido HTML de una URL"""
        try:
            logger.info(f"Consultando: {url}")
            response = requests.get(url, allow_redirects=True, timeout=self.timeout)
            response.raise_for_status()
            time.sleep(self.delay)  # Respetar el servidor
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al consultar {url}: {e}")
            return None
    
    def extract_links(self, soup, base_url):
        """Extrae y categoriza enlaces de una página"""
        data_files = []
        subdirectories = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_href = urljoin(base_url, href)
            parsed_url = urlparse(absolute_href)
            path = parsed_url.path.lower()
            
            # Evitar enlaces al directorio padre y actual
            if path.endswith('../') or absolute_href == base_url:
                continue
            
            # Clasificar enlaces
            if path.endswith('/'):
                subdirectories.append(absolute_href)
            elif any(path.endswith(ext) for ext in self.data_extensions):
                data_files.append(absolute_href)
        
        return list(set(data_files)), list(set(subdirectories))
    
    def get_category_from_path(self, url):
        """Determina la categoría basándose en la ruta del archivo"""
        path = urlparse(url).path
        path_parts = [p for p in path.split('/') if p]
        
        # Buscar categorías conocidas en la ruta
        categories = {
            'AcumPrecipitacion': 'precipitacion_acumulada',
            'Precipitacion': 'precipitacion',
            'Temperatura': 'temperatura',
            'Humedad': 'humedad',
            'Viento': 'viento',
            'PresionAtmosferica': 'presion',
            'RadiacionSolar': 'radiacion',
            'CalidadAire': 'calidad_aire',
            'NivelRio': 'nivel_rio'
        }
        
        for key, value in categories.items():
            if key.lower() in path.lower():
                return value
        
        # Si no se encuentra categoría, usar el directorio padre
        if len(path_parts) >= 2:
            return path_parts[-2].lower()
        
        return 'otros'
    
    def download_file(self, url, category):
        """Descarga un archivo y lo guarda en la carpeta correspondiente"""
        try:
            response = self.get_page_content(url)
            if not response:
                return False
            
            # Crear directorio para la categoría
            category_dir = self.base_dir / category
            category_dir.mkdir(parents=True, exist_ok=True)
            
            # Obtener nombre del archivo
            filename = os.path.basename(urlparse(url).path)
            filepath = category_dir / filename
            
            # Evitar descargar si ya existe
            if filepath.exists():
                logger.info(f"Archivo ya existe, omitiendo: {filename}")
                return True
            
            # Guardar archivo
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Descargado: {filename} -> {category}/")
            
            # Intentar parsear y guardar resumen si es archivo de texto
            if filename.endswith('.txt') or filename.endswith('.csv'):
                self.save_data_summary(filepath, response.text)
            
            return True
            
        except Exception as e:
            logger.error(f"Error descargando {url}: {e}")
            return False
    
    def save_data_summary(self, filepath, content):
        """Guarda un resumen del contenido del archivo"""
        try:
            # Intentar leer como CSV
            df = pd.read_csv(io.StringIO(content), sep=',', skiprows=1, 
                           on_bad_lines='skip', nrows=10)
            
            # Guardar resumen
            summary_path = filepath.parent / f"{filepath.stem}_summary.txt"
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(f"Resumen de {filepath.name}\n")
                f.write(f"Generado: {datetime.now()}\n")
                f.write("="*50 + "\n\n")
                f.write("Primeras 10 filas:\n")
                f.write(df.to_string())
                f.write("\n\nInformación del DataFrame:\n")
                f.write(str(df.info()))
            
            logger.info(f"Resumen guardado: {summary_path.name}")
            
        except Exception as e:
            logger.debug(f"No se pudo crear resumen para {filepath.name}: {e}")
    
    def explore_directory(self, url, max_depth=3, current_depth=0):
        """Explora recursivamente los directorios de SIATA"""
        if current_depth >= max_depth:
            return
        
        logger.info(f"Explorando directorio (profundidad {current_depth}): {url}")
        
        response = self.get_page_content(url)
        if not response:
            return
        
        soup = BeautifulSoup(response.text, 'html.parser')
        data_files, subdirectories = self.extract_links(soup, url)
        
        # Descargar archivos de datos
        logger.info(f"Encontrados {len(data_files)} archivos de datos")
        for file_url in data_files:
            category = self.get_category_from_path(file_url)
            self.download_file(file_url, category)
        
        # Explorar subdirectorios
        logger.info(f"Encontrados {len(subdirectories)} subdirectorios")
        for subdir_url in subdirectories:
            self.explore_directory(subdir_url, max_depth, current_depth + 1)
    
    def download_all(self, max_depth=3):
        """Inicia la descarga de todos los datos históricos"""
        logger.info("="*60)
        logger.info("Iniciando descarga de datos históricos de SIATA")
        logger.info(f"Directorio de destino: {self.base_dir}")
        logger.info("="*60)
        
        start_time = datetime.now()
        
        # Explorar desde la raíz de meteorología
        self.explore_directory(self.base_url, max_depth=max_depth)
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info("="*60)
        logger.info("Descarga completada")
        logger.info(f"Tiempo total: {duration}")
        logger.info(f"Archivos guardados en: {self.base_dir}")
        logger.info("="*60)
    
    def generate_inventory(self):
        """Genera un inventario de todos los archivos descargados"""
        inventory = []
        
        for category_dir in self.base_dir.iterdir():
            if category_dir.is_dir():
                for file in category_dir.iterdir():
                    if not file.name.endswith('_summary.txt'):
                        inventory.append({
                            'categoria': category_dir.name,
                            'archivo': file.name,
                            'ruta': str(file),
                            'tamaño_kb': file.stat().st_size / 1024,
                            'fecha_descarga': datetime.fromtimestamp(file.stat().st_mtime)
                        })
        
        df_inventory = pd.DataFrame(inventory)
        inventory_path = self.base_dir / 'inventario.csv'
        df_inventory.to_csv(inventory_path, index=False)
        
        logger.info(f"Inventario generado: {inventory_path}")
        logger.info(f"Total de archivos: {len(inventory)}")
        
        return df_inventory


def main():
    """Función principal"""
    # Crear instancia del descargador
    downloader = SIATADownloader(base_dir="data/siata_historico")
    
    # Descargar todos los datos (max_depth=3 para explorar hasta 3 niveles)
    downloader.download_all(max_depth=3)
    
    # Generar inventario
    inventory = downloader.generate_inventory()
    
    print("\n" + "="*60)
    print("RESUMEN DE DESCARGA")
    print("="*60)
    print(f"\nArchivos descargados por categoría:")
    print(inventory.groupby('categoria')['archivo'].count().to_string())
    print(f"\nEspacio total utilizado: {inventory['tamaño_kb'].sum():.2f} KB")


if __name__ == "__main__":
    main()