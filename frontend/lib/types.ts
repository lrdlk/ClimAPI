export interface WeatherData {
  time: string
  temperature: number
  humidity: number
  precipitation: number
  wind_speed: number
}

export interface LocationInfo {
  latitude: number
  longitude: number
  timezone: string
  city: string
  country: string
}

export interface WeatherResponse {
  location: LocationInfo
  data: WeatherData[]
  source: string
  timestamp: string
}

export interface LocationRequest {
  latitude: number
  longitude: number
  timezone: string
}

export interface HealthResponse {
  status: string
  service: string
  timestamp: string
}

export interface CacheStats {
  entries: number
  size: number
  path: string
  ttl_minutes: number
}