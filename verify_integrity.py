"""
Script de verificación de integridad del proyecto ClimAPI
Audita estructura, imports y funcionalidad
"""
import sys
from pathlib import Path
import importlib
from typing import Dict, List, Tuple

# Agregar backend al path
sys.path.insert(0, str(Path.cwd()))

class IntegrityChecker:
    """Verifica la integridad del proyecto ClimAPI."""
    
    def __init__(self):
        self.results = {
            "structure": [],
            "imports": [],
            "functionality": [],
            "summary": {}
        }
        self.errors = []
        self.warnings = []
    
    def check_structure(self):
        """Verifica la estructura de directorios y archivos."""
        print("\n" + "="*60)
        print("1️⃣  VERIFICACIÓN DE ESTRUCTURA")
        print("="*60 + "\n")
        
        required_files = {
            "Raíz": [
                "main.py",
                "requirements.txt",
                ".env",
                "backend/requirements.txt"
            ],
            "Backend": [
                "backend/__init__.py",
                "backend/app/__init__.py",
                "backend/app/main.py",
                "backend/app/config.py",
                "backend/app/models.py"
            ],
            "Services": [
                "backend/app/services/__init__.py",
                "backend/app/services/open_meteo.py"
            ],
            "Processors": [
                "backend/app/processors/__init__.py",
                "backend/app/processors/storage.py",
                "backend/app/processors/transform.py"
            ],
            "Scripts": [
                "backend/app/scripts/__init__.py",
                "backend/app/scripts/legacy_main.py"
            ],
            "API": [
                "backend/app/api/__init__.py"
            ]
        }
        
        for category, files in required_files.items():
            print(f"📁 {category}:")
            for file_path in files:
                full_path = Path(file_path)
                if full_path.exists():
                    print(f"  ✓ {file_path}")
                    self.results["structure"].append((file_path, True))
                else:
                    print(f"  ✗ {file_path} FALTA")
                    self.results["structure"].append((file_path, False))
                    self.errors.append(f"Archivo faltante: {file_path}")
            print()
    
    def check_imports(self):
        """Verifica que los imports funcionen correctamente."""
        print("="*60)
        print("2️⃣  VERIFICACIÓN DE IMPORTS")
        print("="*60 + "\n")
        
        import_tests = {
            "Config": "from backend.app.config import settings",
            "Main App": "from backend.app.main import app",
            "Open-Meteo": "from backend.app.services.open_meteo import get_weather_data, validate_coordinates",
            "Storage": "from backend.app.processors.storage import save_to_csv, save_to_json, CacheManager",
            "Transform": "from backend.app.processors.transform import process_weather_data, calculate_statistics",
            "Legacy": "from backend.app.scripts.legacy_main import main"
        }
        
        for name, import_stmt in import_tests.items():
            try:
                exec(import_stmt)
                print(f"  ✓ {name}")
                self.results["imports"].append((name, True))
            except ImportError as e:
                print(f"  ✗ {name}: {str(e)}")
                self.results["imports"].append((name, False))
                self.errors.append(f"Import error en {name}: {str(e)}")
            except Exception as e:
                print(f"  ⚠ {name}: {str(e)}")
                self.results["imports"].append((name, False))
                self.warnings.append(f"Error en {name}: {str(e)}")
        
        print()
    
    def check_functionality(self):
        """Verifica que los módulos funcionen correctamente."""
        print("="*60)
        print("3️⃣  VERIFICACIÓN DE FUNCIONALIDAD")
        print("="*60 + "\n")
        
        try:
            from backend.app.config import settings
            print(f"  ✓ Settings cargado: HOST={settings.HOST}, PORT={settings.PORT}")
            self.results["functionality"].append(("Settings", True))
        except Exception as e:
            print(f"  ✗ Settings: {str(e)}")
            self.results["functionality"].append(("Settings", False))
            self.errors.append(f"Error en Settings: {str(e)}")
        
        try:
            from backend.app.main import app
            print(f"  ✓ FastAPI app creada: {app.title} v{app.version}")
            self.results["functionality"].append(("FastAPI App", True))
        except Exception as e:
            print(f"  ✗ FastAPI App: {str(e)}")
            self.results["functionality"].append(("FastAPI App", False))
            self.errors.append(f"Error en FastAPI: {str(e)}")
        
        try:
            from backend.app.services.open_meteo import validate_coordinates
            assert validate_coordinates(6.2442, -75.5812) == True
            assert validate_coordinates(91, 0) == False
            print(f"  ✓ Validación de coordenadas funciona")
            self.results["functionality"].append(("Coordinates Validation", True))
        except Exception as e:
            print(f"  ✗ Validación de coordenadas: {str(e)}")
            self.results["functionality"].append(("Coordinates Validation", False))
            self.errors.append(f"Error en validación: {str(e)}")
        
        try:
            from backend.app.processors.storage import CacheManager
            cache = CacheManager(ttl_minutes=15)
            cache.set("test_key", {"value": 123})
            result = cache.get("test_key")
            assert result == {"value": 123}
            cache.clear()
            print(f"  ✓ CacheManager funciona correctamente")
            self.results["functionality"].append(("CacheManager", True))
        except Exception as e:
            print(f"  ✗ CacheManager: {str(e)}")
            self.results["functionality"].append(("CacheManager", False))
            self.errors.append(f"Error en CacheManager: {str(e)}")
        
        try:
            from backend.app.processors.transform import process_weather_data
            test_data = {
                "current_weather": {
                    "temperature": 22.5,
                    "windspeed": 3.2,
                    "time": "2025-12-07T14:00"
                },
                "latitude": 6.2442,
                "longitude": -75.5812
            }
            result = process_weather_data(test_data)
            assert result["temperature"] == 22.5
            assert result["source"] == "open_meteo"
            print(f"  ✓ Transform funciona correctamente")
            self.results["functionality"].append(("Transform", True))
        except Exception as e:
            print(f"  ✗ Transform: {str(e)}")
            self.results["functionality"].append(("Transform", False))
            self.errors.append(f"Error en Transform: {str(e)}")
        
        print()
    
    def generate_report(self):
        """Genera reporte final de integridad."""
        print("="*60)
        print("📊 REPORTE FINAL DE INTEGRIDAD")
        print("="*60 + "\n")
        
        # Contar resultados
        structure_pass = sum(1 for _, passed in self.results["structure"] if passed)
        structure_total = len(self.results["structure"])
        
        imports_pass = sum(1 for _, passed in self.results["imports"] if passed)
        imports_total = len(self.results["imports"])
        
        func_pass = sum(1 for _, passed in self.results["functionality"] if passed)
        func_total = len(self.results["functionality"])
        
        total_pass = structure_pass + imports_pass + func_pass
        total_tests = structure_total + imports_total + func_total
        
        # Mostrar resumen
        print(f"Estructura:        {structure_pass}/{structure_total} ✓")
        print(f"Imports:           {imports_pass}/{imports_total} ✓")
        print(f"Funcionalidad:     {func_pass}/{func_total} ✓")
        print(f"\nTotal:             {total_pass}/{total_tests} ✓")
        
        percentage = (total_pass / total_tests) * 100 if total_tests > 0 else 0
        print(f"Integridad:        {percentage:.1f}%\n")
        
        # Resultado general
        if self.errors:
            print(f"❌ ERRORES ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")
            print()
        
        if self.warnings:
            print(f"⚠️  ADVERTENCIAS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")
            print()
        
        if percentage >= 90:
            print("🎉 PROYECTO EN ESTADO ÓPTIMO\n")
            return True
        elif percentage >= 70:
            print("⚠️  PROYECTO FUNCIONAL CON PROBLEMAS MENORES\n")
            return True
        else:
            print("❌ PROYECTO CON PROBLEMAS CRÍTICOS\n")
            return False
    
    def run_all_checks(self):
        """Ejecuta todas las verificaciones."""
        print("\n" + "🔍 INICIANDO VERIFICACIÓN DE INTEGRIDAD - ClimAPI")
        
        self.check_structure()
        self.check_imports()
        self.check_functionality()
        success = self.generate_report()
        
        return success


if __name__ == "__main__":
    checker = IntegrityChecker()
    success = checker.run_all_checks()
    sys.exit(0 if success else 1)
