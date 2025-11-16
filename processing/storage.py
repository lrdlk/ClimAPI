"""
Módulo para guardar y cargar datos meteorológicos.

Este módulo proporciona funciones para persistir los DataFrames
en formato CSV y cargarlos posteriormente.
"""

import pandas as pd
from pathlib import Path
from typing import Optional
from datetime import datetime


def save_to_csv(
    df: pd.DataFrame,
    filepath: str,
    append: bool = False,
    include_timestamp: bool = False
) -> str:
    """
    Guarda un DataFrame en un archivo CSV.
    
    Args:
        df: DataFrame a guardar
        filepath: Ruta del archivo CSV (puede incluir o no la extensión .csv)
        append: Si es True, agrega los datos al archivo existente. Si es False, sobrescribe
        include_timestamp: Si es True, agrega un timestamp al nombre del archivo
    
    Returns:
        str: Ruta completa del archivo guardado
    """
    # Asegurar que el archivo tenga extensión .csv
    if not filepath.endswith('.csv'):
        filepath += '.csv'
    
    # Agregar timestamp si se solicita
    if include_timestamp:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path_obj = Path(filepath)
        filepath = f"{path_obj.stem}_{timestamp}{path_obj.suffix}"
    
    # Crear directorio si no existe
    path_obj = Path(filepath)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    
    # Guardar el DataFrame
    if append and path_obj.exists():
        # Modo append: leer el archivo existente, concatenar y guardar
        df_existing = pd.read_csv(filepath, index_col=0, parse_dates=True)
        df_combined = pd.concat([df_existing, df])
        # Eliminar duplicados basados en el índice
        df_combined = df_combined[~df_combined.index.duplicated(keep='last')]
        df_combined = df_combined.sort_index()
        df_combined.to_csv(filepath)
    else:
        # Modo write: guardar directamente
        df.to_csv(filepath)
    
    return filepath


def load_from_csv(filepath: str) -> pd.DataFrame:
    """
    Carga un DataFrame desde un archivo CSV.
    
    Args:
        filepath: Ruta del archivo CSV a cargar
    
    Returns:
        pd.DataFrame: DataFrame cargado con el índice 'time' como datetime
    """
    if not filepath.endswith('.csv'):
        filepath += '.csv'
    
    # Verificar que el archivo existe
    path_obj = Path(filepath)
    if not path_obj.exists():
        raise FileNotFoundError(f"El archivo {filepath} no existe")
    
    # Cargar el DataFrame
    df = pd.read_csv(filepath, index_col=0, parse_dates=True)
    
    return df

