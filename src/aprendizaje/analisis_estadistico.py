from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from scipy import stats
from loguru import logger

class AnalizadorEstadistico:
    """Componente de análisis estadístico para éxito/fracaso"""
    
    def __init__(self, configuracion: Dict[str, Any]):
        self.config = configuracion
    
    def analizar_episodios(self, df_episodios: pd.DataFrame) -> Dict[str, Any]:
        """
        Realiza análisis estadístico comparativo entre episodios exitosos y fallidos.
        
        Args:
            df_episodios: DataFrame con episodios preprocesados
        
        Returns:
            Dict: Resultados del análisis estadístico
        """
        # Separar episodios exitosos y fallidos
        exitosos = df_episodios[df_episodios['exito'] == 1]
        fallidos = df_episodios[df_episodios['exito'] == 0]
        
        if len(exitosos) == 0 or len(fallidos) == 0:
            logger.warning("No hay suficientes datos para análisis comparativo")
            return {}
        
        resultados = {
            'conteos': {
                'total': len(df_episodios),
                'exitosos': len(exitosos),
                'fallidos': len(fallidos),
                'tasa_exito_global': len(exitosos) / len(df_episodios)
            },
            'comparativas': {},
            'correlaciones': {}
        }
        
        # Análisis comparativo por características numéricas
        características_numericas = ['duracion_total', 'num_tareas', 'tasa_exito_tareas', 'num_herramientas_unicas']
        
        for caracteristica in características_numericas:
            if caracteristica in df_episodios.columns:
                comparativa = self._comparar_distribuciones(
                    exitosos[caracteristica], 
                    fallidos[caracteristica], 
                    caracteristica
                )
                resultados['comparativas'][caracteristica] = comparativa
        
        # Análisis de correlaciones
        resultados['correlaciones'] = self._calcular_correlaciones(df_episodios)
        
        return resultados
    
    def _comparar_distribuciones(self, muestra1: pd.Series, muestra2: pd.Series, nombre: str) -> Dict[str, Any]:
        """Compara dos distribuciones usando tests estadísticos"""
        try:
            # Test t para muestras independientes
            t_stat, p_value = stats.ttest_ind(muestra1.dropna(), muestra2.dropna())
            
            return {
                'media_grupo1': np.mean(muestra1),
                'media_grupo2': np.mean(muestra2),
                'diferencia_medias': np.mean(muestra1) - np.mean(muestra2),
                't_statistic': t_stat,
                'p_value': p_value,
                'diferencia_significativa': p_value < 0.05,
                'size_effect': self._calcular_tamaño_efecto(muestra1, muestra2)
            }
        except Exception as e:
            logger.error(f"Error en comparación de distribuciones: {e}")
            return {}
    
    def _calcular_tamaño_efecto(self, muestra1: pd.Series, muestra2: pd.Series) -> float:
        """Calcula el tamaño del efecto (Cohen's d)"""
        n1, n2 = len(muestra1), len(muestra2)
        var1, var2 = np.var(muestra1, ddof=1), np.var(muestra2, ddof=1)
        
        pooled_var = ((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2)
        d = (np.mean(muestra1) - np.mean(muestra2)) / np.sqrt(pooled_var)
        
        return d
    
    def _calcular_correlaciones(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calcula correlaciones entre variables y éxito"""
        numeric_df = df.select_dtypes(include=[np.number])
        if 'exito' not in numeric_df.columns:
            return {}
        
        correlation_matrix = numeric_df.corr()
        exito_correlations = correlation_matrix['exito'].drop('exito', errors='ignore')
        
        return {
            'correlaciones_exito': exito_correlations.to_dict(),
            'correlaciones_fuertes': exito_correlations[abs(exito_correlations) > 0.3].to_dict()
        }