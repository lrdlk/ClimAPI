"""
Cargador genérico para archivos CSV, TXT, Excel
"""

import pandas as pd
from pathlib import Path
from typing import Union, Dict
import logging

logger = logging.getLogger(__name__)


class FileLoader:
    """Carga datos de archivos CSV, TXT, Excel, etc."""
    
    EXTENSION_HANDLERS = {
        '.csv': 'read_csv',
        '.txt': 'read_csv',  # Asumir formato similar a CSV
        '.xlsx': 'read_excel',
        '.xls': 'read_excel',
        '.parquet': 'read_parquet',
    }
    
    @staticmethod
    def load_file(filepath: Union[str, Path], **kwargs) -> pd.DataFrame:
        """
        Carga archivo automáticamente según extensión
        
        Args:
            filepath: Ruta del archivo
            **kwargs: Argumentos adicionales para pandas (delimiter, encoding, etc.)
        
        Returns:
            DataFrame
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            logger.error(f"Archivo no encontrado: {filepath}")
            return pd.DataFrame()
        
        ext = filepath.suffix.lower()
        
        if ext not in FileLoader.EXTENSION_HANDLERS:
            logger.warning(f"Extensión no soportada: {ext}")
            return pd.DataFrame()
        
        try:
            handler = getattr(pd, FileLoader.EXTENSION_HANDLERS[ext])
            
            # Argumentos por defecto según tipo
            if ext in ['.csv', '.txt']:
                kwargs.setdefault('encoding', 'utf-8')
                kwargs.setdefault('sep', None)  # Detectar automáticamente
            
            df = handler(filepath, **kwargs)
            logger.info(f"Cargado: {filepath.name} ({len(df)} filas)")
            return df
            
        except Exception as e:
            logger.error(f"Error cargando {filepath}: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def load_directory(directory: Union[str, Path], 
                      pattern: str = "*", **kwargs) -> Dict[str, pd.DataFrame]:
        """
        Carga todos los archivos soportados de un directorio
        
        Returns:
            Diccionario {nombre_archivo: DataFrame}
        """
        directory = Path(directory)
        result = {}
        
        for file in directory.glob(pattern):
            if file.suffix.lower() in FileLoader.EXTENSION_HANDLERS:
                df = FileLoader.load_file(file, **kwargs)
                if not df.empty:
                    result[file.stem] = df
        
        return result
    
    @staticmethod
    def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Estandariza nombres de columnas climáticas
        Busca patrones comunes y renombra
        """
        replacements = {
            r'temp.*': 'temperature_C',
            r'wind.*speed': 'windspeed_ms',
            r'wind.*dir': 'winddirection_deg',
            r'precip.*': 'precipitation_mm',
            r'humidity|humedad': 'humidity_percent',
            r'pressure|presion': 'pressure_hPa',
            r'cloud.*': 'cloudiness_percent',
        }
        
        new_columns = {}
        for col in df.columns:
            col_lower = col.lower()
            for pattern, new_name in replacements.items():
                if pd.Series(col_lower).str.contains(pattern, case=False, regex=True).any():
                    new_columns[col] = new_name
                    break
        
        if new_columns:
            df = df.rename(columns=new_columns)
        
        return df
