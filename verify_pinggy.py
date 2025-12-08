#!/usr/bin/env python3
"""
Verificador de integración de Pinggy.io
Confirma que todo esté listo para usar
"""

import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def check_ssh():
    """Verifica disponibilidad de SSH."""
    try:
        subprocess.run(["ssh", "-V"], capture_output=True, check=True)
        return True, "SSH disponible"
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False, "SSH no disponible (requiere OpenSSH Client)"


def check_python():
    """Verifica versión de Python."""
    version = f"{sys.version_info.major}.{sys.version_info.minor}"
    if sys.version_info >= (3, 8):
        return True, f"Python {version} ✅"
    return False, f"Python {version} (requiere 3.8+)"


def check_streamlit():
    """Verifica Streamlit."""
    try:
        import streamlit
        return True, f"Streamlit {streamlit.__version__} ✅"
    except ImportError:
        return False, "Streamlit no instalado"


def check_pinggy_token():
    """Verifica token Pinggy."""
    token = os.getenv("PINGGY_TOKEN", "")
    if token:
        masked = token[:10] + "..." if len(token) > 10 else token
        return True, f"Token configurado: {masked}"
    else:
        return False, "Token no configurado (opcional)"


def check_files_exist():
    """Verifica que los archivos de Pinggy existan."""
    files = [
        "pinggy_installer.py",
        "run_with_pinggy.py",
        "pinggy_config.py",
        "PINGGY_QUICKSTART.md",
        "PINGGY_GUIDE.md",
        "PINGGY_INTEGRATION.md",
    ]
    
    missing = []
    for f in files:
        if not Path(f).exists():
            missing.append(f)
    
    if not missing:
        return True, f"✅ Todos los archivos presentes ({len(files)})"
    else:
        return False, f"❌ Archivos faltantes: {', '.join(missing)}"


def check_dashboard_files():
    """Verifica que el dashboard esté listo."""
    dashboard_files = [
        "dashboard/app.py",
        ".env",
    ]
    
    missing = []
    for f in dashboard_files:
        if not Path(f).exists():
            missing.append(f)
    
    if not missing:
        return True, "Dashboard listo"
    else:
        return False, f"Archivos faltantes: {', '.join(missing)}"


def main():
    """Verificación completa."""
    
    print("""
    ╔════════════════════════════════════════════════════════════════════════════╗
    ║              ✅ VERIFICADOR DE INTEGRACIÓN PINGGY.IO                       ║
    ╚════════════════════════════════════════════════════════════════════════════╝
    """)
    
    checks = [
        ("Python", check_python),
        ("SSH", check_ssh),
        ("Streamlit", check_streamlit),
        ("Token Pinggy", check_pinggy_token),
        ("Archivos Pinggy", check_files_exist),
        ("Dashboard", check_dashboard_files),
    ]
    
    results = []
    print("🔍 Verificando componentes...\n")
    
    for name, checker in checks:
        success, message = checker()
        status = "✅" if success else "⚠️ "
        print(f"  {status} {name:20s} : {message}")
        results.append((name, success, message))
    
    print("\n" + "="*80)
    
    # Resumen
    total = len(results)
    passed = sum(1 for _, success, _ in results if success)
    
    print(f"\n📊 RESULTADO: {passed}/{total} verificaciones pasadas")
    
    # Recomendaciones
    if passed == total:
        print("\n✅ SISTEMA LISTO PARA USAR\n")
        print("🚀 Para comenzar:")
        print("   1. Ejecuta: python pinggy_installer.py")
        print("   2. Selecciona opción 1")
        print("   3. Comparte la URL pública\n")
        return 0
    
    else:
        print("\n⚠️  PROBLEMAS DETECTADOS:\n")
        
        for name, success, message in results:
            if not success:
                print(f"  ❌ {name}: {message}")
        
        print("\n💡 SOLUCIONES:\n")
        
        # Sugerencias basadas en fallos
        for name, success, message in results:
            if not success:
                if "SSH" in name:
                    print("  SSH:")
                    print("    • Windows: Configuración > Apps > Características Opcionales > OpenSSH Client")
                    print("    • Linux/Mac: $ sudo apt-get install openssh-client\n")
                
                elif "Streamlit" in name:
                    print("  Streamlit:")
                    print("    • pip install streamlit\n")
                
                elif "Token" in name and "no configurado" in message:
                    print("  Token Pinggy (opcional):")
                    print("    • Ve a https://pinggy.io/")
                    print("    • Sign up (gratis)")
                    print("    • Settings > SSH Token")
                    print("    • Pega en: $env:PINGGY_TOKEN='token'\n")
                
                elif "Archivos" in name:
                    print("  Archivos Pinggy:")
                    print("    • Los archivos de Pinggy deben estar en el directorio raíz\n")
        
        return 1


if __name__ == "__main__":
    exit_code = main()
    
    # Pausa antes de cerrar
    if exit_code != 0:
        input("\nPresiona Enter para cerrar...")
    
    sys.exit(exit_code)
