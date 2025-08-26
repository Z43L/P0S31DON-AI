from typing import Dict, List, Any, Optional
from collections import Counter
import re
from loguru import logger
import numpy as np

class AbstractorProcedimientos:
    """Sistema de abstractación de procedimientos concretos a plantillas generales"""
    
    def __init__(self, configuracion: Dict[str, Any]):
        self.config = configuracion
    
    async def abstractar_procedimiento(self, episodios: List[Dict]) -> Optional[Dict[str, Any]]:
        """
        Abstracta un procedimiento común desde episodios similares.
        
        Args:
            episodios: Episodios del mismo grupo/cluster
        
        Returns:
            Optional[Dict]: Procedimiento abstractado o None
        """
        if not episodios:
            return None
        
        try:
            # Extraer planes de todos los episodios
            planes = [episodio.get('plan_ejecutado', {}) for episodio in episodios]
            
            # Identificar patrones comunes
            procedimiento_abstracto = self._identificar_patron_comun(planes)
            
            # Generalizar parámetros y herramientas
            procedimiento_generalizado = self._generalizar_procedimiento(procedimiento_abstracto, planes)
            
            # Validar la generalización
            if self._validar_generalizacion(procedimiento_generalizado, episodios):
                return procedimiento_generalizado
            
            return None
            
        except Exception as e:
            logger.error(f"Error en abstractación: {e}")
            return None
    
    def _identificar_patron_comun(self, plans: List[Dict]) -> Dict[str, Any]:
        """Identifica el patrón común entre múltiples planes"""
        if not plans:
            return {}
        
        # Analizar estructura común
        estructuras = [self._analizar_estructura_plan(plan) for plan in plans]
        
        # Encontrar secuencia modal de tipos de tarea
        secuencias_tipos = [e['secuencia_tipos'] for e in estructuras]
        secuencia_comun = self._encontrar_secuencia_comun(secuencias_tipos)
        
        return {
            'secuencia_tipos': secuencia_comun,
            'num_tareas_promedio': np.mean([e['num_tareas'] for e in estructuras]),
            'herramientas_comunes': self._encontrar_herramientas_comunes(estructuras)
        }
    
    def _generalizar_procedimiento(self, patron: Dict, plans: List[Dict]) -> Dict[str, Any]:
        """Generaliza el procedimiento basado en el patrón común"""
        # Crear plantilla de procedimiento
        plantilla = {
            'nombre': self._generar_nombre_procedimiento(patron),
            'tipo': 'procedimiento_generalizado',
            'descripcion': self._generar_descripcion(patron),
            'procedimiento': self._construir_procedimiento_generalizado(patron, plans),
            'precondiciones': self._extraer_precondiciones(plans),
            'parametros_generalizados': self._generalizar_parametros(plans),
            'metadata': {
                'origen': 'generalizado_automatico',
                'episodios_base': len(plans),
                'confianza_generalizacion': self._calcular_confianza(patron, plans)
            }
        }
        
        return plantilla
    
    def _validar_generalizacion(self, procedimiento: Dict, episodios: List[Dict]) -> bool:
        """Valida que la generalización sea válida y útil"""
        # Validaciones básicas
        if not procedimiento.get('procedimiento'):
            return False
        
        if len(procedimiento['procedimiento']) == 0:
            return False
        
        # La generalización debe cubrir al menos el 60% de los episodios
        cobertura = self._calcular_cobertura(procedimiento, episodios)
        return cobertura >= self.config.get('umbral_cobertura', 0.6)