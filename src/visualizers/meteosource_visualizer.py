"""
Meteosource Data Visualizer & Processor
=======================================

Procesa y visualiza datos de Meteosource usando pandas, numpy, matplotlib y sklearn.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-dark')
sns.set_palette("rocket")


class MeteosourceVisualizer:
    """Procesador y visualizador de datos de Meteosource"""
    
    def __init__(self, data_dir="data/meteosource"):
        self.data_dir = Path(data_dir)
        self.df = None
        self.scaler = StandardScaler()
        
    def cargar_datos(self):
        """Carga archivos JSON de Meteosource"""
        json_files = list(self.data_dir.glob("*.json"))
        
        if not json_files:
            print(f"⚠️ No se encontraron archivos en {self.data_dir}")
            return None
        
        print(f"📂 Encontrados {len(json_files)} archivos")
        
        all_data = []
        
        for file in json_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                ciudad = file.stem.split('_')[1] if '_' in file.stem else file.stem
                
                # Datos horarios
                if 'hourly' in data and 'data' in data['hourly']:
                    for item in data['hourly']['data']:
                        row = {
                            'ciudad': ciudad,
                            'fecha': pd.to_datetime(item.get('date')),
                            'temperatura': item.get('temperature'),
                            'feels_like': item.get('feels_like'),
                            'viento_vel': item.get('wind', {}).get('speed'),
                            'viento_dir': item.get('wind', {}).get('dir'),
                            'precipitacion': item.get('precipitation', {}).get('total', 0),
                            'humedad': item.get('humidity'),
                            'presion': item.get('pressure'),
                            'nubosidad': item.get('cloud_cover'),
                            'visibilidad': item.get('visibility'),
                            'uv_index': item.get('uv_index'),
                            'tipo': 'hourly',
                            'archivo': file.name
                        }
                        all_data.append(row)
                
                # Datos diarios
                if 'daily' in data and 'data' in data['daily']:
                    for item in data['daily']['data']:
                        row = {
                            'ciudad': ciudad,
                            'fecha': pd.to_datetime(item.get('day')),
                            'temp_max': item.get('all_day', {}).get('temperature_max'),
                            'temp_min': item.get('all_day', {}).get('temperature_min'),
                            'precipitacion_total': item.get('all_day', {}).get('precipitation', {}).get('total', 0),
                            'viento_max': item.get('all_day', {}).get('wind', {}).get('max_speed'),
                            'humedad_max': item.get('all_day', {}).get('humidity_max'),
                            'humedad_min': item.get('all_day', {}).get('humidity_min'),
                            'tipo': 'daily',
                            'archivo': file.name
                        }
                        all_data.append(row)
                        
            except Exception as e:
                print(f"⚠️ Error en {file.name}: {e}")
                continue
        
        if all_data:
            self.df = pd.DataFrame(all_data)
            self._procesar_datos()
            print(f"✅ Cargados {len(self.df)} registros")
            return self.df
        
        return None
    
    def _procesar_datos(self):
        """Procesa DataFrame"""
        if self.df is None:
            return
        
        # Features temporales
        self.df['hora'] = self.df['fecha'].dt.hour
        self.df['dia'] = self.df['fecha'].dt.day
        self.df['mes'] = self.df['fecha'].dt.month
        self.df['dia_semana'] = self.df['fecha'].dt.dayofweek
        self.df['dia_año'] = self.df['fecha'].dt.dayofyear
        
        # Calcular temperatura promedio si existen min y max
        if 'temp_max' in self.df.columns and 'temp_min' in self.df.columns:
            self.df['temp_promedio'] = (self.df['temp_max'] + self.df['temp_min']) / 2
    
    def estadisticas_basicas(self):
        """Estadísticas descriptivas"""
        if self.df is None:
            print("❌ Primero carga los datos")
            return
        
        print("\n" + "="*60)
        print("📊 ESTADÍSTICAS - METEOSOURCE")
        print("="*60)
        
        print(f"\n📅 Periodo: {self.df['fecha'].min()} a {self.df['fecha'].max()}")
        print(f"🌍 Ciudades: {', '.join(self.df['ciudad'].unique())}")
        print(f"📈 Total registros: {len(self.df)}")
        print(f"📊 Tipos de datos: {', '.join(self.df['tipo'].unique())}")
        
        if 'temperatura' in self.df.columns:
            temp_data = self.df['temperatura'].dropna()
            if len(temp_data) > 0:
                print(f"\n🌡️ Temperatura (datos horarios):")
                print(f"  - Promedio: {temp_data.mean():.2f}°C")
                print(f"  - Máxima: {temp_data.max():.2f}°C")
                print(f"  - Mínima: {temp_data.min():.2f}°C")
        
        if 'uv_index' in self.df.columns:
            uv_data = self.df['uv_index'].dropna()
            if len(uv_data) > 0:
                print(f"\n☀️ Índice UV:")
                print(f"  - Promedio: {uv_data.mean():.2f}")
                print(f"  - Máximo: {uv_data.max():.2f}")
        
        if 'visibilidad' in self.df.columns:
            vis_data = self.df['visibilidad'].dropna()
            if len(vis_data) > 0:
                print(f"\n👁️ Visibilidad:")
                print(f"  - Promedio: {vis_data.mean():.2f} km")
                print(f"  - Mínima: {vis_data.min():.2f} km")
    
    def grafico_uv_index(self, save_path=None):
        """Analiza índice UV"""
        if self.df is None or 'uv_index' not in self.df.columns:
            print("❌ No hay datos de UV index")
            return
        
        df_uv = self.df[self.df['uv_index'].notna()].copy()
        
        if len(df_uv) == 0:
            print("❌ No hay datos válidos de UV index")
            return
        
        fig, axes = plt.subplots(2, 1, figsize=(14, 10))
        fig.suptitle('Análisis de Índice UV - Meteosource', fontsize=16, fontweight='bold')
        
        # Serie temporal
        for ciudad in df_uv['ciudad'].unique():
            data = df_uv[df_uv['ciudad'] == ciudad]
            axes[0].plot(data['fecha'], data['uv_index'], marker='o', label=ciudad, alpha=0.7)
        
        axes[0].axhline(y=3, color='yellow', linestyle='--', label='Moderado (3)')
        axes[0].axhline(y=6, color='orange', linestyle='--', label='Alto (6)')
        axes[0].axhline(y=8, color='red', linestyle='--', label='Muy Alto (8)')
        axes[0].set_ylabel('Índice UV')
        axes[0].set_title('Serie Temporal del Índice UV')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Distribución por hora del día
        if 'hora' in df_uv.columns:
            uv_por_hora = df_uv.groupby('hora')['uv_index'].mean()
            axes[1].bar(uv_por_hora.index, uv_por_hora.values, color='gold', edgecolor='black')
            axes[1].set_xlabel('Hora del día')
            axes[1].set_ylabel('Índice UV promedio')
            axes[1].set_title('Índice UV Promedio por Hora')
            axes[1].grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ Gráfico UV guardado en {save_path}")
        
        plt.show()
    
    def analisis_visibilidad(self, save_path=None):
        """Analiza visibilidad y su relación con otras variables"""
        if self.df is None or 'visibilidad' not in self.df.columns:
            print("❌ No hay datos de visibilidad")
            return
        
        df_vis = self.df[self.df['visibilidad'].notna()].copy()
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Análisis de Visibilidad - Meteosource', fontsize=16, fontweight='bold')
        
        # Serie temporal
        for ciudad in df_vis['ciudad'].unique():
            data = df_vis[df_vis['ciudad'] == ciudad]
            axes[0, 0].plot(data['fecha'], data['visibilidad'], marker='o', label=ciudad, alpha=0.6)
        axes[0, 0].set_ylabel('Visibilidad (km)')
        axes[0, 0].set_title('Visibilidad a lo largo del tiempo')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Visibilidad vs Humedad
        if 'humedad' in df_vis.columns:
            df_plot = df_vis[df_vis['humedad'].notna()]
            axes[0, 1].scatter(df_plot['humedad'], df_plot['visibilidad'], alpha=0.5, c='steelblue')
            axes[0, 1].set_xlabel('Humedad (%)')
            axes[0, 1].set_ylabel('Visibilidad (km)')
            axes[0, 1].set_title('Visibilidad vs Humedad')
            axes[0, 1].grid(True, alpha=0.3)
        
        # Visibilidad vs Precipitación
        if 'precipitacion' in df_vis.columns:
            df_plot = df_vis[df_vis['precipitacion'].notna()]
            axes[1, 0].scatter(df_plot['precipitacion'], df_plot['visibilidad'], alpha=0.5, c='coral')
            axes[1, 0].set_xlabel('Precipitación (mm)')
            axes[1, 0].set_ylabel('Visibilidad (km)')
            axes[1, 0].set_title('Visibilidad vs Precipitación')
            axes[1, 0].grid(True, alpha=0.3)
        
        # Distribución de visibilidad
        axes[1, 1].hist(df_vis['visibilidad'], bins=30, color='skyblue', edgecolor='black', alpha=0.7)
        axes[1, 1].set_xlabel('Visibilidad (km)')
        axes[1, 1].set_ylabel('Frecuencia')
        axes[1, 1].set_title('Distribución de Visibilidad')
        axes[1, 1].grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ Análisis de visibilidad guardado en {save_path}")
        
        plt.show()
    
    def pca_analysis(self, save_path=None):
        """Análisis PCA de variables climáticas"""
        if self.df is None:
            print("❌ Primero carga los datos")
            return
        
        # Seleccionar variables numéricas
        numeric_cols = ['temperatura', 'humedad', 'presion', 'viento_vel', 
                       'nubosidad', 'visibilidad', 'uv_index']
        
        available_cols = [col for col in numeric_cols if col in self.df.columns]
        
        df_pca = self.df[available_cols].dropna()
        
        if len(df_pca) < 10:
            print("❌ No hay suficientes datos para PCA")
            return
        
        # Normalizar
        data_scaled = self.scaler.fit_transform(df_pca)
        
        # PCA
        pca = PCA()
        pca_result = pca.fit_transform(data_scaled)
        
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle('Análisis PCA - Meteosource', fontsize=16, fontweight='bold')
        
        # Varianza explicada
        var_exp = pca.explained_variance_ratio_ * 100
        cum_var_exp = np.cumsum(var_exp)
        
        axes[0].bar(range(1, len(var_exp)+1), var_exp, alpha=0.7, label='Individual')
        axes[0].plot(range(1, len(var_exp)+1), cum_var_exp, 'ro-', label='Acumulada')
        axes[0].set_xlabel('Componente Principal')
        axes[0].set_ylabel('Varianza Explicada (%)')
        axes[0].set_title('Varianza Explicada por Componente')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Scatter de primeras 2 componentes
        axes[1].scatter(pca_result[:, 0], pca_result[:, 1], alpha=0.5, c='purple')
        axes[1].set_xlabel(f'PC1 ({var_exp[0]:.1f}%)')
        axes[1].set_ylabel(f'PC2 ({var_exp[1]:.1f}%)')
        axes[1].set_title('Primeras dos Componentes Principales')
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ PCA guardado en {save_path}")
        
        plt.show()
        
        print(f"\n📊 Componentes que explican 90% varianza: {np.argmax(cum_var_exp >= 90) + 1}")
        print(f"   PC1: {var_exp[0]:.2f}%")
        print(f"   PC2: {var_exp[1]:.2f}%")
    
    def exportar_procesado(self):
        """Exporta datos procesados"""
        if self.df is None:
            print("❌ Primero carga los datos")
            return
        
        output_path = Path("data/processed/meteosource_processed.csv")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.df.to_csv(output_path, index=False)
        print(f"✅ Datos exportados a {output_path}")


def main():
    """Función principal"""
    print("🌦️ METEOSOURCE VISUALIZER")
    print("="*60)
    
    visualizer = MeteosourceVisualizer()
    df = visualizer.cargar_datos()
    
    if df is not None:
        visualizer.estadisticas_basicas()
        visualizer.grafico_uv_index(save_path="data/images/meteosource_uv.png")
        visualizer.analisis_visibilidad(save_path="data/images/meteosource_visibilidad.png")
        visualizer.pca_analysis(save_path="data/images/meteosource_pca.png")
        visualizer.exportar_procesado()


if __name__ == "__main__":
    main()
