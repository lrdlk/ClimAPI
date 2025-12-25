"""
Cargador especializado para archivos JSON de APIs climáticas
Soporta Meteoblue, OpenMeteo, OpenWeatherMap
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class JSONDataLoader:
    """Carga y parsea archivos JSON de diferentes fuentes climáticas"""
    
    SUPPORTED_SOURCES = ['meteoblue', 'openmeteo', 'openweather', 'meteosource']
    
    @staticmethod
    def load_json(filepath: Union[str, Path]) -> Dict:
        """Carga archivo JSON"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error cargando {filepath}: {e}")
            return {}
    
    @staticmethod
    def extract_meteoblue(data: Dict, location: str = None) -> pd.DataFrame:
        """
        Extrae datos de Meteoblue a DataFrame
        Columnas: timestamp, temp, windspeed, precipitation, humidity, pressure
        """
        if 'meteoblue' not in data:
            return pd.DataFrame()
        
        mb = data['meteoblue']
        if mb is None or 'hourly' not in mb or not mb.get('hourly'):
            return pd.DataFrame()
        
        hourly = mb['hourly']
        if 'time' not in hourly or not hourly['time']:
            return pd.DataFrame()
        
        # Crear DataFrame solo con datos disponibles
        df_dict = {'timestamp': pd.to_datetime(hourly['time'])}
        
        # Agregar columnas disponibles
        if 'temperature' in hourly:
            df_dict['temperature_C'] = hourly['temperature']
        if 'windspeed' in hourly:
            df_dict['windspeed_ms'] = hourly['windspeed']
        if 'winddirection' in hourly:
            df_dict['winddirection_deg'] = hourly['winddirection']
        if 'precipitation' in hourly:
            df_dict['precipitation_mm'] = hourly['precipitation']
        if 'relativehumidity' in hourly:
            df_dict['humidity_percent'] = hourly['relativehumidity']
        if 'pressure' in hourly:
            df_dict['pressure_hPa'] = hourly['pressure']
        
        if len(df_dict) <= 1:  # Solo timestamp
            return pd.DataFrame()
        
        df = pd.DataFrame(df_dict)
        
        if location:
            df['location'] = location
        
        return df
    
    @staticmethod
    def extract_openmeteo(data: Dict, location: str = None) -> pd.DataFrame:
        """Extrae datos de Open-Meteo a DataFrame"""
        if 'openmeteo' not in data:
            return pd.DataFrame()
        
        om = data['openmeteo']
        if om is None or 'hourly' not in om or not om.get('hourly'):
            return pd.DataFrame()
        
        hourly = om['hourly']
        if 'time' not in hourly or not hourly['time']:
            return pd.DataFrame()
        
        # Crear DataFrame solo con datos disponibles
        df_dict = {'timestamp': pd.to_datetime(hourly['time'])}
        
        # Agregar columnas disponibles (Open-Meteo usa nombres diferentes)
        if 'temperature_2m' in hourly:
            df_dict['temperature_C'] = hourly['temperature_2m']
        if 'windspeed_10m' in hourly:
            df_dict['windspeed_ms'] = hourly['windspeed_10m']
        if 'winddirection_10m' in hourly:
            df_dict['winddirection_deg'] = hourly['winddirection_10m']
        if 'precipitation' in hourly:
            df_dict['precipitation_mm'] = hourly['precipitation']
        if 'relative_humidity_2m' in hourly:
            df_dict['humidity_percent'] = hourly['relative_humidity_2m']
        if 'pressure' in hourly:
            df_dict['pressure_hPa'] = hourly['pressure']
        
        if len(df_dict) <= 1:  # Solo timestamp
            return pd.DataFrame()
        
        df = pd.DataFrame(df_dict)
        
        if location:
            df['location'] = location
        
        return df
    
    @staticmethod
    def extract_openweather(data: Dict, location: str = None) -> pd.DataFrame:
        """Extrae datos de OpenWeatherMap a DataFrame"""
        if 'openweather' not in data:
            return pd.DataFrame()
        
        ow = data['openweather']
        if ow is None:
            return pd.DataFrame()
        
        records = []
        
        # Procesar lista de pronósticos
        if 'list' in ow and ow['list']:
            for item in ow['list']:
                records.append({
                    'timestamp': pd.to_datetime(item['dt'], unit='s'),
                    'temperature_C': item.get('main', {}).get('temp'),
                    'windspeed_ms': item.get('wind', {}).get('speed'),
                    'winddirection_deg': item.get('wind', {}).get('deg'),
                    'precipitation_mm': item.get('rain', {}).get('3h', 0),
                    'humidity_percent': item.get('main', {}).get('humidity'),
                    'pressure_hPa': item.get('main', {}).get('pressure'),
                    'cloudiness_percent': item.get('clouds', {}).get('all'),
                })
        
        df = pd.DataFrame(records)
        if location:
            df['location'] = location
        
        return df
    
    @classmethod
    def load_from_directory(cls, directory: Union[str, Path], 
                           pattern: str = "*.json") -> pd.DataFrame:
        """
        Carga todos los JSON de un directorio y retorna DataFrame consolidado
        
        Args:
            directory: Ruta del directorio
            pattern: Patrón de búsqueda (ej: "consulta_completa_*.json")
        
        Returns:
            DataFrame consolidado de todos los archivos
        """
        directory = Path(directory)
        json_files = list(directory.glob(pattern))
        
        all_data = []
        
        for json_file in json_files:
            logger.info(f"Procesando: {json_file.name}")
            
            raw_data = cls.load_json(json_file)
            if not raw_data:
                continue
            
            location = raw_data.get('location', 'Unknown')
            
            # Intentar extraer de cada fuente
            for source in cls.SUPPORTED_SOURCES:
                if source in raw_data:
                    method_name = f'extract_{source}'
                    if hasattr(cls, method_name):
                        df = getattr(cls, method_name)(raw_data, location)
                        if not df.empty:
                            df['source'] = source
                            all_data.append(df)
                            break
        
        return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()
