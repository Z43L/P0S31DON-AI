from typing import Dict, List, Any, Optional
import numpy as np
from loguru import logger

class EvaluadorCalidadGeneralizacion:
    """Sistema de evaluación de la calidad de las generalizaciones"""
    
    def __init__(self, configuracion: Dict[str, Any]):
        self.config = configuracion
        self.umbral_calidad = configuracion.get('umbral_calidad', 0.6)
    
    async def evaluar_calidad_generalizacion(self, habilidad: Dict, 
                                             episodios_base: List[Dict]) -> Dict[str, Any]:
        """
        Evalúa la calidad de una generalización.
        
        Args:
            habilidad: Habilidad generalizada
            episodios_base: Episodios utilizados para la generalización
        
        Returns:
            Dict: Métricas de calidad de la generalización
        """
        try:
            metricas = {
                'cobertura': self._calcular_cobertura(habilidad, episodios_base),
                'consistencia': self._calcular_consistencia(habilidad, episodios_base),
                'generalidad': self._calcular_generalidad(habilidad),
                'utilidad_predictiva': self._calcular_utilidad_predictiva(habilidad, episodios_base),
                'precision': self._calcular_precision(habilidad, episodios_base)
            }
            
            # Calcular puntuación general de calidad
            metricas['puntuacion_calidad'] = self._calcular_puntuacion_total(metricas)
            metricas['calidad_suficiente'] = metricas['puntuacion_calidad'] >= self.umbral_calidad
            
            return metricas
            
        except Exception as e:
            logger.error(f"Error evaluando calidad: {e}")
            return {'error': str(e)}
    
    def _calcular_cobertura(self, habilidad: Dict, episodios: List[Dict]) -> float:
        """Calcula qué porcentaje de episodios cubre la generalización"""
        if not episodios:
            return 0.0
        
        # Implementación simplificada - en realidad se necesitaría verificar
        # cuántos episodios son consistentes con la habilidad
        return min(1.0, len(episodios) / self.config.get('min_episodios_grupo', 3))
    
    def _calcular_consistencia(self, habilidad: Dict, episodios: List[Dict]) -> float:
        """Calcula la consistencia de la generalización across episodios"""
        # Análisis de varianza en las características relevantes
        return 0.8  # Placeholder para implementación real
    
    def _calcular_puntuacion_total(self, metricas: Dict) -> float:
        """Calcula la puntuación total de calidad"""
        pesos = {
            'cobertura': 0.3,
            'consistencia': 0.25,
            'generalidad': 0.2,
            'utilidad_predictiva': 0.15,
            'precision': 0.1
        }
        
        return sum(metricas[k] * pesos.get(k, 0) for k in metricas if k in pesos)