from typing import Dict, List, Any, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime

class MetadatosEjecucion(BaseModel):
    """Esquema estándar para metadatos de ejecución de tareas"""
    
    # Identificación
    tarea_id: str = Field(..., description="Identificador único de la tarea")
    ejecucion_id: str = Field(..., description="Identificador único de la ejecución")
    session_id: Optional[str] = Field(None, description="ID de sesión asociada")
    
    # Información de la tarea
    tipo_tarea: str = Field(..., description="Tipo de tarea ejecutada")
    herramienta_utilizada: str = Field(..., description="Herramienta utilizada para la ejecución")
    parametros_ejecucion: Dict[str, Any] = Field(default_factory=dict, description="Parámetros de ejecución")
    
    # Tiempos de ejecución
    timestamp_inicio: datetime = Field(..., description="Timestamp de inicio de ejecución")
    timestamp_fin: datetime = Field(..., description="Timestamp de fin de ejecución")
    duracion_segundos: float = Field(..., description="Duración total en segundos")
    
    # Resultado y estado
    exito: bool = Field(..., description="Indicador de éxito de la ejecución")
    estado: Literal["exito", "fallo", "timeout", "cancelado", "parcial"] = Field(..., description="Estado final de la ejecución")
    resultado: Optional[Any] = Field(None, description="Resultado de la ejecución")
    error: Optional[str] = Field(None, description="Mensaje de error si aplica")
    
    # Métricas de rendimiento
    metricas_rendimiento: Dict[str, float] = Field(default_factory=dict, description="Métricas de rendimiento")
    metricas_eficiencia: Dict[str, float] = Field(default_factory=dict, description="Métricas de eficiencia")
    metricas_calidad: Dict[str, float] = Field(default_factory=dict, description="Métricas de calidad")
    
    # Diagnóstico
    diagnostico: Dict[str, Any] = Field(default_factory=dict, description="Diagnóstico de la ejecución")
    accion_recomendada: Optional[str] = Field(None, description="Acción recomendada basada en el resultado")
    
    # Contexto del sistema
    metricas_sistema: Dict[str, Any] = Field(default_factory=dict, description="Métricas del sistema durante la ejecución")
    contexto_ejecucion: Dict[str, Any] = Field(default_factory=dict, description="Contexto de ejecución")
    
    # Metadata técnica
    version_metadatos: str = Field(default="1.0", description="Versión del esquema de metadatos")
    timestamp_registro: datetime = Field(default_factory=datetime.now, description="Timestamp del registro")
    hash_ejecucion: str = Field(..., description="Hash único de la ejecución")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }