"""
Transformación y normalización de datos meteorológicos.
Soporta múltiples formatos de fuentes (Open-Meteo, SIATA, etc.).
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def process_weather_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Procesa y normaliza datos meteorológicos de diferentes fuentes.
    
    Args:
        raw_data: Datos crudos de la API meteorológica
    
    Returns:
        Diccionario con datos normalizados
    
    Raises:
        ValueError: Si los datos no tienen el formato esperado
    """
    if not raw_data:
        raise ValueError("raw_data no puede estar vacío")
    
    processed = {
        "source": "unknown",
        "processed_at": datetime.utcnow().isoformat(),
        "status": "processed"
    }
    
    try:
        # Detectar y procesar según el formato
        if "current_weather" in raw_data:
            # Formato Open-Meteo
            processed.update(_process_openmeteo_format(raw_data))
            processed["source"] = "open_meteo"
        elif "temperatura" in raw_data or "estacion" in raw_data:
            # Formato SIATA
            processed.update(_process_siata_format(raw_data))
            processed["source"] = "siata"
        else:
            logger.warning("Formato de datos no reconocido, intentando procesamiento genérico")
            processed.update(_process_generic_format(raw_data))
            processed["status"] = "unknown_format"
        
        logger.info(f"✓ Datos procesados exitosamente (fuente: {processed['source']})")
        return processed
        
    except Exception as e:
        logger.error(f"❌ Error procesando datos: {str(e)}")
        processed["status"] = "error"
        processed["error"] = str(e)
        return processed


def _process_openmeteo_format(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Procesa datos en formato Open-Meteo.
    
    Args:
        data: Datos de Open-Meteo
    
    Returns:
        Diccionario con datos procesados
    """
    result = {}
    
    # Extraer datos actuales
    if "current_weather" in data:
        current = data["current_weather"]
        result.update({
            "temperature": current.get("temperature"),
            "wind_speed": current.get("windspeed"),
            "wind_direction": current.get("winddirection"),
            "weather_code": current.get("weathercode"),
            "timestamp": current.get("time")
        })
    
    # Extraer ubicación
    if "latitude" in data and "longitude" in data:
        result["location"] = {
            "latitude": data["latitude"],
            "longitude": data["longitude"]
        }
    
    # Extraer datos horarios (próximas 24 horas)
    if "hourly" in data:
        hourly = data["hourly"]
        result["hourly_forecast"] = _extract_hourly_forecast(hourly, hours=24)
    
    return result


def _process_siata_format(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Procesa datos en formato SIATA (Medellín).
    
    Args:
        data: Datos de SIATA
    
    Returns:
        Diccionario con datos procesados
    """
    result = {}
    
    # Mapeo de campos SIATA a formato estándar
    field_mapping = {
        "temperatura": "temperature",
        "humedad": "humidity",
        "presion": "pressure",
        "precipitacion": "precipitation",
        "velocidad_viento": "wind_speed",
        "direccion_viento": "wind_direction"
    }
    
    for siata_field, std_field in field_mapping.items():
        if siata_field in data:
            result[std_field] = data[siata_field]
    
    # Ubicación de estación
    if "estacion" in data:
        result["station"] = data["estacion"]
    
    if "latitud" in data and "longitud" in data:
        result["location"] = {
            "latitude": data["latitud"],
            "longitude": data["longitud"]
        }
    
    return result


def _process_generic_format(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Procesamiento genérico para formatos no reconocidos.
    
    Args:
        data: Datos en formato desconocido
    
    Returns:
        Diccionario con datos disponibles
    """
    result = {}
    
    # Palabras clave comunes para temperatura
    temp_keys = ["temperature", "temp", "temperatura", "t"]
    for key in temp_keys:
        if key in data:
            result["temperature"] = data[key]
            break
    
    # Palabras clave comunes para humedad
    humidity_keys = ["humidity", "humedad", "rh"]
    for key in humidity_keys:
        if key in data:
            result["humidity"] = data[key]
            break
    
    return result


def _extract_hourly_forecast(
    hourly_data: Dict[str, List],
    hours: int = 24
) -> Dict[str, List]:
    """
    Extrae pronóstico horario limitado a N horas.
    
    Args:
        hourly_data: Datos horarios de la API
        hours: Número de horas a extraer
    
    Returns:
        Diccionario con datos horarios limitados
    """
    forecast = {}
    
    fields = {
        "time": "time",
        "temperature_2m": "temperature",
        "relative_humidity_2m": "humidity",
        "precipitation": "precipitation",
        "wind_speed_10m": "wind_speed",
        "wind_direction_10m": "wind_direction"
    }
    
    for api_field, result_field in fields.items():
        if api_field in hourly_data:
            values = hourly_data[api_field]
            forecast[result_field] = values[:hours] if values else []
    
    return forecast


def calculate_statistics(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calcula estadísticas básicas de los datos horarios.
    
    Args:
        data: Datos procesados con hourly_forecast
    
    Returns:
        Diccionario con estadísticas (min, max, avg)
    """
    stats = {}
    
    if "hourly_forecast" not in data:
        return stats
    
    hourly = data["hourly_forecast"]
    
    # Calcular para temperatura
    if "temperature" in hourly and hourly["temperature"]:
        temps = [t for t in hourly["temperature"] if t is not None]
        if temps:
            stats["temperature"] = {
                "min": min(temps),
                "max": max(temps),
                "avg": round(sum(temps) / len(temps), 2)
            }
    
    # Calcular para humedad
    if "humidity" in hourly and hourly["humidity"]:
        humidities = [h for h in hourly["humidity"] if h is not None]
        if humidities:
            stats["humidity"] = {
                "min": min(humidities),
                "max": max(humidities),
                "avg": round(sum(humidities) / len(humidities), 2)
            }
    
    # Calcular para precipitación total
    if "precipitation" in hourly and hourly["precipitation"]:
        precip = [p for p in hourly["precipitation"] if p is not None]
        if precip:
            stats["precipitation_total"] = round(sum(precip), 2)
    
    # Calcular para viento
    if "wind_speed" in hourly and hourly["wind_speed"]:
        winds = [w for w in hourly["wind_speed"] if w is not None]
        if winds:
            stats["wind_speed"] = {
                "min": min(winds),
                "max": max(winds),
                "avg": round(sum(winds) / len(winds), 2)
            }
    
    return stats


def normalize_temperature(value: float, from_unit: str = "celsius", to_unit: str = "celsius") -> float:
    """
    Normaliza temperatura entre diferentes unidades.
    
    Args:
        value: Valor de temperatura
        from_unit: Unidad origen (celsius, fahrenheit, kelvin)
        to_unit: Unidad destino
    
    Returns:
        Temperatura en la unidad destino
    """
    # Convertir primero a Celsius
    if from_unit == "fahrenheit":
        celsius = (value - 32) * 5/9
    elif from_unit == "kelvin":
        celsius = value - 273.15
    else:
        celsius = value
    
    # Convertir a unidad destino
    if to_unit == "fahrenheit":
        return celsius * 9/5 + 32
    elif to_unit == "kelvin":
        return celsius + 273.15
    else:
        return celsius