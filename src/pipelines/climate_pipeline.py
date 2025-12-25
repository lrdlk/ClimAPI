"""
Pipelines ETL para procesamiento end-to-end de datos climáticos
Orquesta: Carga → Validación → Limpieza → Transformación
"""

import pandas as pd
from pathlib import Path
from typing import Union, Optional, Callable
import logging
from datetime import datetime

from src.data_loaders import UnifiedDataLoader
from src.validators import DataValidator

logger = logging.getLogger(__name__)


class ClimateDataPipeline:
    """
    Pipeline completo de procesamiento de datos climáticos
    
    Uso:
        pipeline = ClimateDataPipeline("data")
        df_clean = pipeline.execute()
    """
    
    def __init__(self, data_dir: Union[str, Path] = "data"):
        """Inicializa pipeline"""
        self.data_dir = Path(data_dir)
        self.loader = UnifiedDataLoader(data_dir)
        self.history = []
    
    def execute(self, 
                validate: bool = True,
                fill_nulls: bool = True,
                remove_outliers: bool = True,
                resample_freq: Optional[str] = None) -> pd.DataFrame:
        """
        Ejecuta pipeline completo
        
        Args:
            validate: Validar rangos de datos
            fill_nulls: Rellenar valores nulos
            remove_outliers: Eliminar outliers
            resample_freq: Frecuencia de resampleo (ej: 'H', 'D')
        
        Returns:
            DataFrame procesado y limpio
        """
        logger.info("="*60)
        logger.info("INICIANDO PIPELINE DE PROCESAMIENTO")
        logger.info("="*60)
        
        # Step 1: Load
        logger.info("\n[1/5] CARGANDO DATOS...")
        df = self.loader.load_all(standardize=True, resample_freq=None)
        
        if df.empty:
            logger.error("No se cargaron datos")
            return pd.DataFrame()
        
        self._log_step(f"Carga: {len(df)} registros")
        
        # Step 2: Validate
        if validate:
            logger.info("\n[2/5] VALIDANDO DATOS...")
            df, reports = DataValidator.validate_all(df, remove_outliers=remove_outliers)
            self._log_step(f"Validación: {len(df)} registros después de eliminar outliers")
        else:
            logger.info("\n[2/5] VALIDACIÓN OMITIDA")
        
        # Step 3: Fill nulls
        if fill_nulls:
            logger.info("\n[3/5] RELLENANDO VALORES NULOS...")
            initial_nulls = df.isna().sum().sum()
            df = DataValidator.fill_missing(df, method='linear')
            self._log_step(f"Nulos rellenados: {initial_nulls} → {df.isna().sum().sum()}")
        else:
            logger.info("\n[3/5] RELLENADO OMITIDO")
        
        # Step 4: Check for duplicates
        logger.info("\n[4/5] VERIFICANDO DUPLICADOS...")
        dup_subset = [col for col in ['timestamp', 'location'] if col in df.columns]
        if dup_subset:
            duplicates = DataValidator.detect_duplicates(df, subset=dup_subset)
            if duplicates > 0:
                df = df.drop_duplicates(subset=dup_subset, keep='first')
                self._log_step(f"Duplicados eliminados: {duplicates}")
            else:
                self._log_step("Sin duplicados")
        else:
            logger.warning("Columnas timestamp/location no disponibles para verificar duplicados")
        
        # Step 5: Resample if needed
        if resample_freq:
            logger.info(f"\n[5/5] RESAMPLEANDO A {resample_freq}...")
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                numeric_cols = df.select_dtypes(include=['number']).columns
                df_resampled = df.set_index('timestamp').resample(resample_freq).agg({
                    col: 'mean' for col in numeric_cols
                })
                df = df_resampled.reset_index()
                self._log_step(f"Resampleado: {len(df)} registros")
        else:
            logger.info("\n[5/5] RESAMPLEO OMITIDO")
        
        # Summary
        logger.info("\n" + "="*60)
        logger.info("RESUMEN DEL PIPELINE")
        logger.info("="*60)
        logger.info(f"Registros finales: {len(df)}")
        logger.info(f"Columnas: {len(df.columns)}")
        logger.info(f"Periodo: {df['timestamp'].min() if 'timestamp' in df.columns else 'N/A'} "
                   f"→ {df['timestamp'].max() if 'timestamp' in df.columns else 'N/A'}")
        logger.info(f"Nulos restantes: {df.isna().sum().sum()}")
        
        return df
    
    def execute_by_location(self, location: str, **kwargs) -> pd.DataFrame:
        """Ejecuta pipeline para ubicación específica"""
        logger.info(f"\nProcesando {location}...")
        
        df = self.loader.load_location(location)
        
        if df.empty:
            logger.warning(f"No hay datos para {location}")
            return pd.DataFrame()
        
        return self._process_dataframe(df, **kwargs)
    
    def execute_by_source(self, source: str, **kwargs) -> pd.DataFrame:
        """Ejecuta pipeline para fuente específica"""
        logger.info(f"\nProcesando {source}...")
        
        df = self.loader.load_source(source)
        
        if df.empty:
            logger.warning(f"No hay datos para {source}")
            return pd.DataFrame()
        
        return self._process_dataframe(df, **kwargs)
    
    def _process_dataframe(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Procesa un DataFrame específico"""
        if df['timestamp'].isna().any():
            df = df.dropna(subset=['timestamp'])
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        if kwargs.get('fill_nulls'):
            df = DataValidator.fill_missing(df, method='linear')
        
        if kwargs.get('remove_outliers'):
            df, _ = DataValidator.validate_all(df, remove_outliers=True)
        
        return df
    
    def _log_step(self, message: str):
        """Registra paso en historial"""
        self.history.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        logger.info(f"✓ {message}")
    
    def save_processed(self, df: pd.DataFrame, output_path: Union[str, Path] = None) -> Path:
        """
        Guarda DataFrame procesado
        
        Args:
            df: DataFrame a guardar
            output_path: Ruta destino (por defecto: data/processed/)
        
        Returns:
            Ruta del archivo guardado
        """
        if output_path is None:
            output_dir = self.data_dir / "processed"
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / f"clima_procesado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        output_path = Path(output_path)
        df.to_csv(output_path, index=False)
        
        logger.info(f"✓ Guardado: {output_path}")
        return output_path
