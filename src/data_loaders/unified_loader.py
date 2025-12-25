"""
Cargador unificado que integra todas las fuentes de datos
Orquesta: JSONLoader + FileLoader + Validación + Consolidación
"""

import pandas as pd
from pathlib import Path
from typing import Union, Optional
import logging
from datetime import datetime

from .json_loader import JSONDataLoader
from .file_loader import FileLoader

logger = logging.getLogger(__name__)


class UnifiedDataLoader:
    """
    Punto único de entrada para cargar, limpiar y consolidar datos climáticos
    
    Uso:
        loader = UnifiedDataLoader("data")
        df = loader.load_all(standardize=True, remove_nulls=True)
    """
    
    def __init__(self, data_dir: Union[str, Path] = "data"):
        """Inicializa con directorio de datos"""
        self.data_dir = Path(data_dir)
        self.metadata = {}
    
    def load_all(self, 
                 standardize: bool = True,
                 remove_nulls: bool = True,
                 resample_freq: Optional[str] = None) -> pd.DataFrame:
        """
        Carga TODOS los datos disponibles del directorio
        
        Args:
            standardize: Estandarizar nombres de columnas
            remove_nulls: Eliminar filas completamente nulas
            resample_freq: Frecuencia de resampleo (ej: 'H' para horario)
        
        Returns:
            DataFrame consolidado
        """
        all_data = []
        
        # 1. Cargar JSONs
        logger.info("Cargando archivos JSON...")
        json_files = list(self.data_dir.glob("consulta_completa_*.json"))
        
        if json_files:
            json_df = JSONDataLoader.load_from_directory(self.data_dir)
            if not json_df.empty:
                all_data.append(json_df)
                logger.info(f"✓ JSON: {len(json_df)} registros")
        
        # 2. Cargar CSVs/TXTs
        logger.info("Cargando archivos CSV/TXT...")
        csv_files = list(self.data_dir.glob("*.csv")) + list(self.data_dir.glob("*.txt"))
        csv_dict = FileLoader.load_directory(self.data_dir, "*.csv")
        csv_dict.update(FileLoader.load_directory(self.data_dir, "*.txt"))
        
        for name, df in csv_dict.items():
            all_data.append(df)
            logger.info(f"✓ {name}: {len(df)} registros")
        
        # 3. Consolidar
        if not all_data:
            logger.warning("No se encontraron datos")
            return pd.DataFrame()
        
        df = pd.concat(all_data, ignore_index=True, sort=False)
        logger.info(f"Datos consolidados: {len(df)} registros totales")
        
        # 4. Procesamiento
        if remove_nulls:
            initial_len = len(df)
            df = df.dropna(how='all', axis=0)  # Filas completamente nulas
            dropped = initial_len - len(df)
            if dropped > 0:
                logger.info(f"Eliminadas {dropped} filas nulas")
        
        if standardize:
            df = FileLoader.standardize_columns(df)
            logger.info("✓ Columnas estandarizadas")
        
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df = df.sort_values('timestamp')
            
            if resample_freq:
                logger.info(f"Resampleando a {resample_freq}...")
                numeric_cols = df.select_dtypes(include=['number']).columns
                df_resampled = df.set_index('timestamp').resample(resample_freq).agg({
                    col: 'mean' for col in numeric_cols
                })
                df = df_resampled.reset_index()
        
        self.metadata['loaded_at'] = datetime.now()
        self.metadata['total_records'] = len(df)
        self.metadata['columns'] = list(df.columns)
        
        return df
    
    def load_location(self, location: str) -> pd.DataFrame:
        """Carga datos de una ubicación específica"""
        json_df = JSONDataLoader.load_from_directory(self.data_dir)
        
        if 'location' in json_df.columns:
            return json_df[json_df['location'].str.contains(location, case=False, na=False)]
        
        return pd.DataFrame()
    
    def load_source(self, source: str) -> pd.DataFrame:
        """Carga datos de una fuente específica (meteoblue, openmeteo, etc)"""
        json_df = JSONDataLoader.load_from_directory(self.data_dir)
        
        if 'source' in json_df.columns:
            return json_df[json_df['source'] == source]
        
        return pd.DataFrame()
    
    def get_metadata(self) -> dict:
        """Retorna metadatos de la carga"""
        return self.metadata
    
    @staticmethod
    def get_available_locations(data_dir: Union[str, Path] = "data") -> list:
        """Retorna lista de ubicaciones disponibles en los datos"""
        data_dir = Path(data_dir)
        locations = set()
        
        for json_file in data_dir.glob("consulta_completa_*.json"):
            # Extraer ubicación del nombre: consulta_completa_UBICACION_DATETIME.json
            parts = json_file.stem.split('_')
            if len(parts) >= 3:
                locations.add(parts[2])
        
        return sorted(list(locations))
    
    @staticmethod
    def get_available_sources(data_dir: Union[str, Path] = "data") -> list:
        """Retorna fuentes climáticas disponibles"""
        json_df = JSONDataLoader.load_from_directory(data_dir)
        
        if 'source' in json_df.columns:
            return json_df['source'].unique().tolist()
        
        return []
