"""
OpenWeatherMap Data Visualizer & Processor
==========================================

Procesa y visualiza datos de OpenWeatherMap usando pandas, numpy, matplotlib y sklearn.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
from datetime import datetime
from sklearn.preprocessing import RobustScaler
from sklearn.linear_model import LinearRegression
import warnings
warnings.filterwarnings('ignore')

plt.style.use('ggplot')
sns.set_palette("Set2")


class OpenWeatherVisualizer:
    """Procesador y visualizador de datos de OpenWeatherMap"""
    
    def __init__(self, data_dir="data/openweathermap"):
        self.data_dir = Path(data_dir)
        self.df = None
        self.scaler = RobustScaler()
        
    def cargar_datos(self):
        """Carga archivos JSON de OpenWeatherMap"""
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
                
                # Determinar tipo de respuesta
                if 'list' in data:  # Forecast
                    for item in data['list']:
                        row = self._extraer_forecast(item, file.stem, data.get('city', {}))
                        all_data.append(row)
                elif 'current' in data:  # One Call API
                    for item in data.get('hourly', []):
                        row = self._extraer_onecall(item, file.stem, data.get('lat'), data.get('lon'))
                        all_data.append(row)
                else:  # Current weather
                    row = self._extraer_current(data, file.stem)
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
    
    def _extraer_forecast(self, item, ciudad, city_info):
        """Extrae datos de forecast"""
        return {
            'ciudad': ciudad,
            'timestamp': item.get('dt'),
            'fecha': datetime.fromtimestamp(item.get('dt', 0)),
            'temperatura': item.get('main', {}).get('temp'),
            'temp_min': item.get('main', {}).get('temp_min'),
            'temp_max': item.get('main', {}).get('temp_max'),
            'feels_like': item.get('main', {}).get('feels_like'),
            'presion': item.get('main', {}).get('pressure'),
            'humedad': item.get('main', {}).get('humidity'),
            'descripcion': item.get('weather', [{}])[0].get('description', ''),
            'nubosidad': item.get('clouds', {}).get('all'),
            'viento_vel': item.get('wind', {}).get('speed'),
            'viento_dir': item.get('wind', {}).get('deg'),
            'precipitacion': item.get('rain', {}).get('3h', 0),
            'tipo': 'forecast'
        }
    
    def _extraer_onecall(self, item, ciudad, lat, lon):
        """Extrae datos de One Call API"""
        return {
            'ciudad': ciudad,
            'timestamp': item.get('dt'),
            'fecha': datetime.fromtimestamp(item.get('dt', 0)),
            'temperatura': item.get('temp'),
            'feels_like': item.get('feels_like'),
            'presion': item.get('pressure'),
            'humedad': item.get('humidity'),
            'descripcion': item.get('weather', [{}])[0].get('description', ''),
            'nubosidad': item.get('clouds'),
            'viento_vel': item.get('wind_speed'),
            'viento_dir': item.get('wind_deg'),
            'precipitacion': item.get('rain', {}).get('1h', 0),
            'tipo': 'onecall'
        }
    
    def _extraer_current(self, data, ciudad):
        """Extrae datos de current weather"""
        return {
            'ciudad': ciudad,
            'timestamp': data.get('dt'),
            'fecha': datetime.fromtimestamp(data.get('dt', 0)),
            'temperatura': data.get('main', {}).get('temp'),
            'temp_min': data.get('main', {}).get('temp_min'),
            'temp_max': data.get('main', {}).get('temp_max'),
            'feels_like': data.get('main', {}).get('feels_like'),
            'presion': data.get('main', {}).get('pressure'),
            'humedad': data.get('main', {}).get('humidity'),
            'descripcion': data.get('weather', [{}])[0].get('description', ''),
            'nubosidad': data.get('clouds', {}).get('all'),
            'viento_vel': data.get('wind', {}).get('speed'),
            'viento_dir': data.get('wind', {}).get('deg'),
            'tipo': 'current'
        }
    
    def _procesar_datos(self):
        """Procesa DataFrame"""
        if self.df is None:
            return
        
        # Convertir a datetime
        self.df['fecha'] = pd.to_datetime(self.df['fecha'])
        self.df['hora'] = self.df['fecha'].dt.hour
        self.df['dia'] = self.df['fecha'].dt.day
        self.df['mes'] = self.df['fecha'].dt.month
        self.df['dia_semana'] = self.df['fecha'].dt.dayofweek
        
        # Convertir temperatura de Kelvin a Celsius si es necesario
        if self.df['temperatura'].mean() > 100:  # Probablemente en Kelvin
            temp_cols = ['temperatura', 'temp_min', 'temp_max', 'feels_like']
            for col in temp_cols:
                if col in self.df.columns:
                    self.df[col] = self.df[col] - 273.15
        
        # Calcular índice de confort
        self.df['indice_confort'] = self.df['temperatura'] - np.abs(self.df['temperatura'] - self.df['feels_like'])
    
    def estadisticas_basicas(self):
        """Estadísticas descriptivas"""
        if self.df is None:
            print("❌ Primero carga los datos")
            return
        
        print("\n" + "="*60)
        print("📊 ESTADÍSTICAS - OPENWEATHERMAP")
        print("="*60)
        
        print(f"\n📅 Periodo: {self.df['fecha'].min()} a {self.df['fecha'].max()}")
        print(f"🌍 Ciudades: {', '.join(self.df['ciudad'].unique())}")
        print(f"📈 Total registros: {len(self.df)}")
        
        print(f"\n🌡️ Temperatura:")
        print(f"  - Promedio: {self.df['temperatura'].mean():.2f}°C")
        print(f"  - Máxima: {self.df['temperatura'].max():.2f}°C")
        print(f"  - Mínima: {self.df['temperatura'].min():.2f}°C")
        print(f"  - Sensación térmica promedio: {self.df['feels_like'].mean():.2f}°C")
        
        print(f"\n💧 Humedad:")
        print(f"  - Promedio: {self.df['humedad'].mean():.2f}%")
        
        print(f"\n☁️ Nubosidad:")
        print(f"  - Promedio: {self.df['nubosidad'].mean():.2f}%")
        
        print(f"\n🌬️ Viento:")
        print(f"  - Velocidad promedio: {self.df['viento_vel'].mean():.2f} m/s")
        print(f"  - Velocidad máxima: {self.df['viento_vel'].max():.2f} m/s")
        
        # Condiciones climáticas más comunes
        print(f"\n🌤️ Condiciones más frecuentes:")
        top_conditions = self.df['descripcion'].value_counts().head(5)
        for cond, count in top_conditions.items():
            print(f"  - {cond}: {count} ({count/len(self.df)*100:.1f}%)")
    
    def grafico_temperatura_feels_like(self, save_path=None):
        """Compara temperatura real vs sensación térmica"""
        if self.df is None:
            print("❌ Primero carga los datos")
            return
        
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle('Temperatura Real vs Sensación Térmica - OpenWeatherMap', 
                     fontsize=14, fontweight='bold')
        
        # Scatter plot
        axes[0].scatter(self.df['temperatura'], self.df['feels_like'], 
                       alpha=0.5, c=self.df['humedad'], cmap='viridis')
        axes[0].plot([self.df['temperatura'].min(), self.df['temperatura'].max()],
                    [self.df['temperatura'].min(), self.df['temperatura'].max()],
                    'r--', label='Línea 1:1')
        axes[0].set_xlabel('Temperatura Real (°C)')
        axes[0].set_ylabel('Sensación Térmica (°C)')
        axes[0].set_title('Correlación')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Diferencia por ciudad
        self.df['diferencia'] = np.abs(self.df['temperatura'] - self.df['feels_like'])
        diff_por_ciudad = self.df.groupby('ciudad')['diferencia'].mean().sort_values()
        
        axes[1].barh(diff_por_ciudad.index, diff_por_ciudad.values, color='coral')
        axes[1].set_xlabel('Diferencia Promedio (°C)')
        axes[1].set_title('Diferencia Real vs Feels Like por Ciudad')
        axes[1].grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ Gráfico guardado en {save_path}")
        
        plt.show()
    
    def analisis_viento(self, save_path=None):
        """Analiza dirección y velocidad del viento"""
        if self.df is None or 'viento_dir' not in self.df.columns:
            print("❌ No hay datos de viento")
            return
        
        fig = plt.figure(figsize=(12, 6))
        
        # Rosa de vientos (polar plot)
        ax1 = fig.add_subplot(121, projection='polar')
        
        # Agrupar por dirección (bins de 30 grados)
        bins = np.arange(0, 361, 30)
        self.df['viento_bin'] = pd.cut(self.df['viento_dir'], bins=bins, labels=bins[:-1])
        
        wind_grouped = self.df.groupby('viento_bin')['viento_vel'].mean()
        
        theta = np.deg2rad(wind_grouped.index.astype(float))
        radii = wind_grouped.values
        
        bars = ax1.bar(theta, radii, width=np.deg2rad(30), bottom=0.0, alpha=0.7)
        
        # Colorear por velocidad
        colors = plt.cm.viridis(radii / radii.max())
        for bar, color in zip(bars, colors):
            bar.set_facecolor(color)
        
        ax1.set_theta_zero_location('N')
        ax1.set_theta_direction(-1)
        ax1.set_title('Rosa de Vientos', fontweight='bold', pad=20)
        
        # Distribución de velocidad
        ax2 = fig.add_subplot(122)
        ax2.hist(self.df['viento_vel'], bins=30, color='skyblue', edgecolor='black', alpha=0.7)
        ax2.set_xlabel('Velocidad del Viento (m/s)')
        ax2.set_ylabel('Frecuencia')
        ax2.set_title('Distribución de Velocidad del Viento', fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ Análisis de viento guardado en {save_path}")
        
        plt.show()
    
    def tendencia_temperatura(self, ciudad=None, save_path=None):
        """Analiza tendencia temporal de temperatura"""
        if self.df is None:
            print("❌ Primero carga los datos")
            return
        
        df_plot = self.df if ciudad is None else self.df[self.df['ciudad'] == ciudad]
        
        # Regresión lineal
        df_plot = df_plot.sort_values('fecha')
        df_plot['timestamp_num'] = (df_plot['fecha'] - df_plot['fecha'].min()).dt.total_seconds()
        
        X = df_plot['timestamp_num'].values.reshape(-1, 1)
        y = df_plot['temperatura'].values
        
        model = LinearRegression()
        model.fit(X, y)
        y_pred = model.predict(X)
        
        # Gráfico
        plt.figure(figsize=(14, 6))
        
        for c in df_plot['ciudad'].unique():
            data = df_plot[df_plot['ciudad'] == c]
            plt.scatter(data['fecha'], data['temperatura'], alpha=0.5, label=c, s=30)
        
        plt.plot(df_plot['fecha'], y_pred, 'r--', linewidth=2, label=f'Tendencia (R²={model.score(X, y):.3f})')
        
        plt.xlabel('Fecha')
        plt.ylabel('Temperatura (°C)')
        plt.title('Tendencia de Temperatura - OpenWeatherMap', fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ Tendencia guardada en {save_path}")
        
        plt.show()
        
        print(f"\n📈 Pendiente: {model.coef_[0]:.6f} °C/segundo")
        print(f"   Equivalente a: {model.coef_[0] * 86400:.4f} °C/día")
    
    def exportar_procesado(self):
        """Exporta datos procesados"""
        if self.df is None:
            print("❌ Primero carga los datos")
            return
        
        output_path = Path("data/processed/openweather_processed.csv")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.df.to_csv(output_path, index=False)
        print(f"✅ Datos exportados a {output_path}")


def main():
    """Función principal"""
    print("🌤️ OPENWEATHERMAP VISUALIZER")
    print("="*60)
    
    visualizer = OpenWeatherVisualizer()
    df = visualizer.cargar_datos()
    
    if df is not None:
        visualizer.estadisticas_basicas()
        visualizer.grafico_temperatura_feels_like(save_path="data/images/openweather_feels_like.png")
        visualizer.analisis_viento(save_path="data/images/openweather_viento.png")
        visualizer.tendencia_temperatura(save_path="data/images/openweather_tendencia.png")
        visualizer.exportar_procesado()


if __name__ == "__main__":
    main()
