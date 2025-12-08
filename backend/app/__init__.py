"""
Backend application - ClimAPI
"""
from .config import settings
from .main import app

__all__ = ["app", "settings"]