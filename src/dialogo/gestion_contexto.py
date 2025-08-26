from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
from loguru import logger

class GestorContexto:
    """Gestor del contexto de diálogo y estado conversacional"""
    
    def __init__(self, sistema_memoria, configuracion: Dict[str, Any]):
        self.memoria = sistema_memoria
        self.config = configuracion
        self.contextos_activos: Dict[str, Dict] = {}
    
    def obtener_contexto(self, session_id: str) -> Dict[str, Any]:
        """Obtiene el contexto de diálogo para una sesión específica"""
        if session_id in self.contextos_activos:
            return self.contextos_activos[session_id]
        
        # Intentar cargar desde memoria persistente
        contexto = self.memoria.obtener_contexto(f"dialogo_contexto_{session_id}")
        if contexto:
            self.contextos_activos[session_id] = contexto
            return contexto
        
        # Crear nuevo contexto
        nuevo_contexto = {
            'session_id': session_id,
            'historial_mensajes': [],
            'estado_actual': 'inicio',
            'objetivo_actual': None,
            'timestamp_creacion': datetime.now(),
            'timestamp_ultimo_acceso': datetime.now()
        }
        
        self.contextos_activos[session_id] = nuevo_contexto
        return nuevo_contexto
    
    def actualizar_contexto(self, session_id: str, actualizaciones: Dict[str, Any]) -> None:
        """Actualiza el contexto de diálogo con nueva información"""
        contexto = self.obtener_contexto(session_id)
        contexto.update(actualizaciones)
        contexto['timestamp_ultimo_acceso'] = datetime.now()
        
        # Persistir en memoria
        self.memoria.guardar_contexto(
            f"dialogo_contexto_{session_id}", 
            contexto,
            expiration=86400  # 24 horas
        )
    
    def agregar_mensaje(self, session_id: str, mensaje: Dict[str, Any]) -> None:
        """Agrega un mensaje al historial de la conversación"""
        contexto = self.obtener_contexto(session_id)
        
        mensaje_con_metadata = {
            **mensaje,
            'timestamp': datetime.now(),
            'id': f"msg_{len(contexto['historial_mensajes']) + 1:04d}"
        }
        
        contexto['historial_mensajes'].append(mensaje_con_metadata)
        
        # Limitar el tamaño del historial para evitar crecimiento excesivo
        if len(contexto['historial_mensajes']) > self.config.get('max_historial_mensajes', 50):
            contexto['historial_mensajes'] = contexto['historial_mensajes'][-25:]
        
        self.actualizar_contexto(session_id, contexto)
    
    def obtener_resumen_conversacion(self, session_id: str) -> str:
        """Genera un resumen de la conversación para contexto de LLM"""
        contexto = self.obtener_contexto(session_id)
        historial = contexto['historial_mensajes'][-10:]  # Últimos 10 mensajes
        
        resumen = "Resumen de la conversación:\n"
        for mensaje in historial:
            rol = mensaje.get('rol', 'usuario')
            contenido = mensaje.get('contenido', '')
            resumen += f"{rol.upper()}: {contenido}\n"
        
        return resumen