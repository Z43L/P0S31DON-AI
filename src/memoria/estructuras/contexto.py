from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

class TipoContexto(Enum):
    """Tipos de contexto almacenados en memoria de trabajo"""
    OBJETIVO = "objetivo"
    TAREA = "tarea"
    RESULTADO = "resultado"
    CONVERSACION = "conversacion"
    METADATA = "metadata"

class AlmacenContexto:
    """
    Estructura especializada para almacenamiento de contexto de ejecución
    con tipado fuerte y validación de estructura.
    """
    
    def __init__(self):
        self._contexto: Dict[TipoContexto, Dict[str, Any]] = {
            tipo: {} for tipo in TipoContexto
        }
        self._timestamp_actualizacion: Dict[str, datetime] = {}
    
    def guardar_contexto(self, tipo: TipoContexto, clave: str, valor: Any) -> None:
        """
        Guarda un valor en el contexto con tipo específico.
        
        Args:
            tipo: Tipo de contexto
            clave: Identificador único
            valor: Valor a almacenar
        """
        self._contexto[tipo][clave] = valor
        self._timestamp_actualizacion[f"{tipo.value}_{clave}"] = datetime.now()
    
    def obtener_contexto(self, tipo: TipoContexto, clave: str, default: Any = None) -> Any:
        """
        Obtiene un valor del contexto.
        
        Args:
            tipo: Tipo de contexto
            clave: Identificador del valor
            default: Valor por defecto si no existe
        
        Returns:
            Any: Valor almacenado o valor por defecto
        """
        return self._contexto[tipo].get(clave, default)
    
    def obtener_todo_tipo(self, tipo: TipoContexto) -> Dict[str, Any]:
        """
        Obtiene todos los valores de un tipo de contexto.
        
        Args:
            tipo: Tipo de contexto
        
        Returns:
            Dict: Todos los valores del tipo especificado
        """
        return self._contexto[tipo].copy()
    
    def eliminar_contexto(self, tipo: TipoContexto, clave: str) -> bool:
        """
        Elimina un valor del contexto.
        
        Args:
            tipo: Tipo de contexto
            clave: Identificador del valor
        
        Returns:
            bool: True si el valor existía y fue eliminado
        """
        if clave in self._contexto[tipo]:
            del self._contexto[tipo][clave]
            timestamp_key = f"{tipo.value}_{clave}"
            if timestamp_key in self._timestamp_actualizacion:
                del self._timestamp_actualizacion[timestamp_key]
            return True
        return False
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del almacén de contexto.
        
        Returns:
            Dict: Métricas de utilización
        """
        return {
            'total_por_tipo': {tipo.value: len(valores) for tipo, valores in self._contexto.items()},
            'total_general': sum(len(valores) for valores in self._contexto.values()),
            'timestamp_ultima_actualizacion': max(self._timestamp_actualizacion.values()) 
                                            if self._timestamp_actualizacion else None
        }