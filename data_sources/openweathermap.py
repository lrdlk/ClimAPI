import requests

city = input ("ingrese Ciudad a consultar : ")
api_key = "32bdf300d39d022bb540ccbb5ea50970"
url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=es"
response = requests.get(url)
data = response.json()

temp = data["main"]["temp"]
wind_speed = data["wind"]["speed"]

latitude = data["coord"]["lat"]
longitude = data["coord"]["lon"]

description = data["weather"][0]["description"]

print(f"Ciudad: {city}")
print(f"Temperatura: {temp}°C")
print(f"Velocidad del viento: {wind_speed} m/s")
print(f"Latitud: {latitude}")
print(f"Longitud: {longitude}")
print(f"Descripción: {description}")