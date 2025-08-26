from typing import Dict, Any, Optional
import time
from datetime import datetime
import uuid
from loguru import logger

class TracingIntegrado:
    """
    Sistema de tracing para monitorizar el flujo completo entre módulos.
    """
    
    def __init__(self, configuracion: Dict[str, Any]):
        self.config = configuracion
        self.traces_activos: Dict[str, Dict] = {}
        
    def iniciar_trace(self, operacion: str, metadata: Optional[Dict] = None) -> str:
        """
        Inicia un nuevo trace para una operación.
        
        Args:
            operacion: Nombre de la operación
            metadata: Metadatos adicionales
        
        Returns:
            str: ID del trace iniciado
        """
        trace_id = f"trace_{uuid.uuid4().hex[:16]}"
        
        self.traces_activos[trace_id] = {
            'operacion': operacion,
            'inicio': time.time(),
            'metadata': metadata or {},
            'spans': [],
            'estado': 'activo'
        }
        
        logger.debug(f"Trace iniciado: {trace_id} - {operacion}")
        return trace_id
    
    def agregar_span(self, trace_id: str, modulo: str, accion: str, 
                    metadata: Optional[Dict] = None) -> None:
        """
        Agrega un nuevo span al trace especificado.
        
        Args:
            trace_id: ID del trace
            modulo: Módulo que ejecuta la acción
            accion: Descripción de la acción
            metadata: Metadatos adicionales del span
        """
        if trace_id not in self.traces_activos:
            logger.warning(f"Trace {trace_id} no encontrado")
            return
        
        span = {
            'modulo': modulo,
            'accion': accion,
            'timestamp': time.time(),
            'metadata': metadata or {},
            'duracion': None
        }
        
        self.traces_activos[trace_id]['spans'].append(span)
    
    def finalizar_span(self, trace_id: str, modulo: str, exito: bool = True, 
                      error: Optional[str] = None) -> None:
        """
        Finaliza el span activo para un módulo específico.
        
        Args:
            trace_id: ID del trace
            modulo: Módulo que finaliza la acción
            exito: Si la ejecución fue exitosa
            error: Mensaje de error si aplica
        """
        if trace_id not in self.traces_activos:
            return
        
        # Encontrar el último span del módulo
        for span in reversed(self.traces_activos[trace_id]['spans']):
            if span['modulo'] == modulo and span['duracion'] is None:
                span['duracion'] = time.time() - span['timestamp']
                span['exito'] = exito
                if error:
                    span['error'] = error
                break
    
    def finalizar_trace(self, trace_id: str, exito: bool = True) -> Optional[Dict]:
        """
        Finaliza un trace y devuelve sus datos completos.
        
        Args:
            trace_id: ID del trace a finalizar
            exito: Si el trace completo fue exitoso
        
        Returns:
            Optional[Dict]: Datos completos del trace o None si no existe
        """
        if trace_id not in self.traces_activos:
            return None
        
        trace = self.traces_activos[trace_id]
        trace['fin'] = time.time()
        trace['duracion_total'] = trace['fin'] - trace['inicio']
        trace['estado'] = 'completado'
        trace['exito_global'] = exito
        
        # Calcular métricas agregadas
        trace['metricas'] = self._calcular_metricas_trace(trace)
        
        logger.debug(f"Trace finalizado: {trace_id} - Duración: {trace['duracion_total']:.2f}s")
        
        # Remover de traces activos y devolver
        return self.traces_activos.pop(trace_id)