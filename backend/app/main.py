"""
FastAPI Backend - ClimAPI
Endpoints para datos meteorológicos con múltiples fuentes.
"""

import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import time

# Importar configuración
from .config import settings

# Importar utilidades de logging y tracing
from .utils.logger import (
    setup_logging, 
    get_logger, 
    get_tracer, 
    get_metrics_collector,
    trace_id_var
)

# Configurar logging con tracing
log_file = Path(settings.LOG_FILE) if hasattr(settings, 'LOG_FILE') else None
setup_logging(
    level=settings.LOG_LEVEL,
    log_file=log_file,
    structured=getattr(settings, 'STRUCTURED_LOGS', False)
)
logger = get_logger(__name__)
tracer = get_tracer("climapi")
metrics = get_metrics_collector()

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

# Add tracing middleware
@app.middleware("http")
async def trace_requests(request: Request, call_next):
    """Middleware to trace all HTTP requests."""
    import uuid
    
    # Generate or extract trace ID
    trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4()))
    trace_id_var.set(trace_id)
    
    # Record request start
    start_time = time.time()
    logger.info(f"→ {request.method} {request.url.path}", extra={
        'extra_fields': {
            'method': request.method,
            'path': request.url.path,
            'trace_id': trace_id
        }
    })
    
    # Process request
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Record metrics
        metrics.record("http_request_duration", duration, {
            'method': request.method,
            'path': request.url.path,
            'status': str(response.status_code)
        })
        
        # Log response
        logger.info(f"✓ {request.method} {request.url.path} - {response.status_code} ({duration:.3f}s)", extra={
            'extra_fields': {
                'method': request.method,
                'path': request.url.path,
                'status_code': response.status_code,
                'duration': duration,
                'trace_id': trace_id
            }
        })
        
        # Add trace ID to response headers
        response.headers["X-Trace-ID"] = trace_id
        return response
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"✗ {request.method} {request.url.path} failed ({duration:.3f}s): {str(e)}", extra={
            'extra_fields': {
                'method': request.method,
                'path': request.url.path,
                'duration': duration,
                'error': str(e),
                'trace_id': trace_id
            }
        })
        raise

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