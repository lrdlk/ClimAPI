import axios from 'axios'
import { WeatherResponse, LocationInfo, HealthResponse, CacheStats } from './types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para manejar errores
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error)
    throw error
  }
)

export const fetchWeatherData = async (location: LocationInfo): Promise<WeatherResponse> => {
  try {
    const response = await api.post('/api/v1/weather/current', {
      latitude: location.latitude,
      longitude: location.longitude,
      timezone: location.timezone,
    })
    return response.data
  } catch (error) {
    console.error('Error fetching weather data:', error)
    throw new Error('No se pudieron obtener los datos meteorológicos')
  }
}

export const fetchPopularLocations = async (): Promise<LocationInfo[]> => {
  try {
    const response = await api.get('/api/v1/locations/popular')
    return response.data
  } catch (error) {
    console.error('Error fetching popular locations:', error)
    throw new Error('No se pudieron obtener las ubicaciones populares')
  }
}

export const fetchDefaultLocation = async (): Promise<LocationInfo> => {
  try {
    const response = await api.get('/api/v1/locations/default')
    return response.data
  } catch (error) {
    console.error('Error fetching default location:', error)
    throw new Error('No se pudo obtener la ubicación por defecto')
  }
}

export const fetchHealthStatus = async (): Promise<HealthResponse> => {
  try {
    const response = await api.get('/api/v1/health')
    return response.data
  } catch (error) {
    console.error('Error fetching health status:', error)
    throw new Error('No se pudo verificar el estado del servicio')
  }
}

export const fetchCacheStats = async (): Promise<CacheStats> => {
  try {
    const response = await api.get('/api/v1/cache/stats')
    return response.data
  } catch (error) {
    console.error('Error fetching cache stats:', error)
    throw new Error('No se pudieron obtener las estadísticas de caché')
  }
}

export const clearCache = async (): Promise<{ message: string; timestamp: string }> => {
  try {
    const response = await api.delete('/api/v1/cache')
    return response.data
  } catch (error) {
    console.error('Error clearing cache:', error)
    throw new Error('No se pudo limpiar la caché')
  }
}

export const searchLocations = async (query: string, limit: number = 10): Promise<LocationInfo[]> => {
  try {
    const response = await api.get('/api/v1/locations/search', {
      params: { query, limit },
    })
    return response.data
  } catch (error) {
    console.error('Error searching locations:', error)
    throw new Error('No se pudo buscar ubicaciones')
  }
}