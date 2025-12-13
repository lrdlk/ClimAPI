"""
SIATA Data Visualizer & Processor
=================================

Procesa y visualiza datos históricos de SIATA usando pandas, numpy, matplotlib y sklearn.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

plt.style.use('bmh')
sns.set_palette("Set3")


class SIATAVisualizer:
    """Procesador y visualizador de datos históricos de SIATA"""
    
    def __init__(self, data_dir="data/siata_historico"):
        self.data_dir = Path(data_dir)
        self.df = None
        self.scaler = StandardScaler()
        
    def cargar_datos(self):
        """Carga archivos CSV de SIATA"""
        csv_files = list(self.data_dir.glob("*.csv"))
        
        if not csv_files:
            print(f"⚠️ No se encontraron archivos CSV en {self.data_dir}")
            return None
        
        print(f"📂 Encontrados {len(csv_files)} archivos CSV")
        
        dfs = []
        
        for file in csv_files:
            try:
                df = pd.read_csv(file)
                df['archivo'] = file.name
                
                # Extraer estación del nombre si es posible
                if '_' in file.stem:
                    estacion = file.stem.split('_')[0]
                    if 'estacion' not in df.columns:
                        df['estacion'] = estacion
                
                dfs.append(df)
                print(f"✅ Cargado: {file.name} ({len(df)} registros)")
                
            except Exception as e:
                print(f"⚠️ Error en {file.name}: {e}")
        
        if dfs:
            self.df = pd.concat(dfs, ignore_index=True)
            self._procesar_datos()
            print(f"\n✅ Total: {len(self.df)} registros de {len(csv_files)} archivos")
            return self.df
        
        return None
    
    def _procesar_datos(self):
        """Procesa y limpia el DataFrame"""
        if self.df is None:
            return
        
        # Identificar columna de fecha
        date_cols = [col for col in self.df.columns if 'fecha' in col.lower() or 'date' in col.lower() or 'time' in col.lower()]
        
        if date_cols:
            # Convertir primera columna de fecha encontrada
            try:
                self.df['fecha'] = pd.to_datetime(self.df[date_cols[0]])
                
                # Features temporales
                self.df['año'] = self.df['fecha'].dt.year
                self.df['mes'] = self.df['fecha'].dt.month
                self.df['dia'] = self.df['fecha'].dt.day
                self.df['hora'] = self.df['fecha'].dt.hour
                self.df['dia_semana'] = self.df['fecha'].dt.dayofweek
                self.df['dia_año'] = self.df['fecha'].dt.dayofyear
                
            except Exception as e:
                print(f"⚠️ Error procesando fechas: {e}")
        
        # Identificar columnas numéricas
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Convertir strings numéricos
        for col in self.df.columns:
            if col not in numeric_cols and col not in ['estacion', 'archivo', 'fecha']:
                try:
                    self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                except:
                    pass
    
    def estadisticas_basicas(self):
        """Estadísticas descriptivas"""
        if self.df is None:
            print("❌ Primero carga los datos con cargar_datos()")
            return
        
        print("\n" + "="*60)
        print("📊 ESTADÍSTICAS - SIATA HISTÓRICO")
        print("="*60)
        
        print(f"\n📈 Total registros: {len(self.df)}")
        print(f"📂 Archivos procesados: {self.df['archivo'].nunique()}")
        
        if 'estacion' in self.df.columns:
            print(f"📍 Estaciones: {self.df['estacion'].nunique()}")
            print(f"   {', '.join(self.df['estacion'].unique()[:10])}")
        
        if 'fecha' in self.df.columns:
            print(f"\n📅 Rango temporal:")
            print(f"  - Desde: {self.df['fecha'].min()}")
            print(f"  - Hasta: {self.df['fecha'].max()}")
            print(f"  - Duración: {self.df['fecha'].max() - self.df['fecha'].min()}")
        
        # Columnas disponibles
        print(f"\n📊 Columnas disponibles ({len(self.df.columns)}):")
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        print(f"  - Numéricas: {len(numeric_cols)}")
        
        for col in numeric_cols[:10]:  # Mostrar solo primeras 10
            if col not in ['año', 'mes', 'dia', 'hora', 'dia_semana', 'dia_año']:
                print(f"    • {col}: μ={self.df[col].mean():.2f}, σ={self.df[col].std():.2f}")
    
    def grafico_series_temporales(self, columna=None, estacion=None, save_path=None):
        """
        Gráfico de series temporales
        
        Args:
            columna: Columna a graficar (si None, usa la primera numérica)
            estacion: Filtrar por estación específica
            save_path: Ruta para guardar
        """
        if self.df is None or 'fecha' not in self.df.columns:
            print("❌ No hay datos temporales")
            return
        
        # Seleccionar columna
        if columna is None:
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
            exclude = ['año', 'mes', 'dia', 'hora', 'dia_semana', 'dia_año']
            available = [col for col in numeric_cols if col not in exclude]
            if not available:
                print("❌ No hay columnas numéricas disponibles")
                return
            columna = available[0]
        
        if columna not in self.df.columns:
            print(f"❌ Columna '{columna}' no encontrada")
            return
        
        df_plot = self.df if estacion is None else self.df[self.df['estacion'] == estacion]
        df_plot = df_plot.sort_values('fecha')
        
        plt.figure(figsize=(15, 6))
        
        if 'estacion' in df_plot.columns and estacion is None:
            for est in df_plot['estacion'].unique()[:5]:  # Máximo 5 estaciones
                data = df_plot[df_plot['estacion'] == est]
                plt.plot(data['fecha'], data[columna], marker='o', label=est, alpha=0.7)
            plt.legend()
        else:
            plt.plot(df_plot['fecha'], df_plot[columna], marker='o', color='steelblue', alpha=0.7)
        
        plt.xlabel('Fecha')
        plt.ylabel(columna)
        plt.title(f'Serie Temporal - {columna} (SIATA)', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ Gráfico guardado en {save_path}")
        
        plt.show()
    
    def analisis_outliers(self, columna=None, method='iqr'):
        """
        Detecta outliers usando IQR o Isolation Forest
        
        Args:
            columna: Columna a analizar
            method: 'iqr' o 'isolation_forest'
        """
        if self.df is None:
            print("❌ Primero carga los datos")
            return
        
        if columna is None:
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
            exclude = ['año', 'mes', 'dia', 'hora', 'dia_semana', 'dia_año']
            available = [col for col in numeric_cols if col not in exclude]
            if not available:
                print("❌ No hay columnas disponibles")
                return
            columna = available[0]
        
        if columna not in self.df.columns:
            print(f"❌ Columna '{columna}' no encontrada")
            return
        
        data = self.df[columna].dropna()
        
        if len(data) == 0:
            print("❌ No hay datos válidos")
            return
        
        print(f"\n🔍 ANÁLISIS DE OUTLIERS - {columna}")
        print("="*60)
        
        if method == 'iqr':
            # Método IQR
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = data[(data < lower_bound) | (data > upper_bound)]
            
            print(f"Método: IQR")
            print(f"  - Q1: {Q1:.2f}")
            print(f"  - Q3: {Q3:.2f}")
            print(f"  - IQR: {IQR:.2f}")
            print(f"  - Límite inferior: {lower_bound:.2f}")
            print(f"  - Límite superior: {upper_bound:.2f}")
            print(f"  - Outliers: {len(outliers)} ({len(outliers)/len(data)*100:.2f}%)")
            
        elif method == 'isolation_forest':
            # Isolation Forest
            iso_forest = IsolationForest(contamination=0.1, random_state=42)
            predictions = iso_forest.fit_predict(data.values.reshape(-1, 1))
            
            outliers = data[predictions == -1]
            
            print(f"Método: Isolation Forest")
            print(f"  - Outliers detectados: {len(outliers)} ({len(outliers)/len(data)*100:.2f}%)")
        
        # Visualización
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        fig.suptitle(f'Detección de Outliers - {columna} (SIATA)', fontsize=14, fontweight='bold')
        
        # Boxplot
        axes[0].boxplot(data, vert=True)
        axes[0].set_ylabel(columna)
        axes[0].set_title('Boxplot')
        axes[0].grid(True, alpha=0.3, axis='y')
        
        # Histograma
        axes[1].hist(data, bins=50, color='skyblue', edgecolor='black', alpha=0.7)
        axes[1].axvline(data.mean(), color='red', linestyle='--', label=f'Media: {data.mean():.2f}')
        axes[1].axvline(data.median(), color='green', linestyle='--', label=f'Mediana: {data.median():.2f}')
        axes[1].set_xlabel(columna)
        axes[1].set_ylabel('Frecuencia')
        axes[1].set_title('Distribución')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.show()
        
        return outliers
    
    def comparacion_estaciones(self, columna=None, save_path=None):
        """Compara estadísticas entre estaciones"""
        if self.df is None or 'estacion' not in self.df.columns:
            print("❌ No hay datos de estaciones")
            return
        
        if columna is None:
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
            exclude = ['año', 'mes', 'dia', 'hora', 'dia_semana', 'dia_año']
            available = [col for col in numeric_cols if col not in exclude]
            if not available:
                return
            columna = available[0]
        
        fig, axes = plt.subplots(2, 1, figsize=(14, 10))
        fig.suptitle(f'Comparación entre Estaciones - {columna} (SIATA)', 
                     fontsize=14, fontweight='bold')
        
        # Boxplot
        estaciones = self.df['estacion'].unique()[:10]  # Máximo 10 estaciones
        data_boxes = [self.df[self.df['estacion'] == est][columna].dropna() for est in estaciones]
        
        axes[0].boxplot(data_boxes, labels=estaciones)
        axes[0].set_ylabel(columna)
        axes[0].set_title('Distribución por Estación')
        axes[0].grid(True, alpha=0.3, axis='y')
        axes[0].tick_params(axis='x', rotation=45)
        
        # Barras con promedios
        promedios = self.df.groupby('estacion')[columna].mean().sort_values(ascending=False)[:10]
        axes[1].barh(promedios.index, promedios.values, color='coral')
        axes[1].set_xlabel(f'{columna} (promedio)')
        axes[1].set_title('Promedio por Estación')
        axes[1].grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ Comparación guardada en {save_path}")
        
        plt.show()
    
    def matriz_correlacion(self, save_path=None):
        """Genera matriz de correlación"""
        if self.df is None:
            print("❌ Primero carga los datos")
            return
        
        # Seleccionar solo columnas numéricas relevantes
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        exclude = ['año', 'mes', 'dia', 'hora', 'dia_semana', 'dia_año']
        available = [col for col in numeric_cols if col not in exclude]
        
        if len(available) < 2:
            print("❌ No hay suficientes columnas para correlación")
            return
        
        corr_matrix = self.df[available].corr()
        
        plt.figure(figsize=(12, 10))
        sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='RdYlGn', 
                   center=0, square=True, linewidths=1, cbar_kws={"shrink": 0.8})
        plt.title('Matriz de Correlación - SIATA', fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ Matriz guardada en {save_path}")
        
        plt.show()
        
        return corr_matrix
    
    def exportar_procesado(self):
        """Exporta datos procesados"""
        if self.df is None:
            print("❌ Primero carga los datos")
            return
        
        output_path = Path("data/processed/siata_processed.csv")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.df.to_csv(output_path, index=False)
        print(f"✅ Datos exportados a {output_path}")


def main():
    """Función principal"""
    print("🌐 SIATA VISUALIZER")
    print("="*60)
    
    visualizer = SIATAVisualizer()
    df = visualizer.cargar_datos()
    
    if df is not None:
        visualizer.estadisticas_basicas()
        visualizer.grafico_series_temporales(save_path="data/images/siata_series.png")
        visualizer.analisis_outliers()
        visualizer.comparacion_estaciones(save_path="data/images/siata_comparacion.png")
        visualizer.matriz_correlacion(save_path="data/images/siata_correlacion.png")
        visualizer.exportar_procesado()


if __name__ == "__main__":
    main()
