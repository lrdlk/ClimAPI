"""
API route definitions.
"""

# Placeholders para routers (se implementarán después)
from fastapi import APIRouter

weather_router = APIRouter()
locations_router = APIRouter()
health_router = APIRouter()

@weather_router.get("/")
async def weather_info():
    return {"message": "Weather endpoints"}

@locations_router.get("/")
async def locations_info():
    return {"message": "Locations endpoints"}

@health_router.get("/")
async def health_info():
    return {"message": "Health endpoints"}

__all__ = ["weather_router", "locations_router", "health_router"]