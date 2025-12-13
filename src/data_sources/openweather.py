import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
import os
import time


class OpenWeatherMapClient:
    """Cliente para consumir datos de OpenWeatherMap API (servicios gratuitos)"""
    
    def __init__(self, api_key: str, data_dir: str = "data"):
        """
        Inicializa el cliente de OpenWeatherMap
        
        Args:
            api_key: Tu API key de OpenWeatherMap
            data_dir: Directorio base para guardar datos
        """
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.geo_url = "http://api.openweathermap.org/geo/1.0"
        
        # Directorios para datos
        self.data_dir = Path(data_dir)
        self.openweather_dir = self.data_dir / "data_openweathermap"
        self.openweather_dir.mkdir(parents=True, exist_ok=True)
    
    def get_coordinates(self, city_name: str, country_code: str = "") -> Optional[Dict[str, float]]:
        """
        Obtiene coordenadas de una ciudad usando Geocoding API
        
        Args:
            city_name: Nombre de la ciudad
            country_code: Código de país ISO 3166 (opcional, ej: "CO")
            
        Returns:
            Diccionario con lat, lon, o None si no se encuentra
        """
        query = f"{city_name},{country_code}" if country_code else city_name
        url = f"{self.geo_url}/direct"
        params = {
            "q": query,
            "limit": 1,
            "appid": self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data:
                return {
                    "lat": data[0]["lat"],
                    "lon": data[0]["lon"],
                    "name": data[0].get("name", city_name),
                    "country": data[0].get("country", "")
                }
            return None
        except Exception as e:
            print(f"❌ Error obteniendo coordenadas: {e}")
            return None
    
    def get_current_weather(self, lat: float, lon: float, 
                           location_name: str = "location",
                           save_data: bool = True) -> Dict[str, Any]:
        """
        Obtiene el clima actual (Current Weather Data API - Gratuito)
        
        Args:
            lat: Latitud
            lon: Longitud
            location_name: Nombre de la ubicación
            save_data: Si guardar los datos
            
        Returns:
            Diccionario con datos del clima actual
        """
        url = f"{self.base_url}/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric",  # Celsius
            "lang": "es"
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Procesar datos
        result = {
            "location": location_name,
            "coordinates": {"lat": lat, "lon": lon},
            "timestamp": datetime.fromtimestamp(data["dt"]).isoformat(),
            "weather": {
                "description": data["weather"][0]["description"],
                "main": data["weather"][0]["main"],
                "icon": data["weather"][0]["icon"]
            },
            "temperature": {
                "current": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "min": data["main"]["temp_min"],
                "max": data["main"]["temp_max"]
            },
            "pressure": data["main"]["pressure"],
            "humidity": data["main"]["humidity"],
            "visibility": data.get("visibility", 0) / 1000,  # Convertir a km
            "wind": {
                "speed": data["wind"]["speed"],
                "direction": data["wind"].get("deg", 0),
                "gust": data["wind"].get("gust", None)
            },
            "clouds": data["clouds"]["all"],
            "sunrise": datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%H:%M:%S"),
            "sunset": datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%H:%M:%S")
        }
        
        if "rain" in data:
            result["rain"] = data["rain"]
        if "snow" in data:
            result["snow"] = data["snow"]
        
        if save_data:
            self._save_data(result, location_name, "current")
        
        return result
    
    def get_forecast_5day(self, lat: float, lon: float,
                         location_name: str = "location",
                         save_data: bool = True) -> Dict[str, Any]:
        """
        Obtiene pronóstico de 5 días con datos cada 3 horas (5 Day Forecast - Gratuito)
        
        Args:
            lat: Latitud
            lon: Longitud
            location_name: Nombre de la ubicación
            save_data: Si guardar los datos
            
        Returns:
            Diccionario con pronóstico de 5 días
        """
        url = f"{self.base_url}/forecast"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric",
            "lang": "es"
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Procesar datos
        result = {
            "location": location_name,
            "coordinates": {"lat": lat, "lon": lon},
            "city": data["city"]["name"],
            "country": data["city"]["country"],
            "timezone": data["city"]["timezone"],
            "forecast": []
        }
        
        for item in data["list"]:
            forecast_item = {
                "datetime": datetime.fromtimestamp(item["dt"]).isoformat(),
                "date": datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d"),
                "time": datetime.fromtimestamp(item["dt"]).strftime("%H:%M"),
                "weather": {
                    "description": item["weather"][0]["description"],
                    "main": item["weather"][0]["main"]
                },
                "temperature": {
                    "temp": item["main"]["temp"],
                    "feels_like": item["main"]["feels_like"],
                    "min": item["main"]["temp_min"],
                    "max": item["main"]["temp_max"]
                },
                "pressure": item["main"]["pressure"],
                "humidity": item["main"]["humidity"],
                "wind": {
                    "speed": item["wind"]["speed"],
                    "direction": item["wind"].get("deg", 0)
                },
                "clouds": item["clouds"]["all"],
                "precipitation_probability": item.get("pop", 0) * 100  # Probabilidad de precipitación
            }
            
            if "rain" in item:
                forecast_item["rain_3h"] = item["rain"].get("3h", 0)
            if "snow" in item:
                forecast_item["snow_3h"] = item["snow"].get("3h", 0)
            
            result["forecast"].append(forecast_item)
        
        if save_data:
            self._save_data(result, location_name, "forecast_5day")
        
        return result
    
    def get_air_pollution(self, lat: float, lon: float,
                         location_name: str = "location",
                         save_data: bool = True) -> Dict[str, Any]:
        """
        Obtiene datos de contaminación del aire actual (Air Pollution API - Gratuito)
        
        Args:
            lat: Latitud
            lon: Longitud
            location_name: Nombre de la ubicación
            save_data: Si guardar los datos
            
        Returns:
            Diccionario con datos de calidad del aire
        """
        url = f"{self.base_url}/air_pollution"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Índice de calidad del aire (AQI)
        aqi_labels = {
            1: "Bueno",
            2: "Aceptable",
            3: "Moderado",
            4: "Malo",
            5: "Muy Malo"
        }
        
        item = data["list"][0]
        result = {
            "location": location_name,
            "coordinates": {"lat": lat, "lon": lon},
            "timestamp": datetime.fromtimestamp(item["dt"]).isoformat(),
            "aqi": {
                "value": item["main"]["aqi"],
                "label": aqi_labels.get(item["main"]["aqi"], "Desconocido")
            },
            "components": {
                "co": item["components"]["co"],  # Monóxido de carbono (μg/m3)
                "no": item["components"]["no"],  # Monóxido de nitrógeno (μg/m3)
                "no2": item["components"]["no2"],  # Dióxido de nitrógeno (μg/m3)
                "o3": item["components"]["o3"],  # Ozono (μg/m3)
                "so2": item["components"]["so2"],  # Dióxido de azufre (μg/m3)
                "pm2_5": item["components"]["pm2_5"],  # Partículas finas (μg/m3)
                "pm10": item["components"]["pm10"],  # Partículas gruesas (μg/m3)
                "nh3": item["components"]["nh3"]  # Amoníaco (μg/m3)
            }
        }
        
        if save_data:
            self._save_data(result, location_name, "air_pollution")
        
        return result
    
    def get_complete_report(self, lat: float, lon: float,
                           location_name: str = "location",
                           save_data: bool = True) -> Dict[str, Any]:
        """
        Obtiene un reporte completo con todos los datos disponibles
        
        Args:
            lat: Latitud
            lon: Longitud
            location_name: Nombre de la ubicación
            save_data: Si guardar los datos
            
        Returns:
            Diccionario con reporte completo
        """
        print(f"🔄 Obteniendo reporte completo para {location_name}...")
        
        report = {
            "location": location_name,
            "coordinates": {"lat": lat, "lon": lon},
            "timestamp": datetime.now().isoformat(),
            "current": None,
            "forecast": None,
            "air_quality": None
        }
        
        try:
            report["current"] = self.get_current_weather(lat, lon, location_name, save_data=False)
            time.sleep(0.5)  # Evitar rate limiting
        except Exception as e:
            print(f"⚠️  Error obteniendo clima actual: {e}")
        
        try:
            report["forecast"] = self.get_forecast_5day(lat, lon, location_name, save_data=False)
            time.sleep(0.5)
        except Exception as e:
            print(f"⚠️  Error obteniendo pronóstico: {e}")
        
        try:
            report["air_quality"] = self.get_air_pollution(lat, lon, location_name, save_data=False)
            time.sleep(0.5)
        except Exception as e:
            print(f"⚠️  Error obteniendo calidad del aire: {e}")
        
        if save_data:
            self._save_data(report, location_name, "complete_report")
        
        return report
    
    def _save_data(self, data: Dict[str, Any], location_name: str, data_type: str):
        """Guarda datos en JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{data_type}_{location_name}_{timestamp}.json"
        filepath = self.openweather_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Datos guardados: {filepath}")


# Ejemplo de uso
if __name__ == "__main__":
    # Cargar variables de entorno
    load_dotenv()
    
    # Obtener API key (primero intenta desde .env, sino usa la proporcionada)
    API_KEY = os.getenv("OPENWEATHER_API_KEY", "32bdf300d39d022bb540ccbb5ea50970")
    
    if not API_KEY:
        print("❌ Error: No se encontró OPENWEATHER_API_KEY")
        exit(1)
    
    # Crear cliente
    client = OpenWeatherMapClient(API_KEY)
    
    # Ubicaciones a consultar
    locations = [
        {"name": "Medellín", "lat": 6.245, "lon": -75.5715},
        {"name": "Bogotá", "lat": 4.711, "lon": -74.0721},
        {"name": "Cartagena", "lat": 10.391, "lon": -75.4794},
    ]
    
    print("=" * 80)
    print("OPENWEATHERMAP: CLIMA ACTUAL")
    print("=" * 80)
    
    for location in locations:
        print(f"\n📍 {location['name']}")
        print("-" * 80)
        
        try:
            # Clima actual
            current = client.get_current_weather(
                lat=location['lat'],
                lon=location['lon'],
                location_name=location['name'],
                save_data=True
            )
            
            print(f"🌡️  Temperatura: {current['temperature']['current']:.1f}°C "
                  f"(sensación: {current['temperature']['feels_like']:.1f}°C)")
            print(f"🌤️  Clima: {current['weather']['description'].capitalize()}")
            print(f"💨 Viento: {current['wind']['speed']} m/s "
                  f"(dirección: {current['wind']['direction']}°)")
            print(f"💧 Humedad: {current['humidity']}%")
            print(f"🔽 Presión: {current['pressure']} hPa")
            print(f"👁️  Visibilidad: {current['visibility']} km")
            print(f"☁️  Nubosidad: {current['clouds']}%")
            print(f"🌅 Amanecer: {current['sunrise']} | Atardecer: {current['sunset']}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 80)
    print("OPENWEATHERMAP: PRONÓSTICO 5 DÍAS")
    print("=" * 80)
    
    for location in locations[:1]:  # Solo primera ubicación para ejemplo
        print(f"\n📍 {location['name']}")
        print("-" * 80)
        
        try:
            forecast = client.get_forecast_5day(
                lat=location['lat'],
                lon=location['lon'],
                location_name=location['name'],
                save_data=True
            )
            
            # Agrupar por día
            days = {}
            for item in forecast['forecast']:
                date = item['date']
                if date not in days:
                    days[date] = []
                days[date].append(item)
            
            # Mostrar resumen por día
            print(f"\n📅 Pronóstico próximos días:")
            for date, items in list(days.items())[:5]:
                temps = [item['temperature']['temp'] for item in items]
                precip_prob = max([item['precipitation_probability'] for item in items])
                weather_desc = items[len(items)//2]['weather']['description']  # Del mediodía
                
                print(f"  {date}: {min(temps):.1f}°C - {max(temps):.1f}°C | "
                      f"{weather_desc.capitalize()} | "
                      f"Precip: {precip_prob:.0f}%")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 80)
    print("OPENWEATHERMAP: CALIDAD DEL AIRE")
    print("=" * 80)
    
    for location in locations:
        print(f"\n📍 {location['name']}")
        print("-" * 80)
        
        try:
            air = client.get_air_pollution(
                lat=location['lat'],
                lon=location['lon'],
                location_name=location['name'],
                save_data=True
            )
            
            print(f"🏭 Índice de Calidad del Aire (AQI): {air['aqi']['value']} - {air['aqi']['label']}")
            print(f"   PM2.5: {air['components']['pm2_5']:.2f} μg/m³")
            print(f"   PM10: {air['components']['pm10']:.2f} μg/m³")
            print(f"   CO: {air['components']['co']:.2f} μg/m³")
            print(f"   NO2: {air['components']['no2']:.2f} μg/m³")
            print(f"   O3: {air['components']['o3']:.2f} μg/m³")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 80)
    print("Consultas completadas")
    print("=" * 80)