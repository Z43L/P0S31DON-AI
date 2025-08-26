from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from datetime import datetime
import re
from loguru import logger

class EstadoDialogo(Enum):
    """Estados posibles en el flujo de diálogo con el usuario"""
    INICIO = "inicio"
    RECEPCION_OBJETIVO = "recepcion_objetivo"
    CLARIFICACION = "clarificacion"
    CONFIRMACION = "confirmacion"
    EJECUCION = "ejecucion"
    FINALIZACION = "finalizacion"

class GestorDialogo:
    """Gestor principal del sistema de diálogo de SAAM"""
    
    def __init__(self, cliente_llm, sistema_memoria, configuracion: Dict[str, Any]):
        self.llm = cliente_llm
        self.memoria = sistema_memoria
        self.config = configuracion
        self.estado_actual = EstadoDialogo.INICIO
        self.contexto_dialogo: Dict[str, Any] = {}
        
        # Plantillas para prompts de diálogo
        self.prompt_templates = self._cargar_templates()
        
        logger.info("Gestor de Diálogo inicializado correctamente")
    
    async def iniciar_dialogo(self, mensaje_usuario: str, session_id: str) -> Dict[str, Any]:
        """
        Inicia o continúa un diálogo con el usuario basado en el mensaje recibido.
        
        Args:
            mensaje_usuario: Mensaje de entrada del usuario
            session_id: Identificador único de la sesión de diálogo
        
        Returns:
            Dict: Respuesta estructurada del sistema
        """
        try:
            # Cargar contexto previo de la sesión
            self._cargar_contexto_sesion(session_id)
            
            # Procesar el mensaje del usuario según el estado actual
            if self.estado_actual == EstadoDialogo.INICIO:
                respuesta = await self._procesar_mensaje_inicial(mensaje_usuario)
            elif self.estado_actual == EstadoDialogo.CLARIFICACION:
                respuesta = await self._procesar_respuesta_clarificacion(mensaje_usuario)
            else:
                respuesta = await self._procesar_mensaje_general(mensaje_usuario)
            
            # Guardar contexto actualizado
            self._guardar_contexto_sesion(session_id)
            
            return respuesta
            
        except Exception as e:
            logger.error(f"Error en diálogo: {e}")
            return self._generar_respuesta_error()
    
    async def _procesar_mensaje_inicial(self, mensaje: str) -> Dict[str, Any]:
        """Procesa el mensaje inicial del usuario para identificar el objetivo principal"""
        # Análisis del mensaje para extraer intención y entidades clave
        analisis = await self._analizar_intencion(mensaje)
        
        if analisis['necesita_clarificacion']:
            self.estado_actual = EstadoDialogo.CLARIFICACION
            return self._generar_pregunta_clarificacion(analisis['puntos_ambiguos'])
        
        # Si el objetivo está claro, proceder con la planificación
        self.estado_actual = EstadoDialogo.CONFIRMACION
        objetivo_estructurado = self._estructurar_objetivo(analisis)
        
        return {
            'tipo': 'confirmacion',
            'mensaje': f"Entendido. ¿Desea que proceda con: {objetivo_estructurado['descripcion']}?",
            'objetivo': objetivo_estructurado,
            'opciones': ['Sí', 'No', 'Modificar']
        }