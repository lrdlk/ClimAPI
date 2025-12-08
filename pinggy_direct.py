#!/usr/bin/env python3
"""
Gestor de Pinggy.io con soporte para pinggy.exe
Integramos el comando directo: pinggy.exe -p 443 -R0:127.0.0.1:8501 ...
"""

import subprocess
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Token Pinggy desde .env o variable de entorno
PINGGY_TOKEN = os.getenv("PINGGY_TOKEN", "Fm4hH7kZ8sz+force")  # Por defecto el tuyo

class PinggyManager:
    """Gestor de túneles Pinggy usando pinggy.exe"""
    
    def __init__(self, token: str = None, port: int = 8501):
        """
        Inicializa el gestor.
        
        Args:
            token: Token Pinggy (default: del .env o variable de entorno)
            port: Puerto local del dashboard (default: 8501)
        """
        self.token = token or PINGGY_TOKEN
        self.port = port
        self.process = None
    
    def get_command(self) -> str:
        """Obtiene el comando Pinggy completo."""
        return (
            f'pinggy.exe -p 443 '
            f'-R0:127.0.0.1:{self.port} '
            f'-o StrictHostKeyChecking=no '
            f'-o ServerAliveInterval=30 '
            f'{self.token}@free.pinggy.io'
        )
    
    def start(self) -> bool:
        """Inicia el túnel Pinggy."""
        
        print("""
        ╔════════════════════════════════════════════════════════════════════════════╗
        ║                  🌐 PINGGY.IO TUNNEL - CLIMAPI DASHBOARD                   ║
        ╚════════════════════════════════════════════════════════════════════════════╝
        """)
        
        cmd = self.get_command()
        
        print(f"\n🔗 Token:      {self.token[:20]}...")
        print(f"🚪 Puerto:     {self.port}")
        print(f"🌐 Destino:    free.pinggy.io")
        print(f"\n━" * 80)
        print(f"\n📡 Comando:")
        print(f"   {cmd}\n")
        print(f"━" * 80)
        print(f"\n⏳ Iniciando túnel...\n")
        
        try:
            # Ejecutar comando
            self.process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Mostrar output en tiempo real
            print("📊 Output del túnel:\n")
            for line in self.process.stdout:
                print(line.rstrip())
                
                # Detectar cuando el túnel está listo
                if "free.pinggy.io" in line and "http" in line:
                    print("\n✅ TÚNEL ACTIVO - URL arriba")
            
            return True
            
        except FileNotFoundError:
            print("❌ pinggy.exe no encontrado")
            print("\n💡 Soluciones:")
            print("   1. Descargar pinggy.exe desde: https://pinggy.io/")
            print("   2. O usar SSH: ssh -R 0:localhost:8501 a.pinggy.io")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def stop(self):
        """Detiene el túnel."""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()


def main():
    """Flujo principal."""
    
    print("""
    ╔════════════════════════════════════════════════════════════════════════════╗
    ║                  🌐 CLIMAPI - PINGGY.IO TUNNEL MANAGER                     ║
    ╚════════════════════════════════════════════════════════════════════════════╝
    
    Opciones:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    1. 🚀 Iniciar Dashboard + Túnel Pinggy
    2. 🌐 Solo Túnel Pinggy
    3. 📊 Solo Dashboard Streamlit
    4. ⚙️  Ver Configuración
    5. 🔑 Cambiar Token
    6. ❌ Salir
    
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)
    
    choice = input("Selecciona (1-6): ").strip()
    
    manager = PinggyManager()
    
    if choice == "1":
        print("\n🚀 Iniciando Dashboard + Túnel...")
        print("   Terminal 1: Túnel Pinggy")
        print("   Terminal 2: Dashboard Streamlit")
        print("\n📌 Abre otra terminal y ejecuta:")
        print("   .venv\\Scripts\\streamlit.exe run dashboard/app.py\n")
        input("Presiona Enter para iniciar el túnel...")
        manager.start()
    
    elif choice == "2":
        manager.start()
    
    elif choice == "3":
        print("\n🎨 Iniciando Dashboard Streamlit...\n")
        try:
            subprocess.run([".venv\\Scripts\\streamlit.exe", "run", "dashboard/app.py"])
        except KeyboardInterrupt:
            print("\n✋ Dashboard detenido")
    
    elif choice == "4":
        print(f"\n⚙️  CONFIGURACIÓN ACTUAL\n")
        print(f"   Token:     {manager.token[:20]}...")
        print(f"   Puerto:    {manager.port}")
        print(f"   Destino:   free.pinggy.io")
        print(f"\n   Comando:")
        print(f"   {manager.get_command()}\n")
    
    elif choice == "5":
        token = input("\n🔑 Nuevo token Pinggy: ").strip()
        if token:
            manager.token = token
            
            # Guardar en .env
            env_file = Path(".env")
            content = env_file.read_text() if env_file.exists() else ""
            
            lines = content.split("\n")
            lines = [l for l in lines if not l.startswith("PINGGY_TOKEN=")]
            lines.append(f"\nPINGGY_TOKEN={token}\n")
            
            env_file.write_text("\n".join(lines))
            print(f"\n✅ Token guardado en .env")
        else:
            print("❌ Token vacío")
    
    elif choice == "6":
        print("\n👋 Hasta luego!")
        sys.exit(0)
    
    else:
        print("❌ Opción no válida")
        sys.exit(1)


if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrumpido")
        sys.exit(0)
