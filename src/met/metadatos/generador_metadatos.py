from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import time
from enum import Enum
from loguru import logger

class EstadoEjecucion(Enum):
    """Estados posibles de una ejecución de tarea"""
    EXITO = "exito"
    FALLO = "fallo"
    TIMEOUT = "timeout"
    CANCELADO = "cancelado"
    PARCIAL = "parcial"

class GeneradorMetadatos:
    """Sistema principal de generación y gestión de metadatos de ejecución"""
    
    def __init__(self, sistema_memoria, configuracion: Dict[str, Any]):
        self.memoria = sistema_memoria
        self.config = configuracion
        self.metricas_activas = {}
        
        logger.info("Generador de Metadatos inicializado correctamente")
    
    async def generar_metadatos_ejecucion(self, tarea: Dict, resultado: Dict, 
                                        contexto_ejecucion: Dict) -> Dict[str, Any]:
        """
        Genera metadatos completos para una ejecución de tarea.
        
        Args:
            tarea: Definición de la tarea ejecutada
            resultado: Resultado de la ejecución
            contexto_ejecucion: Contexto durante la ejecución
        
        Returns:
            Dict: Metadatos estructurados de la ejecución
        """
        try:
            # 1. Calcular métricas básicas de ejecución
            metricas_basicas = self._calcular_metricas_basicas(resultado)
            
            # 2. Evaluar resultado y determinar estado
            estado = self._determinar_estado_ejecucion(resultado, metricas_basicas)
            
            # 3. Generar metadatos completos
            metadatos = {
                **metricas_basicas,
                'estado': estado.value,
                'tarea_id': tarea.get('id'),
                'tipo_tarea': tarea.get('tipo'),
                'herramienta_utilizada': resultado.get('herramienta'),
                'parametros_ejecucion': tarea.get('parametros', {}),
                'timestamp_ejecucion': datetime.now().isoformat(),
                'contexto_ejecucion': contexto_ejecucion,
                'diagnostico': self._generar_diagnostico(resultado, estado)
            }
            
            # 4. Enriquecer con métricas avanzadas
            metadatos.update(self._calcular_metricas_avanzadas(metadatos))
            
            # 5. Registrar en el sistema de memoria
            await self._registrar_metadatos(metadatos)
            
            logger.debug(f"Metadatos generados para tarea {tarea.get('id')}")
            return metadatos
            
        except Exception as e:
            logger.error(f"Error generando metadatos: {e}")
            return self._generar_metadatos_error(e, tarea)
    
    def _calcular_metricas_basicas(self, resultado: Dict) -> Dict[str, Any]:
        """Calcula las métricas básicas de ejecución"""
        tiempo_inicio = resultado.get('timestamp_inicio')
        tiempo_fin = resultado.get('timestamp_fin')
        
        if tiempo_inicio and tiempo_fin:
            if isinstance(tiempo_inicio, str):
                tiempo_inicio = datetime.fromisoformat(tiempo_inicio.replace('Z', '+00:00'))
            if isinstance(tiempo_fin, str):
                tiempo_fin = datetime.fromisoformat(tiempo_fin.replace('Z', '+00:00'))
            
            duracion = (tiempo_fin - tiempo_inicio).total_seconds()
        else:
            duracion = resultado.get('duracion', 0)
        
        return {
            'duracion_segundos': duracion,
            'timestamp_inicio': tiempo_inicio.isoformat() if isinstance(tiempo_inicio, datetime) else tiempo_inicio,
            'timestamp_fin': tiempo_fin.isoformat() if isinstance(tiempo_fin, datetime) else tiempo_fin,
            'exito': resultado.get('exito', False)
        }
    
    def _determinar_estado_ejecucion(self, resultado: Dict, metricas: Dict) -> EstadoEjecucion:
        """Determina el estado final de la ejecución"""
        if resultado.get('exito', False):
            return EstadoEjecucion.EXITO
        
        error = resultado.get('error', '')
        if 'timeout' in error.lower():
            return EstadoEjecucion.TIMEOUT
        elif 'cancel' in error.lower():
            return EstadoEjecucion.CANCELADO
        
        # Evaluar si el fallo fue parcial o completo
        if resultado.get('resultado_parcial'):
            return EstadoEjecucion.PARCIAL
        
        return EstadoEjecucion.FALLO
    
    def _generar_diagnostico(self, resultado: Dict, estado: EstadoEjecucion) -> Dict[str, Any]:
        """Genera diagnóstico detallado del resultado de ejecución"""
        error = resultado.get('error', '')
        
        diagnostico = {
            'estado': estado.value,
            'error': error,
            'tipo_error': type(resultado.get('exception')).__name__ if resultado.get('exception') else 'Unknown',
            'recuperable': self._es_error_recuperable(error),
            'accion_recomendada': self._sugerir_accion_remediacion(estado, error)
        }
        
        # Agregar información específica por tipo de error
        if 'timeout' in error.lower():
            diagnostico['detalles'] = {
                'tipo': 'timeout',
                'umbral_sugerido': resultado.get('timeout_original', 0) * 1.5
            }
        elif 'connection' in error.lower():
            diagnostico['detalles'] = {
                'tipo': 'conexion',
                'reintentos_realizados': resultado.get('reintentos', 0)
            }
        
        return diagnostico