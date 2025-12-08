"""
ClimAPI - Punto de entrada principal
Delega a backend.app.main o ejecuta script legacy.

Uso:
  python main.py api      -> Inicia FastAPI en http://localhost:8000
  python main.py legacy   -> Ejecuta script legacy (CLI)
  python main.py test     -> Ejecuta tests unitarios
  python main.py          -> Muestra ayuda
"""
import sys
import subprocess
from pathlib import Path

# Agregar backend al path ANTES de cualquier import
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def show_help():
    """Muestra ayuda."""
    print("""
╔══════════════════════════════════════════════════════════╗
║                    ClimAPI v1.0.0                        ║
║       Dashboard Meteorológico con FastAPI + Streamlit    ║
╚══════════════════════════════════════════════════════════╝

Comandos disponibles:
  python main.py api         -> Inicia API FastAPI (puerto 8000)
  python main.py dashboard   -> Inicia Dashboard Streamlit (puerto 8501)
  python main.py legacy      -> Ejecuta script legacy CLI
  python main.py test        -> Ejecuta tests unitarios
  python main.py             -> Muestra esta ayuda

Documentación API: http://localhost:8000/docs
Dashboard: http://localhost:8501
    """)

def run_api():
    """Inicia FastAPI."""
    try:
        import uvicorn
        print("🚀 Iniciando ClimAPI en http://localhost:8000")
        print("📚 Documentación: http://localhost:8000/docs")
        print("⏹️  Presiona Ctrl+C para detener\n")
        uvicorn.run(
            "backend.app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except ImportError:
        print("❌ Error: uvicorn no instalado.")
        print("   Ejecuta: pip install -r backend/requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error al iniciar API: {str(e)}")
        sys.exit(1)

def run_legacy():
    """Ejecuta script legacy."""
    try:
        from backend.app.scripts import legacy_main
        print("🔧 Ejecutando script legacy...\n")
        legacy_main.main()
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("   Asegúrate de tener todos los módulos en backend/app/scripts/")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Script interrumpido por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

def run_tests():
    """Ejecuta tests."""
    try:
        import pytest
        print("🧪 Ejecutando tests unitarios...\n")
        exit_code = pytest.main(["backend/tests/", "-v", "--tb=short"])
        sys.exit(exit_code)
    except ImportError:
        print("❌ Error: pytest no instalado.")
        print("   Ejecuta: pip install pytest pytest-cov pytest-asyncio")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


def run_dashboard():
    """Inicia Dashboard Streamlit."""
    try:
        import subprocess
        import streamlit  # Verificar que está instalado
        
        print("📊 Iniciando ClimAPI Dashboard en http://localhost:8501")
        print("📚 Documentación API: http://localhost:8000/docs")
        print("⏹️  Presiona Ctrl+C para detener\n")
        
        # Usar subprocess para ejecutar streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "dashboard/app.py"
        ], check=True)
    except ImportError as e:
        print("❌ Error: Streamlit no instalado.")
        print("   Ejecuta: pip install streamlit plotly")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al iniciar Streamlit: {str(e)}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Dashboard detenido")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            show_help()
        elif sys.argv[1] == "api":
            run_api()
        elif sys.argv[1] == "dashboard":
            run_dashboard()
        elif sys.argv[1] == "legacy":
            run_legacy()
        elif sys.argv[1] == "test":
            run_tests()
        elif sys.argv[1] in ["-h", "--help", "help"]:
            show_help()
        else:
            print(f"❌ Comando desconocido: {sys.argv[1]}")
            show_help()
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 ClimAPI detenido por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error fatal: {str(e)}")
        sys.exit(1)