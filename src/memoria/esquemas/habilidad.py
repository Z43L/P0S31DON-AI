from typing import Dict, List, Any, Optional, TypedDict
from datetime import datetime
from enum import Enum

class TipoHabilidad(str, Enum):
    """Tipos de habilidades soportadas por el sistema"""
    PROCEDIMIENTO = "procedimiento"
    ESTRATEGIA = "estrategia"
    PLANTILLA = "plantilla"
    RECETA = "receta"
    ADAPTACION = "adaptacion"

class PasoProcedimiento(TypedDict):
    """Estructura de un paso en un procedimiento"""
    orden: int
    accion: str
    parametros: Dict[str, Any]
    herramientas: List[str]
    condiciones: Optional[List[str]]
    descripcion: str

class Habilidad(TypedDict):
    """Estructura completa de una habilidad"""
    # Identificación
    id: Optional[str]
    nombre: str
    tipo: TipoHabilidad
    version: str
    
    # Descripción
    descripcion: str
    objetivos: List[str]
    categorias: List[str]
    
    # Contenido procedural
    procedimiento: List[PasoProcedimiento]
    precondiciones: List[str]
    postcondiciones: List[str]
    
    # Metadatos de rendimiento
    metricas_rendimiento: Dict[str, float]
    estadisticas_uso: Dict[str, int]
    
    # Relaciones
    habilidades_relacionadas: List[str]
    dependencias: List[str]
    
    # Control de versiones
    fecha_creacion: str
    fecha_actualizacion: str
    autor: str  # 'sistema' o 'usuario'
    
    # Configuración de ejecución
    timeout_estimado: int
    recursos_estimados: Dict[str, Any]