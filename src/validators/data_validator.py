"""
Validadores de calidad de datos climáticos
Detecta anomalías, valores faltantes y outliers
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, List
import logging

logger = logging.getLogger(__name__)


class DataValidator:
    """Valida integridad y calidad de datos climáticos"""
    
    # Rangos realistas para variables climáticas
    VALID_RANGES = {
        'temperature_C': (-50, 60),  # Temperatura razonable
        'windspeed_ms': (0, 50),      # Velocidad del viento
        'humidity_percent': (0, 100), # Humedad relativa
        'pressure_hPa': (900, 1100),  # Presión
        'precipitation_mm': (0, 500), # Precipitación
        'cloudiness_percent': (0, 100),
    }
    
    @staticmethod
    def validate_range(df: pd.DataFrame, column: str, 
                      min_val: float, max_val: float) -> Tuple[pd.DataFrame, Dict]:
        """
        Valida que valores estén en rango esperado
        
        Returns:
            (DataFrame limpio, reporte de anomalías)
        """
        if column not in df.columns:
            return df, {}
        
        mask = (df[column] >= min_val) & (df[column] <= max_val)
        outliers = df[~mask]
        
        report = {
            'column': column,
            'valid_range': (min_val, max_val),
            'outliers_count': len(outliers),
            'outliers_percent': round(100 * len(outliers) / len(df), 2),
        }
        
        if len(outliers) > 0:
            logger.warning(f"{column}: {report['outliers_count']} outliers detectados "
                          f"({report['outliers_percent']}%)")
        
        return df[mask], report
    
    @staticmethod
    def validate_all(df: pd.DataFrame, remove_outliers: bool = True) -> Tuple[pd.DataFrame, Dict]:
        """
        Valida todo el DataFrame contra rangos conocidos
        
        Returns:
            (DataFrame validado, reporte completo)
        """
        initial_len = len(df)
        reports = {}
        
        for column, (min_val, max_val) in DataValidator.VALID_RANGES.items():
            if column in df.columns:
                df, report = DataValidator.validate_range(df, column, min_val, max_val)
                reports[column] = report
        
        if remove_outliers:
            removed = initial_len - len(df)
            if removed > 0:
                logger.info(f"Eliminadas {removed} filas con outliers ({100*removed/initial_len:.1f}%)")
        
        return df, reports
    
    @staticmethod
    def check_missing_data(df: pd.DataFrame) -> Dict[str, float]:
        """
        Analiza datos faltantes
        
        Returns:
            {columna: porcentaje_faltante}
        """
        missing = {}
        
        for col in df.columns:
            pct = 100 * df[col].isna().sum() / len(df)
            if pct > 0:
                missing[col] = pct
        
        if missing:
            logger.info("Datos faltantes detectados:")
            for col, pct in sorted(missing.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"  {col}: {pct:.1f}%")
        
        return missing
    
    @staticmethod
    def detect_duplicates(df: pd.DataFrame, subset: List[str] = None) -> int:
        """Detecta filas duplicadas"""
        duplicates = df.duplicated(subset=subset, keep=False).sum()
        
        if duplicates > 0:
            logger.warning(f"Detectadas {duplicates} filas duplicadas")
        
        return duplicates
    
    @staticmethod
    def fill_missing(df: pd.DataFrame, method: str = 'forward') -> pd.DataFrame:
        """
        Rellena datos faltantes
        
        Args:
            method: 'forward' (last observation), 'linear', 'mean', 'drop'
        """
        initial_nulls = df.isna().sum().sum()
        
        if method == 'forward':
            df = df.fillna(method='ffill').fillna(method='bfill')
        elif method == 'linear':
            numeric_cols = df.select_dtypes(include=['number']).columns
            for col in numeric_cols:
                if df[col].isna().any():
                    df[col] = df[col].interpolate(method='linear')
        elif method == 'mean':
            numeric_cols = df.select_dtypes(include=['number']).columns
            for col in numeric_cols:
                df[col].fillna(df[col].mean(), inplace=True)
        elif method == 'drop':
            df = df.dropna()
        
        final_nulls = df.isna().sum().sum()
        
        if initial_nulls > 0:
            logger.info(f"Nulos rellenados: {initial_nulls} → {final_nulls} ({method})")
        
        return df
