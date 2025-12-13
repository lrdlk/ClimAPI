import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
from datetime import datetime, timedelta
from pathlib import Path
import json
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
import os


class OpenMeteoClient:
    """Cliente para consumir datos de Open-Meteo API (Forecast y Historical)"""
    
    def __init__(self, data_dir: str = "data"):
        """
        Inicializa el cliente de Open-Meteo
        
        Args:
            data_dir: Directorio base para guardar datos
        """
        # Setup con cache y retry
        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        self.client = openmeteo_requests.Client(session=retry_session)
        
        # URLs de las APIs
        self.forecast_url = "https://api.open-meteo.com/v1/forecast"
        self.historical_url = "https://archive-api.open-meteo.com/v1/archive"
        
        # Directorios para datos
        self.data_dir = Path(data_dir)
        self.openmeteo_dir = self.data_dir / "data_openmeteo"
        self.openmeteo_dir.mkdir(parents=True, exist_ok=True)
    
    def get_forecast(self, lat: float, lon: float,
                     location_name: str = "location",
                     days: int = 7,
                     hourly_vars: Optional[List[str]] = None,
                     daily_vars: Optional[List[str]] = None,
                     save_data: bool = True) -> Dict[str, Any]:
        """
        Obtiene el pronóstico del tiempo
        
        Args:
            lat: Latitud
            lon: Longitud
            location_name: Nombre de la ubicación
            days: Días de pronóstico (1-16)
            hourly_vars: Variables horarias a consultar
            daily_vars: Variables diarias a consultar
            save_data: Si guardar los datos
            
        Returns:
            Diccionario con los datos del pronóstico
        """
        # Variables por defecto
        if hourly_vars is None:
            hourly_vars = ["temperature_2m", "relative_humidity_2m", "wind_speed_10m"]
        
        if daily_vars is None:
            daily_vars = ["temperature_2m_max", "temperature_2m_min", 
                         "precipitation_sum", "wind_speed_10m_max"]
        
        # Parámetros de la consulta
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": hourly_vars,
            "daily": daily_vars,
            "forecast_days": days,
            "timezone": "auto"
        }
        
        # Realizar consulta
        responses = self.client.weather_api(self.forecast_url, params=params)
        response = responses[0]
        
        # Procesar respuesta
        result = {
            "location": location_name,
            "coordinates": {
                "latitude": response.Latitude(),
                "longitude": response.Longitude(),
                "elevation": response.Elevation()
            },
            "timezone": response.UtcOffsetSeconds(),
            "hourly": None,
            "daily": None
        }
        
        # Procesar datos horarios
        if hourly_vars:
            hourly = response.Hourly()
            hourly_data = {
                "date": pd.date_range(
                    start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                    end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                    freq=pd.Timedelta(seconds=hourly.Interval()),
                    inclusive="left"
                )
            }
            
            for i, var in enumerate(hourly_vars):
                hourly_data[var] = hourly.Variables(i).ValuesAsNumpy()
            
            result["hourly"] = pd.DataFrame(data=hourly_data)
        
        # Procesar datos diarios
        if daily_vars:
            daily = response.Daily()
            daily_data = {
                "date": pd.date_range(
                    start=pd.to_datetime(daily.Time(), unit="s", utc=True),
                    end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
                    freq=pd.Timedelta(seconds=daily.Interval()),
                    inclusive="left"
                )
            }
            
            for i, var in enumerate(daily_vars):
                daily_data[var] = daily.Variables(i).ValuesAsNumpy()
            
            result["daily"] = pd.DataFrame(data=daily_data)
        
        # Guardar datos
        if save_data:
            self._save_forecast_data(result, location_name)
        
        return result
    
    def get_historical(self, lat: float, lon: float,
                      start_date: str, end_date: str,
                      location_name: str = "location",
                      hourly_vars: Optional[List[str]] = None,
                      daily_vars: Optional[List[str]] = None,
                      save_data: bool = True) -> Dict[str, Any]:
        """
        Obtiene datos históricos del tiempo
        
        Args:
            lat: Latitud
            lon: Longitud
            start_date: Fecha inicio (YYYY-MM-DD)
            end_date: Fecha fin (YYYY-MM-DD)
            location_name: Nombre de la ubicación
            hourly_vars: Variables horarias a consultar
            daily_vars: Variables diarias a consultar
            save_data: Si guardar los datos
            
        Returns:
            Diccionario con los datos históricos
        """
        # Variables por defecto
        if hourly_vars is None:
            hourly_vars = ["temperature_2m", "relative_humidity_2m", "wind_speed_10m"]
        
        if daily_vars is None:
            daily_vars = ["temperature_2m_max", "temperature_2m_min", 
                         "precipitation_sum", "wind_speed_10m_max"]
        
        # Parámetros de la consulta
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start_date,
            "end_date": end_date,
            "hourly": hourly_vars,
            "daily": daily_vars,
            "timezone": "auto"
        }
        
        # Realizar consulta
        responses = self.client.weather_api(self.historical_url, params=params)
        response = responses[0]
        
        # Procesar respuesta (similar a forecast)
        result = {
            "location": location_name,
            "coordinates": {
                "latitude": response.Latitude(),
                "longitude": response.Longitude(),
                "elevation": response.Elevation()
            },
            "timezone": response.UtcOffsetSeconds(),
            "period": {"start": start_date, "end": end_date},
            "hourly": None,
            "daily": None
        }
        
        # Procesar datos horarios
        if hourly_vars:
            hourly = response.Hourly()
            hourly_data = {
                "date": pd.date_range(
                    start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                    end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                    freq=pd.Timedelta(seconds=hourly.Interval()),
                    inclusive="left"
                )
            }
            
            for i, var in enumerate(hourly_vars):
                hourly_data[var] = hourly.Variables(i).ValuesAsNumpy()
            
            result["hourly"] = pd.DataFrame(data=hourly_data)
        
        # Procesar datos diarios
        if daily_vars:
            daily = response.Daily()
            daily_data = {
                "date": pd.date_range(
                    start=pd.to_datetime(daily.Time(), unit="s", utc=True),
                    end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
                    freq=pd.Timedelta(seconds=daily.Interval()),
                    inclusive="left"
                )
            }
            
            for i, var in enumerate(daily_vars):
                daily_data[var] = daily.Variables(i).ValuesAsNumpy()
            
            result["daily"] = pd.DataFrame(data=daily_data)
        
        # Guardar datos
        if save_data:
            self._save_historical_data(result, location_name, start_date, end_date)
        
        return result
    
    def _save_forecast_data(self, data: Dict[str, Any], location_name: str):
        """Guarda datos de pronóstico"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Guardar metadatos
        metadata = {
            "location": data["location"],
            "coordinates": data["coordinates"],
            "timezone": data["timezone"],
            "timestamp": timestamp
        }
        
        metadata_file = self.openmeteo_dir / f"forecast_{location_name}_{timestamp}_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        # Guardar datos horarios
        if data["hourly"] is not None:
            hourly_file = self.openmeteo_dir / f"forecast_{location_name}_{timestamp}_hourly.csv"
            data["hourly"].to_csv(hourly_file, index=False)
            print(f"📊 Datos horarios guardados: {hourly_file}")
        
        # Guardar datos diarios
        if data["daily"] is not None:
            daily_file = self.openmeteo_dir / f"forecast_{location_name}_{timestamp}_daily.csv"
            data["daily"].to_csv(daily_file, index=False)
            print(f"📊 Datos diarios guardados: {daily_file}")
    
    def _save_historical_data(self, data: Dict[str, Any], location_name: str, 
                             start_date: str, end_date: str):
        """Guarda datos históricos"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Guardar metadatos
        metadata = {
            "location": data["location"],
            "coordinates": data["coordinates"],
            "timezone": data["timezone"],
            "period": data["period"],
            "timestamp": timestamp
        }
        
        metadata_file = self.openmeteo_dir / f"historical_{location_name}_{start_date}_{end_date}_{timestamp}_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        # Guardar datos horarios
        if data["hourly"] is not None:
            hourly_file = self.openmeteo_dir / f"historical_{location_name}_{start_date}_{end_date}_{timestamp}_hourly.csv"
            data["hourly"].to_csv(hourly_file, index=False)
            print(f"📊 Datos históricos horarios guardados: {hourly_file}")
        
        # Guardar datos diarios
        if data["daily"] is not None:
            daily_file = self.openmeteo_dir / f"historical_{location_name}_{start_date}_{end_date}_{timestamp}_daily.csv"
            data["daily"].to_csv(daily_file, index=False)
            print(f"📊 Datos históricos diarios guardados: {daily_file}")


# Ejemplo de uso
if __name__ == "__main__":
    # Cargar variables de entorno (opcional para Open-Meteo, es gratuito)
    load_dotenv()
    
    # Crear cliente
    client = OpenMeteoClient()
    
    # Ubicaciones a consultar
    locations = [
        {"name": "Medellin", "lat": 6.245, "lon": -75.5715},
        {"name": "Bogota", "lat": 4.711, "lon": -74.0721},
        {"name": "Cartagena", "lat": 10.391, "lon": -75.4794},
    ]
    
    print("=" * 70)
    print("OPEN-METEO: PRONÓSTICO DEL TIEMPO (7 DÍAS)")
    print("=" * 70)
    
    for location in locations:
        print(f"\n📍 {location['name']}")
        print("-" * 70)
        
        try:
            # Obtener pronóstico
            forecast = client.get_forecast(
                lat=location['lat'],
                lon=location['lon'],
                location_name=location['name'],
                days=7,
                save_data=True
            )
            
            # Mostrar información
            print(f"Coordenadas: {forecast['coordinates']['latitude']}°N, {forecast['coordinates']['longitude']}°E")
            print(f"Elevación: {forecast['coordinates']['elevation']} m")
            
            # Mostrar resumen de datos diarios
            if forecast['daily'] is not None:
                daily = forecast['daily']
                print(f"\n📅 Resumen próximos 3 días:")
                for i in range(min(3, len(daily))):
                    date = daily['date'].iloc[i].strftime('%Y-%m-%d')
                    temp_max = daily['temperature_2m_max'].iloc[i]
                    temp_min = daily['temperature_2m_min'].iloc[i]
                    precip = daily['precipitation_sum'].iloc[i]
                    wind = daily['wind_speed_10m_max'].iloc[i]
                    
                    print(f"  {date}: {temp_min:.1f}°C - {temp_max:.1f}°C | "
                          f"Precipitación: {precip:.1f}mm | Viento: {wind:.1f}km/h")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("OPEN-METEO: DATOS HISTÓRICOS (ÚLTIMOS 14 DÍAS)")
    print("=" * 70)
    
    # Calcular fechas para histórico
    end_date = datetime.now() - timedelta(days=1)
    start_date = end_date - timedelta(days=13)
    
    for location in locations[:1]:  # Solo Medellín para el ejemplo histórico
        print(f"\n📍 {location['name']}")
        print("-" * 70)
        
        try:
            # Obtener datos históricos
            historical = client.get_historical(
                lat=location['lat'],
                lon=location['lon'],
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
                location_name=location['name'],
                save_data=True
            )
            
            print(f"Período: {historical['period']['start']} a {historical['period']['end']}")
            print(f"Coordenadas: {historical['coordinates']['latitude']}°N, {historical['coordinates']['longitude']}°E")
            
            # Mostrar estadísticas
            if historical['daily'] is not None:
                daily = historical['daily']
                print(f"\n📊 Estadísticas del período:")
                print(f"  Temperatura máxima promedio: {daily['temperature_2m_max'].mean():.1f}°C")
                print(f"  Temperatura mínima promedio: {daily['temperature_2m_min'].mean():.1f}°C")
                print(f"  Precipitación total: {daily['precipitation_sum'].sum():.1f}mm")
                print(f"  Viento máximo registrado: {daily['wind_speed_10m_max'].max():.1f}km/h")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("Consultas completadas")
    print("=" * 70)