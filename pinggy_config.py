#!/usr/bin/env python3
"""
Integración de Pinggy.io - Variables y configuración
Se importa en otros módulos para acceder a la configuración del túnel
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de Pinggy
PINGGY_TOKEN: Optional[str] = os.getenv("PINGGY_TOKEN", None)
PINGGY_ENABLED: bool = bool(PINGGY_TOKEN)
PINGGY_PORT: int = int(os.getenv("PINGGY_PORT", "8501"))
PINGGY_HOST: str = os.getenv("PINGGY_HOST", "a.pinggy.io")

# URLs
PINGGY_DOCS_URL = "https://pinggy.io/"
PINGGY_DASHBOARD_URL = "https://pinggy.io/dashboard"

# Información del túnel
TUNNEL_INFO = {
    "service": "Pinggy.io",
    "type": "HTTP",
    "protocol": "HTTPS",
    "port": PINGGY_PORT,
    "status": "ENABLED" if PINGGY_ENABLED else "DISABLED",
    "token_configured": PINGGY_ENABLED,
}


class PinggyConfig:
    """Gestor de configuración de Pinggy."""
    
    @staticmethod
    def get_tunnel_url() -> Optional[str]:
        """
        Obtiene la URL del túnel desde la configuración.
        
        Returns:
            URL pública del túnel o None si no está configurado
        """
        if not PINGGY_ENABLED:
            return None
        
        return f"https://{PINGGY_TOKEN}@a.pinggy.io"
    
    @staticmethod
    def get_local_url() -> str:
        """
        Obtiene la URL local del dashboard.
        
        Returns:
            URL local: http://localhost:8501
        """
        return f"http://localhost:{PINGGY_PORT}"
    
    @staticmethod
    def get_ssh_command() -> str:
        """
        Genera el comando SSH para iniciar el túnel.
        
        Returns:
            Comando SSH completo
        """
        if PINGGY_TOKEN:
            return f"ssh -R 0:localhost:{PINGGY_PORT} {PINGGY_TOKEN}@{PINGGY_HOST}"
        else:
            return f"ssh -R 0:localhost:{PINGGY_PORT} {PINGGY_HOST}"
    
    @staticmethod
    def is_configured() -> bool:
        """Verifica si Pinggy está configurado."""
        return PINGGY_ENABLED
    
    @staticmethod
    def get_config_dict() -> dict:
        """Obtiene la configuración completa como diccionario."""
        return {
            "enabled": PINGGY_ENABLED,
            "token_configured": bool(PINGGY_TOKEN),
            "port": PINGGY_PORT,
            "host": PINGGY_HOST,
            "local_url": PinggyConfig.get_local_url(),
            "ssh_command": PinggyConfig.get_ssh_command(),
            "docs_url": PINGGY_DOCS_URL,
        }


def get_tunnel_info() -> dict:
    """Obtiene información del túnel para mostrar en UI."""
    info = {
        "service": "Pinggy.io",
        "status": "✅ Configurado" if PINGGY_ENABLED else "⚙️  No configurado",
        "local_url": PinggyConfig.get_local_url(),
        "remote_url": "🔗 Ejecutar: python pinggy_installer.py",
        "documentation": PINGGY_DOCS_URL,
    }
    return info


# Exportar para uso en otros módulos
__all__ = [
    "PINGGY_TOKEN",
    "PINGGY_ENABLED",
    "PINGGY_PORT",
    "PINGGY_HOST",
    "PinggyConfig",
    "TUNNEL_INFO",
    "get_tunnel_info",
]

if __name__ == "__main__":
    # Mostrar configuración actual
    print("\n🌐 PINGGY CONFIGURATION")
    print("=" * 60)
    
    config = PinggyConfig.get_config_dict()
    for key, value in config.items():
        print(f"  {key:20s}: {value}")
    
    print("\n✓ Configuration loaded successfully")
