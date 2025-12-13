"""
Script de Verificación Visual Rápida
====================================
Muestra el estado de todas las conexiones del sistema IDEAM
"""

print("\n" + "="*70)
print("🔍 VERIFICACIÓN RÁPIDA DEL SISTEMA IDEAM")
print("="*70 + "\n")

# 1. Verificar imports principales
print("📦 Verificando librerías principales...\n")

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Pandas
try:
    import pandas as pd
    print("✅ pandas:", pd.__version__)
except:
    print("❌ pandas: NO DISPONIBLE")

# NumPy
try:
    import numpy as np
    print("✅ numpy:", np.__version__)
except:
    print("❌ numpy: NO DISPONIBLE")

# Matplotlib
try:
    import matplotlib
    print("✅ matplotlib:", matplotlib.__version__)
except:
    print("❌ matplotlib: NO DISPONIBLE")

# Seaborn
try:
    import seaborn as sns
    print("✅ seaborn:", sns.__version__, "(opcional)")
except:
    print("ℹ️  seaborn: No disponible (opcional)")

print("\n" + "-"*70)
print("📡 Verificando librerías de radar...\n")

# PyART
try:
    import pyart
    print("✅ PyART:", pyart.__version__)
    print("   → Análisis avanzado de radar")
    print("   → Lectura de archivos Sigmet")
    print("   → Cálculo de estadísticas")
except:
    print("❌ PyART: NO DISPONIBLE")

# xradar
try:
    import xradar as xd
    print("✅ xradar: Disponible")
    print("   → Lectura nativa Sigmet")
    print("   → Conversión a xarray")
    print("   → Georreferenciación")
except:
    print("ℹ️  xradar: No disponible (opcional)")

print("\n" + "-"*70)
print("☁️  Verificando capacidades AWS...\n")

# boto3
try:
    import boto3
    print("✅ boto3:", boto3.__version__)
    print("   → Cliente AWS S3")
except:
    print("ℹ️  boto3: No disponible (opcional)")

# fsspec
try:
    import fsspec
    print("✅ fsspec:", fsspec.__version__)
    print("   → Sistema de archivos flexible")
except:
    print("ℹ️  fsspec: No disponible (opcional)")

print("\n" + "-"*70)
print("🔌 Verificando visualizador IDEAM...\n")

try:
    from visualizers.ideam_visualizer import IDEAMRadarVisualizer
    print("✅ IDEAMRadarVisualizer importado correctamente")
    
    # Inicializar
    viz = IDEAMRadarVisualizer()
    print("✅ Visualizador inicializado")
    
    # Verificar radares
    if hasattr(viz, 'radares_info') and viz.radares_info:
        print(f"✅ Radares disponibles: {len(viz.radares_info)}")
        for radar_name, info in viz.radares_info.items():
            print(f"   • {radar_name}: {info['lat']:.4f}°N, {info['lon']:.4f}°W")
    else:
        print("⚠️  No se encontraron radares")
    
    # Verificar AWS
    if hasattr(viz, 'enable_aws') and viz.enable_aws:
        print("✅ AWS S3 habilitado")
        print(f"   Bucket: s3://{viz.s3_bucket}/")
    else:
        print("ℹ️  AWS S3 no habilitado (opcional)")
    
    # Verificar archivos
    data_dir = Path("data/Radar_IDEAM/Barrancabermeja")
    if data_dir.exists():
        archivos = list(data_dir.glob("*.RAW*"))
        print(f"✅ Archivos disponibles: {len(archivos)}")
    else:
        print("⚠️  Directorio de datos no encontrado")
    
except Exception as e:
    print(f"❌ Error al verificar visualizador: {e}")

print("\n" + "="*70)
print("📊 RESUMEN")
print("="*70 + "\n")

# Contar componentes disponibles
componentes = {
    'pandas': False,
    'numpy': False,
    'matplotlib': False,
    'pyart': False,
    'xradar': False,
    'boto3': False,
    'fsspec': False,
    'seaborn': False
}

try:
    import pandas
    componentes['pandas'] = True
except:
    pass

try:
    import numpy
    componentes['numpy'] = True
except:
    pass

try:
    import matplotlib
    componentes['matplotlib'] = True
except:
    pass

try:
    import pyart
    componentes['pyart'] = True
except:
    pass

try:
    import xradar
    componentes['xradar'] = True
except:
    pass

try:
    import boto3
    componentes['boto3'] = True
except:
    pass

try:
    import fsspec
    componentes['fsspec'] = True
except:
    pass

try:
    import seaborn
    componentes['seaborn'] = True
except:
    pass

# Categorizar
requeridos = ['pandas', 'numpy', 'matplotlib', 'pyart']
opcionales = ['xradar', 'boto3', 'fsspec', 'seaborn']

requeridos_ok = sum(componentes[k] for k in requeridos)
opcionales_ok = sum(componentes[k] for k in opcionales)

print(f"Componentes requeridos: {requeridos_ok}/{len(requeridos)} ✅" if requeridos_ok == len(requeridos) else f"Componentes requeridos: {requeridos_ok}/{len(requeridos)} ⚠️")
print(f"Componentes opcionales: {opcionales_ok}/{len(opcionales)}")

if requeridos_ok == len(requeridos):
    print("\n🎉 SISTEMA OPERACIONAL")
    print("   Todas las funcionalidades básicas están disponibles")
    
    if opcionales_ok == len(opcionales):
        print("   + TODAS las funcionalidades avanzadas disponibles")
    elif opcionales_ok > 0:
        print(f"   + {opcionales_ok} funcionalidades avanzadas disponibles")
else:
    print("\n⚠️  SISTEMA PARCIALMENTE OPERACIONAL")
    print("   Instalar componentes faltantes con:")
    print("   pip install -r requirements.txt")

print("\n" + "="*70 + "\n")

print("💡 Comandos útiles:")
print("   • python tests/test_ideam_visualizer.py")
print("   • python verificar_ideam_completo.py")
print("   • python -m src.visualizers.ideam_visualizer")
print()
