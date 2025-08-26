from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class TipoEvento(str, Enum):
    """Tipos de eventos del sistema SAAM"""
    PLAN_GENERADO = "plan.generado"
    TAREA_EJECUTADA = "tarea.ejecutada"
    EPISODIO_REGISTRADO = "episodio.registrado"
    HABILIDAD_ACTUALIZADA = "habilidad.actualizada"
    ERROR_SISTEMA = "error.sistema"
    ALERTA_DESEMPEÑO = "alerta.desempeño"

class NivelSeveridad(str, Enum):
    """Niveles de severidad para eventos"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class EventoSistema(BaseModel):
    """Esquema base para eventos del sistema"""
    tipo: TipoEvento = Field(..., description="Tipo de evento")
    severidad: NivelSeveridad = Field(default=NivelSeveridad.INFO)
    timestamp: datetime = Field(default_factory=datetime.now)
    modulo_origen: str = Field(..., description="Módulo que generó el evento")
    correlation_id: str = Field(..., description="ID para correlacionar eventos")
    datos: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class EventoPlanGenerado(EventoSistema):
    """Evento específico para planificación completada"""
    tipo: TipoEvento = Field(default=TipoEvento.PLAN_GENERADO)
    session_id: str = Field(..., description="ID de sesión del plan")
    objetivo: str = Field(..., description="Objetivo del plan")
    num_tareas: int = Field(..., description="Número de tareas en el plan")

class EventoTareaEjecutada(EventoSistema):
    """Evento específico para tarea ejecutada"""
    tipo: TipoEvento = Field(default=TipoEvento.TAREA_EJECUTADA)
    tarea_id: str = Field(..., description="ID de la tarea ejecutada")
    exito: bool = Field(..., description="Resultado de la ejecución")
    duracion: float = Field(..., description="Duración de la ejecución")
    herramienta_utilizada: str = Field(..., description="Herramienta utilizada")