"""
Open-Meteo Data Visualizer & Processor
======================================

Procesa y visualiza datos de Open-Meteo usando pandas, numpy, matplotlib y sklearn.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("muted")


class OpenMeteoVisualizer:
    """Procesador y visualizador de datos de Open-Meteo"""
    
    def __init__(self, data_dir="data/openmeteo"):
        self.data_dir = Path(data_dir)
        self.df_hourly = None
        self.df_daily = None
        self.scaler = MinMaxScaler()
        
    def cargar_datos(self):
        """Carga archivos CSV de Open-Meteo"""
        hourly_files = list(self.data_dir.glob("*_hourly.csv"))
        daily_files = list(self.data_dir.glob("*_daily.csv"))
        
        print(f"📂 Archivos hourly: {len(hourly_files)}")
        print(f"📂 Archivos daily: {len(daily_files)}")
        
        # Cargar datos horarios
        if hourly_files:
            dfs_hourly = []
            for file in hourly_files:
                try:
                    df = pd.read_csv(file)
                    # Extraer ciudad del nombre del archivo
                    ciudad = file.stem.split('_')[1]
                    df['ciudad'] = ciudad
                    df['archivo'] = file.name
                    dfs_hourly.append(df)
                except Exception as e:
                    print(f"⚠️ Error en {file.name}: {e}")
            
            if dfs_hourly:
                self.df_hourly = pd.concat(dfs_hourly, ignore_index=True)
                self._procesar_hourly()
                print(f"✅ Datos horarios: {len(self.df_hourly)} registros")
        
        # Cargar datos diarios
        if daily_files:
            dfs_daily = []
            for file in daily_files:
                try:
                    df = pd.read_csv(file)
                    ciudad = file.stem.split('_')[1]
                    df['ciudad'] = ciudad
                    df['archivo'] = file.name
                    dfs_daily.append(df)
                except Exception as e:
                    print(f"⚠️ Error en {file.name}: {e}")
            
            if dfs_daily:
                self.df_daily = pd.concat(dfs_daily, ignore_index=True)
                self._procesar_daily()
                print(f"✅ Datos diarios: {len(self.df_daily)} registros")
        
        return self.df_hourly, self.df_daily
    
    def _procesar_hourly(self):
        """Procesa datos horarios"""
        if self.df_hourly is None:
            return
        
        # Convertir time a datetime
        if 'time' in self.df_hourly.columns:
            self.df_hourly['time'] = pd.to_datetime(self.df_hourly['time'])
            self.df_hourly['fecha'] = self.df_hourly['time'].dt.date
            self.df_hourly['hora'] = self.df_hourly['time'].dt.hour
            self.df_hourly['dia_semana'] = self.df_hourly['time'].dt.dayofweek
        
        # Renombrar columnas si es necesario
        if 'temperature_2m' in self.df_hourly.columns:
            self.df_hourly.rename(columns={'temperature_2m': 'temperatura'}, inplace=True)
        if 'relative_humidity_2m' in self.df_hourly.columns:
            self.df_hourly.rename(columns={'relative_humidity_2m': 'humedad'}, inplace=True)
    
    def _procesar_daily(self):
        """Procesa datos diarios"""
        if self.df_daily is None:
            return
        
        if 'time' in self.df_daily.columns:
            self.df_daily['time'] = pd.to_datetime(self.df_daily['time'])
            self.df_daily['dia_semana'] = self.df_daily['time'].dt.dayofweek
            self.df_daily['mes'] = self.df_daily['time'].dt.month
        
        # Renombrar columnas
        rename_map = {
            'temperature_2m_max': 'temp_max',
            'temperature_2m_min': 'temp_min',
            'precipitation_sum': 'precipitacion',
            'wind_speed_10m_max': 'viento_max'
        }
        self.df_daily.rename(columns=rename_map, inplace=True)
        
        # Calcular promedio
        if 'temp_max' in self.df_daily.columns and 'temp_min' in self.df_daily.columns:
            self.df_daily['temp_promedio'] = (self.df_daily['temp_max'] + self.df_daily['temp_min']) / 2
    
    def estadisticas_basicas(self):
        """Estadísticas descriptivas"""
        print("\n" + "="*60)
        print("📊 ESTADÍSTICAS - OPEN-METEO")
        print("="*60)
        
        if self.df_daily is not None:
            print("\n📅 DATOS DIARIOS:")
            print(f"  - Registros: {len(self.df_daily)}")
            print(f"  - Ciudades: {', '.join(self.df_daily['ciudad'].unique())}")
            
            if 'temp_max' in self.df_daily.columns:
                print(f"\n🌡️ Temperatura:")
                print(f"  - Máxima promedio: {self.df_daily['temp_max'].mean():.2f}°C")
                print(f"  - Mínima promedio: {self.df_daily['temp_min'].mean():.2f}°C")
            
            if 'precipitacion' in self.df_daily.columns:
                print(f"\n💧 Precipitación:")
                print(f"  - Total: {self.df_daily['precipitacion'].sum():.2f} mm")
                print(f"  - Promedio diario: {self.df_daily['precipitacion'].mean():.2f} mm")
        
        if self.df_hourly is not None:
            print(f"\n⏰ DATOS HORARIOS:")
            print(f"  - Registros: {len(self.df_hourly)}")
            
            if 'temperatura' in self.df_hourly.columns:
                print(f"  - Temp promedio: {self.df_hourly['temperatura'].mean():.2f}°C")
    
    def grafico_temperatura_horaria(self, ciudad=None, save_path=None):
        """Gráfico de temperatura por hora del día"""
        if self.df_hourly is None or 'temperatura' not in self.df_hourly.columns:
            print("❌ No hay datos horarios de temperatura")
            return
        
        df_plot = self.df_hourly if ciudad is None else self.df_hourly[self.df_hourly['ciudad'] == ciudad]
        
        # Agrupar por hora
        temp_por_hora = df_plot.groupby(['hora', 'ciudad'])['temperatura'].mean().reset_index()
        
        plt.figure(figsize=(14, 6))
        
        for c in temp_por_hora['ciudad'].unique():
            data = temp_por_hora[temp_por_hora['ciudad'] == c]
            plt.plot(data['hora'], data['temperatura'], marker='o', label=c, linewidth=2)
        
        plt.xlabel('Hora del día', fontsize=12)
        plt.ylabel('Temperatura (°C)', fontsize=12)
        plt.title('Patrón de Temperatura por Hora - Open-Meteo', fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.xticks(range(0, 24))
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ Gráfico guardado en {save_path}")
        
        plt.show()
    
    def comparacion_ciudades(self, save_path=None):
        """Compara estadísticas entre ciudades"""
        if self.df_daily is None:
            print("❌ No hay datos diarios")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Comparación entre Ciudades - Open-Meteo', fontsize=16, fontweight='bold')
        
        ciudades = self.df_daily['ciudad'].unique()
        
        # Temperatura máxima
        if 'temp_max' in self.df_daily.columns:
            temp_data = [self.df_daily[self.df_daily['ciudad'] == c]['temp_max'].dropna() for c in ciudades]
            axes[0, 0].boxplot(temp_data, labels=ciudades)
            axes[0, 0].set_title('Temperatura Máxima')
            axes[0, 0].set_ylabel('°C')
            axes[0, 0].grid(True, alpha=0.3)
        
        # Temperatura mínima
        if 'temp_min' in self.df_daily.columns:
            temp_data = [self.df_daily[self.df_daily['ciudad'] == c]['temp_min'].dropna() for c in ciudades]
            axes[0, 1].boxplot(temp_data, labels=ciudades)
            axes[0, 1].set_title('Temperatura Mínima')
            axes[0, 1].set_ylabel('°C')
            axes[0, 1].grid(True, alpha=0.3)
        
        # Precipitación
        if 'precipitacion' in self.df_daily.columns:
            precip_totals = self.df_daily.groupby('ciudad')['precipitacion'].sum()
            axes[1, 0].bar(precip_totals.index, precip_totals.values, color='steelblue')
            axes[1, 0].set_title('Precipitación Total')
            axes[1, 0].set_ylabel('mm')
            axes[1, 0].grid(True, alpha=0.3, axis='y')
        
        # Viento
        if 'viento_max' in self.df_daily.columns:
            viento_data = [self.df_daily[self.df_daily['ciudad'] == c]['viento_max'].dropna() for c in ciudades]
            axes[1, 1].boxplot(viento_data, labels=ciudades)
            axes[1, 1].set_title('Velocidad Máxima del Viento')
            axes[1, 1].set_ylabel('km/h')
            axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ Comparación guardada en {save_path}")
        
        plt.show()
    
    def prediccion_temperatura(self):
        """Modelo simple de predicción con Random Forest"""
        if self.df_hourly is None or 'temperatura' not in self.df_hourly.columns:
            print("❌ No hay datos suficientes")
            return
        
        print("\n🤖 MODELO DE PREDICCIÓN")
        print("="*60)
        
        # Preparar features
        df_model = self.df_hourly.copy()
        df_model = df_model.dropna(subset=['temperatura'])
        
        features = ['hora', 'dia_semana']
        if 'humedad' in df_model.columns:
            features.append('humedad')
        
        df_model = df_model.dropna(subset=features)
        
        X = df_model[features]
        y = df_model['temperatura']
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Entrenar
        rf = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        rf.fit(X_train, y_train)
        
        # Evaluar
        train_score = rf.score(X_train, y_train)
        test_score = rf.score(X_test, y_test)
        
        print(f"\n📊 Resultados:")
        print(f"  - R² Train: {train_score:.4f}")
        print(f"  - R² Test: {test_score:.4f}")
        print(f"  - Features: {', '.join(features)}")
        
        # Importancia de features
        importances = pd.DataFrame({
            'feature': features,
            'importance': rf.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(f"\n🔍 Importancia de variables:")
        print(importances.to_string(index=False))
        
        return rf, importances
    
    def exportar_procesado(self):
        """Exporta datos procesados"""
        output_dir = Path("data/processed")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if self.df_hourly is not None:
            path = output_dir / "openmeteo_hourly_processed.csv"
            self.df_hourly.to_csv(path, index=False)
            print(f"✅ Hourly exportado a {path}")
        
        if self.df_daily is not None:
            path = output_dir / "openmeteo_daily_processed.csv"
            self.df_daily.to_csv(path, index=False)
            print(f"✅ Daily exportado a {path}")


def main():
    """Función principal"""
    print("🌐 OPEN-METEO VISUALIZER")
    print("="*60)
    
    visualizer = OpenMeteoVisualizer()
    visualizer.cargar_datos()
    
    if visualizer.df_daily is not None or visualizer.df_hourly is not None:
        visualizer.estadisticas_basicas()
        visualizer.grafico_temperatura_horaria(save_path="data/images/openmeteo_temp_horaria.png")
        visualizer.comparacion_ciudades(save_path="data/images/openmeteo_comparacion.png")
        visualizer.prediccion_temperatura()
        visualizer.exportar_procesado()


if __name__ == "__main__":
    main()
