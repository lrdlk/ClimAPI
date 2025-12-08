"""
FastAPI Backend - ClimAPI
Endpoints para datos meteorológicos con múltiples fuentes.
"""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

# Importar configuración
from .config import settings

# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Crear app FastAPI
app = FastAPI(
    title="ClimAPI",
    description="API de datos meteorológicos con 8+ fuentes",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
origins = settings.ALLOWED_ORIGINS
if isinstance(origins, str):
    origins = [o.strip() for o in origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas básicas
@app.get("/")
async def root():
    """Endpoint raíz - Info del servicio."""
    return {
        "service": "ClimAPI",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "ClimAPI",
        "version": "1.0.0"
    }


@app.on_event("startup")
async def startup_event():
    """Evento al iniciar la aplicación."""
    logger.info("=" * 60)
    logger.info("🚀 ClimAPI iniciado correctamente")
    logger.info(f"📚 Documentación en: http://localhost:{settings.PORT}/docs")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Evento al cerrar la aplicación."""
    logger.info("👋 ClimAPI detenido")


# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Manejador general de excepciones."""
    logger.error(f"Error no manejado: {str(exc)}")
    return {
        "error": "Internal Server Error",
        "detail": str(exc) if settings.DEBUG else "An error occurred"
    }