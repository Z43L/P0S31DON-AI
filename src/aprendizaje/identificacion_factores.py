from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from sklearn.inspection import permutation_importance
from loguru import logger

class IdentificadorFactores:
    """Sistema para identificación de factores clave en éxito/fracaso"""
    
    def __init__(self, configuracion: Dict[str, Any]):
        self.config = configuracion
    
    def identificar_factores_clave(self, modelo, X: pd.DataFrame, y: pd.Series, 
                                 caracteristicas: List[str]) -> Dict[str, Any]:
        """
        Identifica los factores más importantes para predecir éxito/fracaso.
        
        Args:
            modelo: Modelo de machine learning entrenado
            X: Características de entrada
            y: Variable objetivo
            caracteristicas: Nombres de las características
        
        Returns:
            Dict: Factores clave ordenados por importancia
        """
        try:
            # Importancia de características del modelo
            if hasattr(modelo, 'feature_importances_'):
                importancia = modelo.feature_importances_
                indices_importancia = np.argsort(importancia)[::-1]
                
                factores = {}
                for i, idx in enumerate(indices_importancia):
                    if i < len(caracteristicas):
                        factor = caracteristicas[idx]
                        factores[factor] = {
                            'importancia': importancia[idx],
                            'ranking': i + 1
                        }
                
                return factores
            
            # Importancia por permutación (para modelos sin feature_importances_)
            else:
                resultado_permutacion = permutation_importance(
                    modelo, X, y, n_repeats=10, random_state=42
                )
                
                factores = {}
                indices_importancia = np.argsort(resultado_permutacion.importances_mean)[::-1]
                
                for i, idx in enumerate(indices_importancia):
                    if i < len(caracteristicas):
                        factor = caracteristicas[idx]
                        factores[factor] = {
                            'importancia': resultado_permutacion.importances_mean[idx],
                            'importancia_std': resultado_permutacion.importances_std[idx],
                            'ranking': i + 1
                        }
                
                return factores
                
        except Exception as e:
            logger.error(f"Error identificando factores clave: {e}")
            return {}
    
    def analizar_interacciones(self, df: pd.DataFrame, target: str) -> Dict[str, Any]:
        """
        Analiza interacciones entre variables para éxito/fracaso.
        
        Args:
            df: DataFrame con los datos
            target: Variable objetivo
        
        Returns:
            Dict: Interacciones significativas
        """
        interacciones_significativas = {}
        
        # Análisis de interacciones simples (para ejemplo)
        # En implementación real, usar técnicas más sofisticadas
        características = [col for col in df.columns if col != target and df[col].dtype in [np.number]]
        
        for i, col1 in enumerate(características):
            for col2 in características[i+1:]:
                # Calcular alguna medida de interacción
                interacción = self._calcular_interaccion_simple(df, col1, col2, target)
                if interacción['significativa']:
                    clave = f"{col1}_{col2}"
                    interacciones_significativas[clave] = interacción
        
        return interacciones_significativas
    
    def _calcular_interaccion_simple(self, df: pd.DataFrame, col1: str, col2: str, target: str) -> Dict[str, Any]:
        """Calcula una medida simple de interacción entre variables"""
        # Implementación simplificada para ejemplo
        correlation = df[[col1, col2, target]].corr()
        interaccion = correlation.loc[col1, col2] * correlation.loc[col1, target] * correlation.loc[col2, target]
        
        return {
            'variables': [col1, col2],
            'fuerza_interaccion': abs(interaccion),
            'significativa': abs(interaccion) > 0.1,
            'tipo': 'positiva' if interaccion > 0 else 'negativa'
        }