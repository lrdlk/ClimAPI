import requests
import json
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class MeteosourceAPI:
    def __init__(self):
        self.api_key = os.getenv('METEOSOURCE_API_KEY')
        self.base_url = "https://www.meteosource.com/api/v1/free"
        self.data_dir = Path("data/data_meteosource")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.api_key:
            raise ValueError("API key no encontrada. Verifica tu archivo .env")
    
    def get_current_weather(self, place_id):
        """Obtiene el clima actual para una ubicación"""
        url = f"{self.base_url}/point"
        params = {
            'key': self.api_key,
            'place_id': place_id,
            'sections': 'current'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener datos: {e}")
            return None
    
    def get_hourly_forecast(self, place_id):
        """Obtiene pronóstico por hora"""
        url = f"{self.base_url}/point"
        params = {
            'key': self.api_key,
            'place_id': place_id,
            'sections': 'hourly'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener pronóstico horario: {e}")
            return None
    
    def get_daily_forecast(self, place_id):
        """Obtiene pronóstico diario"""
        url = f"{self.base_url}/point"
        params = {
            'key': self.api_key,
            'place_id': place_id,
            'sections': 'daily'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener pronóstico diario: {e}")
            return None
    
    def get_all_data(self, place_id):
        """Obtiene todos los datos disponibles (current, hourly, daily)"""
        url = f"{self.base_url}/point"
        params = {
            'key': self.api_key,
            'place_id': place_id,
            'sections': 'all'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener todos los datos: {e}")
            return None
    
    def save_data(self, data, place_id, data_type):
        """Guarda los datos en formato JSON"""
        if data is None:
            print("No hay datos para guardar")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{place_id}_{data_type}_{timestamp}.json"
        filepath = self.data_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✓ Datos guardados en: {filepath}")
        except Exception as e:
            print(f"Error al guardar datos: {e}")
    
    def display_current_weather(self, data):
        """Muestra información del clima actual"""
        if data and 'current' in data:
            current = data['current']
            print("\n" + "="*50)
            print(f"CLIMA ACTUAL - {data.get('place', 'Ubicación desconocida')}")
            print("="*50)
            print(f"Temperatura: {current.get('temperature', 'N/A')} °C")
            print(f"Sensación térmica: {current.get('feels_like', 'N/A')} °C")
            print(f"Descripción: {current.get('summary', 'N/A')}")
            print(f"Humedad: {current.get('humidity', 'N/A')}%")
            print(f"Viento: {current.get('wind', {}).get('speed', 'N/A')} m/s")
            print(f"Dirección del viento: {current.get('wind', {}).get('dir', 'N/A')}")
            print(f"Precipitación: {current.get('precipitation', {}).get('total', 'N/A')} mm")
            print(f"Presión: {current.get('pressure', 'N/A')} hPa")
            print(f"Visibilidad: {current.get('visibility', 'N/A')} km")
            print("="*50)

def main():
    # Inicializar API
    api = MeteosourceAPI()
    
    # Lista de ciudades para obtener datos (puedes modificar esto)
    ciudades = ['medellin', 'bogota', 'cali']
    
    print("Iniciando descarga de datos climáticos de Meteosource...")
    print(f"Directorio de datos: {api.data_dir}")
    
    for ciudad in ciudades:
        print(f"\n{'='*60}")
        print(f"Obteniendo datos para: {ciudad.upper()}")
        print(f"{'='*60}")
        
        # Obtener todos los datos
        all_data = api.get_all_data(ciudad)
        
        if all_data:
            # Mostrar clima actual
            api.display_current_weather(all_data)
            
            # Guardar datos completos
            api.save_data(all_data, ciudad, 'complete')
            
            # También puedes guardar secciones individuales si lo prefieres
            # api.save_data(all_data.get('current'), ciudad, 'current')
            # api.save_data(all_data.get('hourly'), ciudad, 'hourly')
            # api.save_data(all_data.get('daily'), ciudad, 'daily')
        else:
            print(f"✗ No se pudieron obtener datos para {ciudad}")
    
    print("\n" + "="*60)
    print("Descarga completada!")
    print(f"Revisa los archivos en: {api.data_dir}")
    print("="*60)

if __name__ == "__main__":
    main()