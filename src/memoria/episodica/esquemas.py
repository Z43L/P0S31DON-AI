from typing import Dict, List, Any, Optional, TypedDict
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator

class EstadoEjecucion(str, Enum):
    """Estados posibles de una ejecución registrada en memoria episódica"""
    EXITO = "exito"
    FALLO = "fallo"
    PARCIAL = "parcial"
    TIMEOUT = "timeout"
    CANCELADO = "cancelado"

class ResultadoTarea(TypedDict):
    """Estructura de resultado de una tarea individual"""
    tarea_id: str
    exito: bool
    resultado: Optional[Any]
    error: Optional[str]
    duracion_segundos: float
    herramienta_utilizada: str
    timestamp_inicio: datetime
    timestamp_fin: datetime

class Episodio(BaseModel):
    """
    Esquema inmutable para registro de experiencias completas del sistema.
    Cada episodio representa una ejecución completa de un objetivo.
    """
    # Identificación única
    id: str = Field(..., description="Identificador único universal del episodio")
    objetivo: str = Field(..., description="Objetivo original que inició la ejecución")
    session_id: str = Field(..., description="ID de sesión asociada")
    
    # Información de planificación
    plan_ejecutado: Dict[str, Any] = Field(..., description="Plan completo que se ejecutó")
    timestamp_planificacion: datetime = Field(..., description="Momento de la planificación")
    
    # Resultados de ejecución
    resultados_tareas: List[ResultadoTarea] = Field(..., description="Resultados de todas las tareas ejecutadas")
    estado_global: EstadoEjecucion = Field(..., description="Estado global de la ejecución")
    duracion_total_segundos: float = Field(..., description="Duración total de la ejecución")
    
    # Contexto y metadata
    contexto_ejecucion: Dict[str, Any] = Field(default_factory=dict, description="Contexto durante la ejecución")
    metricas_rendimiento: Dict[str, float] = Field(default_factory=dict, description="Métricas de rendimiento")
    recursos_utilizados: Dict[str, Any] = Field(default_factory=dict, description="Recursos consumidos")
    
    # Auditoría y control
    timestamp_inicio: datetime = Field(..., description="Inicio de la ejecución")
    timestamp_fin: datetime = Field(..., description="Fin de la ejecución")
    version_sistema: str = Field(..., description="Versión de SAAM durante la ejecución")
    checksum_integridad: str = Field(..., description="Hash de verificación de integridad")
    
    # Retroalimentación y evaluación
    feedback_usuario: Optional[Dict[str, Any]] = Field(None, description="Retroalimentación del usuario")
    evaluacion_automatica: Dict[str, float] = Field(default_factory=dict, description="Evaluación automática de calidad")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @validator('id')
    def validar_id_unico(cls, v):
        """Valida que el ID siga el formato correcto"""
        if not v.startswith('episodio_'):
            raise ValueError('ID debe comenzar con "episodio_"')
        return v
    
    @validator('checksum_integridad')
    def calcular_checksum(cls, v, values):
        """Calcula el checksum de integridad del episodio"""
        import hashlib
        contenido = f"{values['objetivo']}{values['timestamp_inicio']}{values['timestamp_fin']}"
        return hashlib.sha256(contenido.encode()).hexdigest()