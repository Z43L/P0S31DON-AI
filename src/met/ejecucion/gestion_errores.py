from typing import Dict, List, Any, Optional, Type
import re
from datetime import datetime
from loguru import logger

class GestorErrores:
    """Sistema avanzado de gestión y clasificación de errores"""
    
    def __init__(self, configuracion: Dict[str, Any]):
        self.config = configuracion
        self.patrones_error = self._cargar_patrones_error()
        self.estadisticas_errores = {}
        
    def clasificar_error(self, error: Exception) -> Dict[str, Any]:
        """
        Clasifica un error según patrones predefinidos.
        
        Args:
            error: Excepción o mensaje de error
        
        Returns:
            Dict: Clasificación del error con metadata
        """
        mensaje_error = str(error).lower()
        tipo_error = type(error).__name__
        
        clasificacion = {
            'tipo': 'desconocido',
            'categoria': 'no_clasificado',
            'recuperable': False,
            'accion_recomendada': 'escalar_a_mcp',
            'confianza': 0.0
        }
        
        # Clasificación por tipo de excepción
        if tipo_error in ['TimeoutError', 'asyncio.TimeoutError']:
            clasificacion.update({
                'tipo': 'timeout',
                'categoria': 'rendimiento',
                'recuperable': True,
                'accion_recomendada': 'reintentar_con_backoff',
                'confianza': 0.9
            })
        elif tipo_error in ['ConnectionError', 'NetworkError']:
            clasificacion.update({
                'tipo': 'conexion',
                'categoria': 'infraestructura',
                'recuperable': True,
                'accion_recomendada': 'reintentar_inmediato',
                'confianza': 0.8
            })
        
        # Clasificación por patrones en mensaje de error
        for patron, info in self.patrones_error.items():
            if re.search(patron, mensaje_error):
                clasificacion.update(info)
                clasificacion['confianza'] = max(clasificacion['confianza'], info.get('confianza', 0.0))
                break
        
        # Actualizar estadísticas
        self._actualizar_estadisticas(clasificacion)
        
        return clasificacion
    
    def _cargar_patrones_error(self) -> Dict[str, Dict]:
        """Carga los patrones de clasificación de errores"""
        return {
            r'connection refused|cannot connect': {
                'tipo': 'conexion_rechazada',
                'categoria': 'infraestructura',
                'recuperable': True,
                'accion_recomendada': 'reintentar_con_backoff',
                'confianza': 0.85
            },
            r'timeout|timed out': {
                'tipo': 'timeout',
                'categoria': 'rendimiento',
                'recuperable': True,
                'accion_recomendada': 'reintentar_con_backoff',
                'confianza': 0.9
            },
            r'rate limit|too many requests': {
                'tipo': 'rate_limiting',
                'categoria': 'recursos',
                'recuperable': True,
                'accion_recomendada': 'reintentar_con_backoff_exponencial',
                'confianza': 0.8
            },
            r'authentication|unauthorized|invalid token': {
                'tipo': 'autenticacion',
                'categoria': 'seguridad',
                'recuperable': False,
                'accion_recomendada': 'escalar_a_mcp',
                'confianza': 0.95
            },
            r'not found|404|invalid endpoint': {
                'tipo': 'recurso_no_encontrado',
                'categoria': 'configuracion',
                'recuperable': False,
                'accion_recomendada': 'escalar_a_mcp',
                'confianza': 0.7
            }
        }
    
    def obtener_estrategia_reintento(self, clasificacion: Dict) -> Dict[str, Any]:
        """
        Obtiene la estrategia de reintento para un error clasificado.
        
        Args:
            clasificacion: Clasificación del error
        
        Returns:
            Dict: Estrategia de reintento
        """
        estrategias = {
            'reintentar_inmediato': {
                'delay': 1,
                'max_reintentos': 3,
                'backoff': 'ninguno'
            },
            'reintentar_con_backoff': {
                'delay': 2,
                'max_reintentos': 5,
                'backoff': 'lineal',
                'factor': 2
            },
            'reintentar_con_backoff_exponencial': {
                'delay': 1,
                'max_reintentos': 7,
                'backoff': 'exponencial',
                'base': 2
            }
        }
        
        return estrategias.get(
            clasificacion['accion_recomendada'],
            {'delay': 5, 'max_reintentos': 3, 'backoff': 'lineal'}
        )