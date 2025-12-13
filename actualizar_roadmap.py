#!/usr/bin/env python
"""
Script para actualizar el progreso del Roadmap de CLIMAPI
Permite marcar tareas como completadas y actualizar porcentajes de progreso
"""

import re
from pathlib import Path
from datetime import datetime

ROADMAP_FILE = Path("ROADMAP.md")

class RoadmapManager:
    """Gestor del roadmap del proyecto"""
    
    def __init__(self):
        self.roadmap_path = ROADMAP_FILE
        self.content = self._load_roadmap()
    
    def _load_roadmap(self):
        """Carga el contenido del roadmap"""
        if not self.roadmap_path.exists():
            print(f"❌ No se encuentra el archivo {self.roadmap_path}")
            return None
        
        with open(self.roadmap_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _save_roadmap(self):
        """Guarda los cambios en el roadmap"""
        with open(self.roadmap_path, 'w', encoding='utf-8') as f:
            f.write(self.content)
        print(f"✅ Roadmap actualizado: {self.roadmap_path}")
    
    def actualizar_progreso_etapa(self, etapa_numero, nuevo_progreso):
        """
        Actualiza el progreso de una etapa
        
        Args:
            etapa_numero: Número de la etapa (1-8)
            nuevo_progreso: Porcentaje de progreso (0-100)
        """
        etapas = {
            1: "Recolección de datos",
            2: "Procesamiento y limpieza",
            3: "Análisis exploratorio y feature engineering",
            4: "Entrenamiento de modelos",
            5: "Integración con MLflow",
            6: "API con FastAPI",
            7: "Dashboard con Streamlit",
            8: "Despliegue y pruebas"
        }
        
        etapa_nombre = etapas.get(etapa_numero)
        if not etapa_nombre:
            print(f"❌ Etapa {etapa_numero} no válida (debe ser 1-8)")
            return False
        
        # Buscar y reemplazar el progreso
        pattern = rf"### [✅🔄⏳]? \d\. {re.escape(etapa_nombre)}\n\*\*Progreso: \d+%\*\*"
        
        # Determinar emoji según progreso
        emoji = "⚪" if nuevo_progreso == 0 else "🟡" if nuevo_progreso < 50 else "🟠" if nuevo_progreso < 100 else "🟢"
        
        replacement = f"### {emoji} {etapa_numero}. {etapa_nombre}\n**Progreso: {nuevo_progreso}%** {emoji}"
        
        if re.search(pattern, self.content):
            self.content = re.sub(pattern, replacement, self.content)
            print(f"✅ Progreso de '{etapa_nombre}' actualizado a {nuevo_progreso}%")
            return True
        else:
            print(f"❌ No se pudo encontrar la etapa '{etapa_nombre}'")
            return False
    
    def marcar_tarea_completada(self, tarea_texto):
        """
        Marca una tarea como completada
        
        Args:
            tarea_texto: Texto parcial de la tarea a marcar
        """
        # Buscar la tarea
        pattern = rf"- \[[ x]\] {re.escape(tarea_texto)}"
        
        if re.search(pattern, self.content):
            # Reemplazar [ ] o [x] con [x]
            self.content = re.sub(
                rf"- \[ \] ({re.escape(tarea_texto)})",
                r"- [x] \1",
                self.content
            )
            print(f"✅ Tarea marcada como completada: {tarea_texto}")
            return True
        else:
            print(f"❌ No se encontró la tarea: {tarea_texto}")
            return False
    
    def agregar_nota_progreso(self, nota):
        """
        Agrega una nota de progreso con la fecha actual
        
        Args:
            nota: Texto de la nota a agregar
        """
        fecha = datetime.now().strftime("%Y-%m-%d")
        
        # Buscar la sección de Notas de Progreso
        pattern = r"(## 📝 Notas de Progreso\n\n)"
        
        if re.search(pattern, self.content):
            nueva_nota = f"### {fecha}\n{nota}\n\n"
            self.content = re.sub(pattern, f"\\1{nueva_nota}", self.content)
            print(f"✅ Nota agregada para {fecha}")
            return True
        else:
            print("❌ No se encontró la sección de Notas de Progreso")
            return False
    
    def mostrar_estado(self):
        """Muestra el estado actual del proyecto"""
        print("\n" + "="*60)
        print("ESTADO ACTUAL DEL ROADMAP")
        print("="*60)
        
        # Extraer progreso de cada etapa
        pattern = r"### [✅🔄⏳⚪🟡🟠🟢]+ \d\. (.+?)\n\*\*Progreso: (\d+)%\*\*"
        etapas = re.findall(pattern, self.content)
        
        total_progreso = 0
        for etapa, progreso in etapas:
            progreso_int = int(progreso)
            total_progreso += progreso_int
            
            barra = "█" * (progreso_int // 5) + "░" * (20 - progreso_int // 5)
            print(f"\n{etapa:<40} {barra} {progreso}%")
        
        progreso_general = total_progreso // len(etapas) if etapas else 0
        barra_general = "█" * (progreso_general // 5) + "░" * (20 - progreso_general // 5)
        
        print("\n" + "-"*60)
        print(f"{'Progreso General':<40} {barra_general} {progreso_general}%")
        print("="*60)
        
        # Contar tareas completadas
        tareas_completadas = len(re.findall(r"- \[x\]", self.content))
        tareas_totales = len(re.findall(r"- \[[x ]\]", self.content))
        
        print(f"\nTareas completadas: {tareas_completadas}/{tareas_totales}")
        print()
    
    def guardar(self):
        """Guarda los cambios realizados"""
        self._save_roadmap()


def menu_interactivo():
    """Menú interactivo para actualizar el roadmap"""
    manager = RoadmapManager()
    
    if not manager.content:
        return
    
    while True:
        print("\n" + "="*60)
        print("GESTOR DE ROADMAP - CLIMAPI")
        print("="*60)
        print("\n1. Ver estado actual")
        print("2. Actualizar progreso de etapa")
        print("3. Marcar tarea como completada")
        print("4. Agregar nota de progreso")
        print("5. Guardar y salir")
        print("6. Salir sin guardar")
        
        opcion = input("\nSelecciona una opción: ").strip()
        
        if opcion == "1":
            manager.mostrar_estado()
        
        elif opcion == "2":
            print("\nEtapas disponibles:")
            print("1. Recolección de datos")
            print("2. Procesamiento y limpieza")
            print("3. Análisis exploratorio y feature engineering")
            print("4. Entrenamiento de modelos")
            print("5. Integración con MLflow")
            print("6. API con FastAPI")
            print("7. Dashboard con Streamlit")
            print("8. Despliegue y pruebas")
            
            etapa = input("\nNúmero de etapa (1-8): ").strip()
            progreso = input("Nuevo progreso (0-100): ").strip()
            
            try:
                manager.actualizar_progreso_etapa(int(etapa), int(progreso))
            except ValueError:
                print("❌ Valores inválidos")
        
        elif opcion == "3":
            print("\nEjemplos de tareas:")
            print("- Configurar cuentas y claves de APIs climáticas")
            print("- Desarrollar scripts de extracción en tiempo real/histórico")
            print("- Elegir y poblar la base de datos")
            
            tarea = input("\nTexto de la tarea (parcial): ").strip()
            manager.marcar_tarea_completada(tarea)
        
        elif opcion == "4":
            print("\nEjemplo: '- ✅ Implementada normalización de datos'")
            nota = input("\nNota a agregar: ").strip()
            
            if nota:
                manager.agregar_nota_progreso(nota)
        
        elif opcion == "5":
            manager.guardar()
            print("\n👋 ¡Hasta luego!")
            break
        
        elif opcion == "6":
            print("\n👋 Saliendo sin guardar...")
            break
        
        else:
            print("❌ Opción inválida")
        
        input("\nPresiona ENTER para continuar...")


if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║              GESTOR DE ROADMAP - CLIMAPI                      ║
    ║         Actualiza el progreso del proyecto fácilmente         ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    menu_interactivo()
