#!/usr/bin/env python3
"""
Integración de Pinggy.io para exposición segura del dashboard ClimAPI.
Permite acceder al dashboard desde internet con HTTPS.
"""

import subprocess
import sys
import os
import time
import json
from pathlib import Path
from typing import Dict, Optional

# Configuración de Pinggy
PINGGY_TUNNEL_TYPE = "http"  # http, ssh, tcp
PINGGY_PORT = 8501  # Puerto del dashboard Streamlit
PINGGY_CONFIG_FILE = "pinggy_config.json"

class PinggyTunnel:
    """Gestor de túneles Pinggy.io para ClimAPI."""
    
    def __init__(self, token: Optional[str] = None):
        """
        Inicializa el gestor de túneles.
        
        Args:
            token: Token de Pinggy (opcional, puede venir de variable de entorno)
        """
        self.token = token or os.getenv("PINGGY_TOKEN", "")
        self.dashboard_port = PINGGY_PORT
        self.tunnel_url = None
        self.process = None
    
    def start_tunnel(self) -> bool:
        """
        Inicia un túnel Pinggy hacia el dashboard.
        
        Returns:
            True si el túnel se inició correctamente
        """
        try:
            print("\n" + "="*70)
            print("🌐 INICIANDO TÚNEL PINGGY.IO")
            print("="*70)
            
            # Comando para iniciar el túnel usando pinggy.exe
            if self.token:
                cmd = [
                    "pinggy.exe",
                    "-p", "443",
                    "-R0:127.0.0.1:8501",
                    "-o", "StrictHostKeyChecking=no",
                    "-o", "ServerAliveInterval=30",
                    f"{self.token}@free.pinggy.io"
                ]
                print(f"✓ Token Pinggy configurado")
            else:
                # Fallback a SSH si no hay pinggy.exe
                cmd = [
                    "ssh",
                    "-R",
                    f"0:localhost:{self.dashboard_port}",
                    "a.pinggy.io"
                ]
                print("⚠️  Sin token - generando túnel temporal")
                print("   Para obtener un token permanente:")
                print("   1. Ve a https://pinggy.io/")
                print("   2. Inicia sesión/crea cuenta")
                print("   3. Copia tu token")
                print("   4. Exporta: $env:PINGGY_TOKEN='tu_token'")
            
            print(f"\n✓ Exponiendo puerto {self.dashboard_port} a través de Pinggy")
            print("  Esperando URL pública...\n")
            
            # Iniciar proceso
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Esperar a que se muestre la URL
            timeout = 15
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                line = self.process.stdout.readline()
                if line:
                    print(f"[Pinggy] {line.strip()}")
                    
                    # Buscar la URL pública en la salida
                    if "https://" in line or "http://" in line:
                        # Extraer URL
                        for word in line.split():
                            if "pinggy" in word.lower() and ("https://" in word or "http://" in word):
                                self.tunnel_url = word.strip()
                                break
                
                if self.tunnel_url:
                    break
                
                time.sleep(0.1)
            
            if self.tunnel_url:
                print(f"\n{'='*70}")
                print(f"✅ TÚNEL ACTIVO")
                print(f"{'='*70}")
                print(f"\n🔗 URL Pública (HTTPS):")
                print(f"   {self.tunnel_url}")
                print(f"\n📱 Acceso:")
                print(f"   • Desde internet: {self.tunnel_url}")
                print(f"   • Localmente: http://localhost:{self.dashboard_port}")
                print(f"\n{'='*70}\n")
                return True
            else:
                print("⚠️  No se detectó URL pública. El túnel puede estar iniciándose...")
                print("   Monitorea la salida anterior para la URL.\n")
                return True  # El proceso está corriendo
                
        except FileNotFoundError as e:
            print(f"\n❌ No se encontró: {e.filename}")
            print("   Asegúrate de que pinggy.exe o SSH están disponibles")
            return False
        except Exception as e:
            print(f"\n❌ Error al iniciar túnel: {e}")
            return False
    
    def save_config(self) -> None:
        """Guarda la configuración del túnel en un archivo."""
        config = {
            "token": self.token,
            "port": self.dashboard_port,
            "tunnel_url": self.tunnel_url,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open(PINGGY_CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
        
        print(f"✓ Configuración guardada en {PINGGY_CONFIG_FILE}")
    
    def stop_tunnel(self) -> None:
        """Detiene el túnel Pinggy."""
        if self.process:
            print("\n🛑 Deteniendo túnel Pinggy...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
                print("✓ Túnel detenido correctamente")
            except subprocess.TimeoutExpired:
                self.process.kill()
                print("✓ Túnel forzado a detener")


def main():
    """Función principal - integración completa."""
    
    print("""
    ╔════════════════════════════════════════════════════════════════════════════╗
    ║                  🌐 CLIMAPI DASHBOARD CON PINGGY.IO 🌐                    ║
    ║                        Acceso Remoto Seguro (HTTPS)                        ║
    ╚════════════════════════════════════════════════════════════════════════════╝
    
    📋 OPCIONES:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    1. Lanzar Dashboard + Túnel Pinggy
       → Expone automáticamente con URL pública HTTPS
    
    2. Lanzar solo Dashboard
       → Local en http://localhost:8501
    
    3. Configurar Token Pinggy
       → Para usar túneles con dominio permanente
    
    4. Salir
    
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)
    
    choice = input("Selecciona opción (1-4): ").strip()
    
    if choice == "1":
        launch_with_tunnel()
    elif choice == "2":
        launch_dashboard_only()
    elif choice == "3":
        configure_token()
    elif choice == "4":
        print("\n👋 Hasta luego!")
        sys.exit(0)
    else:
        print("❌ Opción no válida")
        sys.exit(1)


def launch_with_tunnel():
    """Lanza dashboard con túnel Pinggy."""
    print("\n🚀 Preparando Dashboard con Túnel Pinggy...")
    
    # Crear instancia de túnel
    tunnel = PinggyTunnel()
    
    # Iniciar túnel en thread separado
    print("⏳ Iniciando túnel...")
    tunnel_started = tunnel.start_tunnel()
    
    if not tunnel_started:
        print("❌ No se pudo iniciar el túnel")
        sys.exit(1)
    
    # Dar tiempo al túnel a establecerse
    time.sleep(2)
    
    # Iniciar dashboard
    print("\n🎨 Iniciando Dashboard Streamlit...")
    print("   (El dashboard abrirá en tu navegador)\n")
    
    try:
        # Ejecutar Streamlit
        subprocess.run([
            ".venv/Scripts/streamlit.exe",
            "run",
            "dashboard/app.py"
        ])
    except KeyboardInterrupt:
        print("\n\n✋ Dashboard detenido")
    finally:
        # Detener túnel
        tunnel.stop_tunnel()


def launch_dashboard_only():
    """Lanza solo el dashboard sin túnel."""
    print("\n🎨 Iniciando Dashboard Streamlit...")
    print("   Local: http://localhost:8501\n")
    
    try:
        subprocess.run([
            ".venv/Scripts/streamlit.exe",
            "run",
            "dashboard/app.py"
        ])
    except KeyboardInterrupt:
        print("\n\n✋ Dashboard detenido")
    except FileNotFoundError:
        print("❌ Streamlit no encontrado. Instala: pip install streamlit")
        sys.exit(1)


def configure_token():
    """Configura el token de Pinggy."""
    print("""
    ╔════════════════════════════════════════════════════════════════════════════╗
    ║                      🔐 CONFIGURACIÓN DE PINGGY.IO                         ║
    ╚════════════════════════════════════════════════════════════════════════════╝
    
    🌐 Para obtener tu token:
    
    1. Ve a https://pinggy.io/
    2. Inicia sesión (gratis)
    3. Ve a Settings/Profile
    4. Copia tu "SSH Token"
    5. Pégalo a continuación
    
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)
    
    token = input("Ingresa tu token Pinggy: ").strip()
    
    if not token:
        print("❌ Token vacío")
        return
    
    # Guardar en variable de entorno
    os.environ["PINGGY_TOKEN"] = token
    
    # También guardar en archivo .env
    env_file = Path(".env")
    env_content = env_file.read_text() if env_file.exists() else ""
    
    if "PINGGY_TOKEN" not in env_content:
        env_content += f"\n\n# Pinggy Configuration\nPINGGY_TOKEN={token}\n"
        env_file.write_text(env_content)
        print(f"\n✅ Token guardado en .env")
    else:
        # Actualizar token existente
        lines = env_content.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("PINGGY_TOKEN="):
                lines[i] = f"PINGGY_TOKEN={token}"
                break
        env_file.write_text("\n".join(lines))
        print(f"\n✅ Token actualizado en .env")
    
    print("\n💡 Ahora puedes usar la opción 1 para lanzar con túnel")


if __name__ == "__main__":
    # Cambiar a directorio del proyecto
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrumpido por el usuario")
        sys.exit(0)
