"""
Módulo para transformar y limpiar datos meteorológicos.

Este módulo convierte las respuestas JSON de la API en DataFrames de Pandas,
limpia y estandariza las columnas, y prepara los datos para su análisis.
"""

import pandas as pd
from typing import Dict
from datetime import datetime


def json_to_dataframe(api_response: Dict) -> pd.DataFrame:
    """
    Convierte la respuesta JSON de la API en un DataFrame de Pandas.
    
    Args:
        api_response: Diccionario con la respuesta de la API de Open-Meteo
    
    Returns:
        pd.DataFrame: DataFrame con los datos meteorológicos procesados
    """
    # Extraer los datos horarios
    hourly_data = api_response.get("hourly", {})
    
    if not hourly_data:
        raise ValueError("La respuesta no contiene datos horarios")
    
    # Crear DataFrame desde los datos horarios
    df = pd.DataFrame(hourly_data)
    
    return df


def clean_and_standardize(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia y estandariza las columnas del DataFrame.
    
    Esta función:
    - Convierte la columna 'time' a datetime
    - Establece 'time' como índice
    - Renombra columnas a nombres más legibles en español
    - Elimina filas con valores nulos críticos
    
    Args:
        df: DataFrame con datos meteorológicos sin procesar
    
    Returns:
        pd.DataFrame: DataFrame limpio y estandarizado
    """
    # Crear una copia para no modificar el original
    df_clean = df.copy()
    
    # Convertir la columna 'time' a datetime
    if 'time' in df_clean.columns:
        df_clean['time'] = pd.to_datetime(df_clean['time'])
        # Establecer 'time' como índice
        df_clean.set_index('time', inplace=True)
    
    # Renombrar columnas a nombres más legibles
    column_mapping = {
        'temperature_2m': 'temperatura_c',
        'relative_humidity_2m': 'humedad_porcentaje',
        'precipitation': 'precipitacion_mm',
        'windspeed_10m': 'velocidad_viento_kmh'
    }
    
    # Renombrar solo las columnas que existen
    df_clean.rename(columns=column_mapping, inplace=True)
    
    # Eliminar filas donde la temperatura es nula (datos críticos)
    df_clean = df_clean.dropna(subset=['temperatura_c'])
    
    # Redondear valores numéricos a 2 decimales
    numeric_columns = df_clean.select_dtypes(include=['float64', 'int64']).columns
    df_clean[numeric_columns] = df_clean[numeric_columns].round(2)
    
    return df_clean


def process_weather_data(api_response: Dict) -> pd.DataFrame:
    """
    Función principal que procesa completamente los datos meteorológicos.
    
    Combina json_to_dataframe y clean_and_standardize en un solo flujo.
    
    Args:
        api_response: Diccionario con la respuesta de la API de Open-Meteo
    
    Returns:
        pd.DataFrame: DataFrame completamente procesado y listo para usar
    """
    # Convertir JSON a DataFrame
    df = json_to_dataframe(api_response)
    
    # Limpiar y estandarizar
    df_clean = clean_and_standardize(df)
    
    return df_clean

