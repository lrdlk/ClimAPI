#!/usr/bin/env python
"""
Script de prueba rápida del Dashboard CLIMAPI
Verifica que todas las dependencias estén instaladas
"""

import sys
from pathlib import Path

def verificar_dependencias():
    """Verifica que todas las dependencias necesarias estén instaladas"""
    
    print("=" * 60)
    print("CLIMAPI Dashboard - Verificación de Dependencias")
    print("=" * 60)
    
    dependencias = {
        'streamlit': 'Streamlit (Dashboard)',
        'plotly': 'Plotly (Gráficos)',
        'pandas': 'Pandas (Manejo de datos)',
        'requests': 'Requests (Peticiones HTTP)',
        'dotenv': 'Python-dotenv (Variables de entorno)'
    }
    
    faltantes = []
    
    for modulo, descripcion in dependencias.items():
        try:
            if modulo == 'dotenv':
                __import__('dotenv')
            else:
                __import__(modulo)
            print(f"✅ {descripcion}")
        except ImportError:
            print(f"❌ {descripcion} - NO INSTALADO")
            faltantes.append(modulo)
    
    print("\n" + "=" * 60)
    
    if faltantes:
        print("\n⚠️  DEPENDENCIAS FALTANTES:")
        print("\nPara instalar las dependencias faltantes, ejecuta:")
        print(f"\npip install {' '.join(faltantes)}")
        return False
    else:
        print("\n✅ Todas las dependencias están instaladas correctamente")
        return True


def verificar_estructura():
    """Verifica la estructura de directorios"""
    
    print("\n" + "=" * 60)
    print("Verificando Estructura de Directorios")
    print("=" * 60)
    
    directorios = [
        'data',
        'data/data_meteoblue',
        'data/data_openmeteo',
        'data/data_openweathermap',
        'data/data_meteosource',
        'logs',
        'src/data_sources'
    ]
    
    for directorio in directorios:
        path = Path(directorio)
        if path.exists():
            print(f"✅ {directorio}/")
        else:
            print(f"⚠️  {directorio}/ - No existe (se creará automáticamente)")
    
    print("\n" + "=" * 60)


def verificar_archivos():
    """Verifica archivos importantes"""
    
    print("\nVerificando Archivos Importantes")
    print("=" * 60)
    
    archivos = [
        'main.py',
        'dashboard.py',
        'requirements.txt',
        '.env.example'
    ]
    
    for archivo in archivos:
        path = Path(archivo)
        if path.exists():
            print(f"✅ {archivo}")
        else:
            print(f"❌ {archivo} - NO ENCONTRADO")
    
    # Verificar .env
    env_path = Path('.env')
    if env_path.exists():
        print(f"✅ .env (configurado)")
    else:
        print(f"⚠️  .env - No existe (usa .env.example como plantilla)")
    
    print("\n" + "=" * 60)


def main():
    """Función principal"""
    
    print("\n🌦️  CLIMAPI Dashboard - Verificación del Sistema\n")
    
    # Verificar dependencias
    deps_ok = verificar_dependencias()
    
    # Verificar estructura
    verificar_estructura()
    
    # Verificar archivos
    verificar_archivos()
    
    print("\n" + "=" * 60)
    print("Resumen")
    print("=" * 60)
    
    if deps_ok:
        print("\n✅ El sistema está listo para usar")
        print("\n📝 Próximos pasos:")
        print("1. Configura tu archivo .env con las API keys")
        print("2. Ejecuta: streamlit run dashboard.py")
        print("3. Abre http://localhost:8501 en tu navegador")
    else:
        print("\n⚠️  Instala las dependencias faltantes antes de continuar")
        print("\nEjecuta: pip install -r requirements.txt")
    
    print("\n" + "=" * 60)
    print()


if __name__ == "__main__":
    main()
