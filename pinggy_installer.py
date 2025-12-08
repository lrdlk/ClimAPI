#!/usr/bin/env python3
"""
Instalador y gestor simple de Pinggy.io para ClimAPI
Acceso rápido con HTTPS público
"""

import subprocess
import sys
import os
import platform
from pathlib import Path


def check_ssh():
    """Verifica si SSH está disponible."""
    try:
        subprocess.run(["ssh", "-V"], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def install_openssh_windows():
    """Instala OpenSSH en Windows."""
    print("""
    ╔════════════════════════════════════════════════════════════════════════════╗
    ║                    📦 INSTALACIÓN DE OPENSSH REQUERIDA                     ║
    ╚════════════════════════════════════════════════════════════════════════════╝
    
    PowerShell se abrirá para instalar OpenSSH.
    
    Pasos:
    1. Haz clic en "Sí" cuando se pida confirmación
    2. Espera a que se complete la instalación
    3. Reinicia PowerShell
    4. Vuelve a ejecutar este script
    
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)
    
    input("Presiona Enter para continuar...")
    
    # Comando para instalar OpenSSH en Windows 10+
    ps_command = """
    Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0
    """
    
    # Ejecutar en nueva ventana de PowerShell con permisos admin
    subprocess.run([
        "powershell.exe",
        "-Command",
        ps_command
    ])
    
    print("\n✓ OpenSSH instalado (si es que no lo estaba)")
    print("✓ Cierra y reabre PowerShell")
    print("✓ Vuelve a ejecutar: python pinggy_installer.py\n")


def get_token():
    """Obtiene el token de Pinggy interactivamente."""
    print("""
    ╔════════════════════════════════════════════════════════════════════════════╗
    ║                 🔐 CONFIGURACIÓN DEL TOKEN PINGGY.IO                       ║
    ╚════════════════════════════════════════════════════════════════════════════╝
    
    🌐 Obtener Token (Gratis):
    
    1. Ve a: https://pinggy.io/
    2. Haz clic en "Sign Up" 
    3. Usa Email o GitHub
    4. Ve a Settings → SSH Token
    5. Copia el token (ej: user_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx)
    
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)
    
    token = input("\n📋 Pega tu token Pinggy (o presiona Enter para usar anónimo): ").strip()
    
    if token:
        save_token(token)
        return token
    else:
        print("ℹ️  Usando modo anónimo (URL temporal)")
        return None


def save_token(token):
    """Guarda el token en .env."""
    env_file = Path(".env")
    
    # Leer contenido actual
    content = env_file.read_text() if env_file.exists() else ""
    
    # Eliminar token anterior si existe
    lines = content.split("\n")
    lines = [l for l in lines if not l.startswith("PINGGY_TOKEN=")]
    
    # Agregar nuevo token
    lines.append(f"\n# Pinggy Configuration\nPINGGY_TOKEN={token}\n")
    
    # Guardar
    env_file.write_text("\n".join(lines))
    
    print(f"\n✅ Token guardado en .env")
    print(f"   Úsalo próximas veces automáticamente\n")


def quick_start():
    """Inicia rápidamente con Pinggy."""
    
    os.chdir(Path(__file__).parent)
    
    # Obtener token si no existe
    env_file = Path(".env")
    token = None
    
    if env_file.exists():
        content = env_file.read_text()
        for line in content.split("\n"):
            if line.startswith("PINGGY_TOKEN="):
                token = line.split("=", 1)[1].strip()
                break
    
    if not token:
        token = get_token()
    
    print("\n" + "="*80)
    print("🚀 INICIANDO DASHBOARD CON PINGGY.IO")
    print("="*80 + "\n")
    
    # Comando para abrir túnel usando pinggy.exe
    if token:
        # Usar comando pinggy.exe con token
        cmd = f'pinggy.exe -p 443 -R0:127.0.0.1:8501 -o StrictHostKeyChecking=no -o ServerAliveInterval=30 {token}@free.pinggy.io'
        print(f"✓ Usando token configurado")
    else:
        # Fallback a SSH si no hay token
        cmd = "ssh -R 0:localhost:8501 a.pinggy.io"
        print(f"ℹ️  Usando túnel temporal (URL cambiará en próximas sesiones)")
    
    print(f"\nEjecutando: {cmd}\n")
    print("Espera a ver: 'Port 8501 is forwarded to https://...'")
    print("━" * 80 + "\n")
    
    # Ejecutar comando
    try:
        subprocess.run(cmd, shell=True)
    except KeyboardInterrupt:
        print("\n\n✋ Túnel detenido\n")


def main():
    """Flujo principal."""
    
    print("""
    ╔════════════════════════════════════════════════════════════════════════════╗
    ║              🌐 CLIMAPI DASHBOARD - ACCESO REMOTO CON PINGGY 🌐            ║
    ║                        Expone tu Dashboard a Internet                      ║
    ╚════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Verificar SSH
    if not check_ssh():
        print("❌ SSH no está disponible\n")
        
        if platform.system() == "Windows":
            print("💡 Solución para Windows:\n")
            print("   Opción 1: Instalar OpenSSH desde Configuración")
            print("            Settings > Apps > Características Opcionales > OpenSSH Client\n")
            print("   Opción 2: Ejecutar comando (requiere admin):")
            print("            powershell.exe -Command \"Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0\"\n")
            
            choice = input("¿Instalar OpenSSH automáticamente? (s/n): ").strip().lower()
            if choice == 's':
                install_openssh_windows()
            sys.exit(1)
        else:
            print("💡 Instala OpenSSH con:")
            if platform.system() == "Darwin":
                print("   brew install openssh")
            else:
                print("   sudo apt-get install openssh-client")
            sys.exit(1)
    
    print("✅ SSH disponible\n")
    
    # Elegir acción
    print("¿Qué deseas hacer?\n")
    print("1. 🚀 Iniciar Dashboard con Pinggy (acceso público HTTPS)")
    print("2. 🔐 Configurar/cambiar Token Pinggy")
    print("3. 📊 Iniciar Dashboard solo local (http://localhost:8501)")
    print("4. ❌ Salir\n")
    
    choice = input("Selecciona (1-4): ").strip()
    
    if choice == "1":
        quick_start()
    elif choice == "2":
        get_token()
        print("✅ Ahora usa opción 1 para iniciar con el nuevo token")
    elif choice == "3":
        os.chdir(Path(__file__).parent)
        print("\n🎨 Iniciando Dashboard Streamlit...\n")
        subprocess.run([".venv\\Scripts\\streamlit.exe", "run", "dashboard/app.py"])
    elif choice == "4":
        print("\n👋 Hasta luego!")
    else:
        print("❌ Opción no válida")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrumpido")
        sys.exit(0)
