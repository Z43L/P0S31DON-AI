from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class MensajeGeneracionPlan(BaseModel):
    """Esquema para mensajes de generación de plan"""
    objetivo: str = Field(..., description="Objetivo del usuario en lenguaje natural")
    contexto: Dict[str, Any] = Field(default_factory=dict)
    session_id: str = Field(..., description="ID único de sesión")
    timestamp: datetime = Field(default_factory=datetime.now)
    prioridad: int = Field(default=1, ge=1, le=10)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MensajeRespuestaPlan(BaseModel):
    """Esquema para respuestas de generación de plan"""
    plan: Dict[str, Any] = Field(..., description="Plan estructurado generado")
    session_id: str = Field(..., description="ID de sesión correlacionado")
    timestamp: datetime = Field(default_factory=datetime.now)
    estado: str = Field(..., description="Estado de la generación")
    metadatos: Dict[str, Any] = Field(default_factory=dict)
    errores: List[str] = Field(default_factory=list)

class MensajeEjecucionTarea(BaseModel):
    """Esquema para mensajes de ejecución de tarea"""
    tarea_id: str = Field(..., description="Identificador único de la tarea")
    tipo_tarea: str = Field(..., description="Tipo de tarea a ejecutar")
    parametros: Dict[str, Any] = Field(default_factory=dict)
    contexto: Dict[str, Any] = Field(default_factory=dict)
    prioridad: int = Field(default=1, ge=1, le=10)
    timeout: Optional[int] = Field(default=None, description="Timeout en segundos")

class MensajeResultadoTarea(BaseModel):
    """Esquema para resultados de ejecución de tarea"""
    tarea_id: str = Field(..., description="ID de la tarea ejecutada")
    exito: bool = Field(..., description="Indica si la ejecución fue exitosa")
    resultado: Optional[Dict[str, Any]] = Field(default=None)
    errores: List[str] = Field(default_factory=list)
    metadatos_ejecucion: Dict[str, Any] = Field(default_factory=dict)
    timestamp_inicio: datetime
    timestamp_fin: datetime
    duracion: float = Field(..., description="Duración en segundos")