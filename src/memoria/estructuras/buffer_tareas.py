from typing import Dict, List, Any, Optional, Deque
from collections import deque
from datetime import datetime

class BufferTareas:
    """
    Buffer circular para almacenamiento temporal de resultados de tareas
    durante la ejecución de un objetivo.
    """
    
    def __init__(self, capacidad_maxima: int = 100):
        """
        Inicializa el buffer de tareas.
        
        Args:
            capacidad_maxima: Número máximo de tareas en buffer
        """
        self._buffer: Deque[Dict[str, Any]] = deque(maxlen=capacidad_maxima)
        self._indices: Dict[str, int] = {}  # Mapa de task_id a índice
    
    def agregar_tarea(self, tarea_id: str, resultado: Dict[str, Any]) -> None:
        """
        Agrega un resultado de tarea al buffer.
        
        Args:
            tarea_id: Identificador de la tarea
            resultado: Resultado de la ejecución
        """
        entrada = {
            'tarea_id': tarea_id,
            'resultado': resultado,
            'timestamp': datetime.now(),
            'estado': resultado.get('estado', 'completada')
        }
        
        self._buffer.append(entrada)
        self._indices[tarea_id] = len(self._buffer) - 1
    
    def obtener_tarea(self, tarea_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un resultado de tarea por ID.
        
        Args:
            tarea_id: Identificador de la tarea
        
        Returns:
            Optional[Dict]: Resultado de la tarea o None
        """
        if tarea_id in self._indices:
            index = self._indices[tarea_id]
            if index < len(self._buffer):
                return self._buffer[index]
        return None
    
    def obtener_ultimas_tareas(self, cantidad: int = 10) -> List[Dict[str, Any]]:
        """
        Obtiene las últimas tareas ejecutadas.
        
        Args:
            cantidad: Número de tareas a recuperar
        
        Returns:
            List: Lista de tareas más recientes
        """
        return list(self._buffer)[-cantidad:]
    
    def limpiar_completadas(self) -> int:
        """
        Limpia las tareas marcadas como completadas.
        
        Returns:
            int: Número de tareas eliminadas
        """
        tareas_a_mantener = []
        indices_actualizados = {}
        eliminadas = 0
        
        for i, tarea in enumerate(self._buffer):
            if tarea['estado'] != 'completada':
                tareas_a_mantener.append(tarea)
                indices_actualizados[tarea['tarea_id']] = len(tareas_a_mantener) - 1
            else:
                eliminadas += 1
        
        self._buffer = deque(tareas_a_mantener, maxlen=self._buffer.maxlen)
        self._indices = indices_actualizados
        
        return eliminadas