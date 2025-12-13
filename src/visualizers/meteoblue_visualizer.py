"""
Meteoblue Data Visualizer & Processor
=====================================

Procesa y visualiza datos de Meteoblue usando pandas, numpy, matplotlib y sklearn.
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
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings('ignore')

# Configuración de estilo
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


class MeteoblueVisualizer:
    """Procesador y visualizador de datos de Meteoblue"""
    
    def __init__(self, data_dir="data/data_meteoblue"):
        """
        Inicializa el visualizador
        
        Args:
            data_dir: Directorio con datos de Meteoblue
        """
        self.data_dir = Path(data_dir)
        self.df = None
        self.scaler = StandardScaler()
        
    def cargar_datos(self):
        """Carga y procesa todos los archivos JSON de Meteoblue"""
        all_data = []
        
        if not self.data_dir.exists():
            print(f"❌ Directorio {self.data_dir} no existe")
            return None
            
        json_files = list(self.data_dir.glob("*.json"))
        
        if not json_files:
            print(f"⚠️ No se encontraron archivos JSON en {self.data_dir}")
            return None
        
        print(f"📂 Encontrados {len(json_files)} archivos")
        
        for file in json_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extraer información
                metadata = data.get('metadata', {})
                location = file.stem.split('_')[1]  # Extraer ciudad del nombre
                
                # Procesar datos diarios si existen
                if 'data_day' in data:
                    for day_data in data['data_day']:
                        row = {
                            'ciudad': location,
                            'fecha': day_data.get('date'),
                            'temp_max': day_data.get('temperature_max'),
                            'temp_min': day_data.get('temperature_min'),
                            'precipitacion': day_data.get('precipitation'),
                            'humedad': day_data.get('relative_humidity_mean'),
                            'viento_max': day_data.get('wind_speed_max'),
                            'presion': day_data.get('pressure_mean'),
                            'archivo': file.name
                        }
                        all_data.append(row)
                        
            except Exception as e:
                print(f"⚠️ Error procesando {file.name}: {e}")
                continue
        
        if all_data:
            self.df = pd.DataFrame(all_data)
            self._procesar_datos()
            print(f"✅ Cargados {len(self.df)} registros")
            return self.df
        else:
            print("❌ No se pudo cargar ningún dato")
            return None
    
    def _procesar_datos(self):
        """Procesa y limpia el DataFrame"""
        if self.df is None:
            return
        
        # Convertir fecha a datetime
        self.df['fecha'] = pd.to_datetime(self.df['fecha'])
        
        # Crear features temporales
        self.df['año'] = self.df['fecha'].dt.year
        self.df['mes'] = self.df['fecha'].dt.month
        self.df['dia'] = self.df['fecha'].dt.day
        self.df['dia_semana'] = self.df['fecha'].dt.dayofweek
        
        # Convertir a numéricos
        numeric_cols = ['temp_max', 'temp_min', 'precipitacion', 'humedad', 
                       'viento_max', 'presion']
        for col in numeric_cols:
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
        # Calcular estadísticas
        self.df['temp_promedio'] = (self.df['temp_max'] + self.df['temp_min']) / 2
        self.df['amplitud_termica'] = self.df['temp_max'] - self.df['temp_min']
        
    def estadisticas_basicas(self):
        """Genera estadísticas descriptivas"""
        if self.df is None:
            print("❌ Primero carga los datos con cargar_datos()")
            return None
        
        print("\n" + "="*60)
        print("📊 ESTADÍSTICAS DESCRIPTIVAS - METEOBLUE")
        print("="*60)
        
        print(f"\n📅 Rango de fechas: {self.df['fecha'].min()} a {self.df['fecha'].max()}")
        print(f"🌍 Ciudades: {', '.join(self.df['ciudad'].unique())}")
        print(f"📈 Total registros: {len(self.df)}")
        print(f"\n🌡️ Temperatura:")
        print(f"  - Máxima promedio: {self.df['temp_max'].mean():.2f}°C")
        print(f"  - Mínima promedio: {self.df['temp_min'].mean():.2f}°C")
        print(f"  - Record máximo: {self.df['temp_max'].max():.2f}°C")
        print(f"  - Record mínimo: {self.df['temp_min'].min():.2f}°C")
        
        print(f"\n💧 Precipitación:")
        print(f"  - Promedio: {self.df['precipitacion'].mean():.2f} mm")
        print(f"  - Máxima: {self.df['precipitacion'].max():.2f} mm")
        
        print(f"\n💨 Viento:")
        print(f"  - Velocidad máxima promedio: {self.df['viento_max'].mean():.2f} km/h")
        
        print(f"\n💧 Humedad:")
        print(f"  - Promedio: {self.df['humedad'].mean():.2f}%")
        
        return self.df.describe()
    
    def grafico_series_temporales(self, ciudad=None, save_path=None):
        """
        Genera gráfico de series temporales
        
        Args:
            ciudad: Filtrar por ciudad específica
            save_path: Ruta para guardar la imagen
        """
        if self.df is None:
            print("❌ Primero carga los datos")
            return
        
        df_plot = self.df if ciudad is None else self.df[self.df['ciudad'] == ciudad]
        
        fig, axes = plt.subplots(3, 1, figsize=(15, 10))
        titulo = f"Series Temporales - Meteoblue" + (f" ({ciudad})" if ciudad else "")
        fig.suptitle(titulo, fontsize=16, fontweight='bold')
        
        # Temperatura
        for c in df_plot['ciudad'].unique():
            data = df_plot[df_plot['ciudad'] == c]
            axes[0].plot(data['fecha'], data['temp_promedio'], marker='o', label=c)
        axes[0].set_ylabel('Temperatura (°C)')
        axes[0].set_title('Temperatura Promedio')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Precipitación
        for c in df_plot['ciudad'].unique():
            data = df_plot[df_plot['ciudad'] == c]
            axes[1].bar(data['fecha'], data['precipitacion'], label=c, alpha=0.7)
        axes[1].set_ylabel('Precipitación (mm)')
        axes[1].set_title('Precipitación Diaria')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        # Humedad
        for c in df_plot['ciudad'].unique():
            data = df_plot[df_plot['ciudad'] == c]
            axes[2].plot(data['fecha'], data['humedad'], marker='s', label=c)
        axes[2].set_ylabel('Humedad (%)')
        axes[2].set_title('Humedad Relativa')
        axes[2].legend()
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ Gráfico guardado en {save_path}")
        
        plt.show()
    
    def analisis_correlacion(self, save_path=None):
        """Genera matriz de correlación"""
        if self.df is None:
            print("❌ Primero carga los datos")
            return
        
        # Seleccionar variables numéricas
        numeric_cols = ['temp_max', 'temp_min', 'temp_promedio', 'amplitud_termica',
                       'precipitacion', 'humedad', 'viento_max', 'presion']
        
        corr_matrix = self.df[numeric_cols].corr()
        
        plt.figure(figsize=(12, 10))
        sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', 
                   center=0, square=True, linewidths=1)
        plt.title('Matriz de Correlación - Variables Climáticas Meteoblue', 
                 fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ Matriz guardada en {save_path}")
        
        plt.show()
        
        return corr_matrix
    
    def clustering_ciudades(self, n_clusters=3, save_path=None):
        """
        Realiza clustering de ciudades basado en patrones climáticos
        
        Args:
            n_clusters: Número de clusters
            save_path: Ruta para guardar
        """
        if self.df is None:
            print("❌ Primero carga los datos")
            return
        
        # Agrupar por ciudad y calcular promedios
        city_features = self.df.groupby('ciudad').agg({
            'temp_promedio': 'mean',
            'precipitacion': 'mean',
            'humedad': 'mean',
            'viento_max': 'mean',
            'amplitud_termica': 'mean'
        }).reset_index()
        
        # Normalizar features
        features = city_features.drop('ciudad', axis=1)
        features_scaled = self.scaler.fit_transform(features)
        
        # K-Means
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        city_features['cluster'] = kmeans.fit_predict(features_scaled)
        
        # PCA para visualización
        pca = PCA(n_components=2)
        features_pca = pca.fit_transform(features_scaled)
        
        plt.figure(figsize=(12, 8))
        scatter = plt.scatter(features_pca[:, 0], features_pca[:, 1], 
                            c=city_features['cluster'], cmap='viridis', 
                            s=200, alpha=0.6, edgecolors='black')
        
        for i, ciudad in enumerate(city_features['ciudad']):
            plt.annotate(ciudad, (features_pca[i, 0], features_pca[i, 1]),
                        fontsize=12, fontweight='bold')
        
        plt.colorbar(scatter, label='Cluster')
        plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%} varianza)')
        plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%} varianza)')
        plt.title('Clustering de Ciudades - Patrones Climáticos', 
                 fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ Clustering guardado en {save_path}")
        
        plt.show()
        
        print("\n📊 Características por cluster:")
        print(city_features.groupby('cluster').mean())
        
        return city_features
    
    def detectar_outliers(self):
        """Detecta valores atípicos usando IQR"""
        if self.df is None:
            print("❌ Primero carga los datos")
            return
        
        print("\n🔍 DETECCIÓN DE OUTLIERS")
        print("="*60)
        
        numeric_cols = ['temp_max', 'temp_min', 'precipitacion', 'humedad', 'viento_max']
        
        for col in numeric_cols:
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = self.df[(self.df[col] < lower_bound) | (self.df[col] > upper_bound)]
            
            if len(outliers) > 0:
                print(f"\n📌 {col}:")
                print(f"  - Límite inferior: {lower_bound:.2f}")
                print(f"  - Límite superior: {upper_bound:.2f}")
                print(f"  - Outliers encontrados: {len(outliers)}")
                print(f"  - Porcentaje: {len(outliers)/len(self.df)*100:.2f}%")
    
    def exportar_procesado(self, output_path="data/processed/meteoblue_processed.csv"):
        """Exporta datos procesados"""
        if self.df is None:
            print("❌ Primero carga los datos")
            return
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.df.to_csv(output_path, index=False)
        print(f"✅ Datos exportados a {output_path}")


def main():
    """Función principal de ejemplo"""
    print("🌦️ METEOBLUE VISUALIZER")
    print("="*60)
    
    visualizer = MeteoblueVisualizer()
    
    # Cargar datos
    df = visualizer.cargar_datos()
    
    if df is not None:
        # Estadísticas
        visualizer.estadisticas_basicas()
        
        # Gráficos
        visualizer.grafico_series_temporales(save_path="data/images_meteo_blue/series_temporales.png")
        visualizer.analisis_correlacion(save_path="data/images_meteo_blue/correlacion.png")
        visualizer.clustering_ciudades(save_path="data/images_meteo_blue/clustering.png")
        visualizer.detectar_outliers()
        
        # Exportar
        visualizer.exportar_procesado()


if __name__ == "__main__":
    main()
