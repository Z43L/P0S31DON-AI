from typing import Dict, Any, Optional, Callable
import asyncio
from enum import Enum
from loguru import logger

class ModoComunicacion(Enum):
    SINCRONO = "sincrono"
    ASINCRONO = "asincrono"
    HIBRIDO = "hibrido"

class PatronComunicacion:
    """
    Gestor de patrones de comunicación entre módulos del sistema SAAM.
    """
    
    def __init__(self, configuracion: Dict[str, Any]):
        self.config = configuracion
        self.modo = ModoComunicacion(configuracion.get('modo_comunicacion', 'hibrido'))
        
    async def comunicar_modulos(self, modulo_origen: str, modulo_destino: str, 
                              mensaje: Dict, callback: Optional[Callable] = None) -> Any:
        """
        Gestiona la comunicación entre módulos según el modo configurado.
        
        Args:
            modulo_origen: Módulo originador de la comunicación
            modulo_destino: Módulo destino de la comunicación
            mensaje: Contenido del mensaje
            callback: Función callback para procesar respuesta (modo asíncrono)
        
        Returns:
            Any: Respuesta del módulo destino o None en modo asíncrono
        """
        if self.modo == ModoComunicacion.SINCRONO:
            return await self._comunicacion_sincrona(modulo_destino, mensaje)
        elif self.modo == ModoComunicacion.ASINCRONO:
            return await self._comunicacion_asincrona(modulo_destino, mensaje, callback)
        else:  # HIBRIDO
            return await self._comunicacion_hibrida(modulo_destino, mensaje, callback)
    
    async def _comunicacion_sincrona(self, modulo_destino: str, mensaje: Dict) -> Any:
        """Comunicación síncrona entre módulos"""
        try:
            # Simular comunicación directa entre módulos
            if modulo_destino == 'mcp':
                return await self._llamar_mcp(mensaje)
            elif modulo_destino == 'met':
                return await self._llamar_met(mensaje)
            elif modulo_destino == 'sm3':
                return await self._llamar_sm3(mensaje)
            elif modulo_destino == 'mao':
                return await self._llamar_mao(mensaje)
                
        except Exception as e:
            logger.error(f"Error en comunicación síncrona con {modulo_destino}: {e}")
            raise
    
    async def _comunicacion_asincrona(self, modulo_destino: str, mensaje: Dict, 
                                    callback: Callable) -> None:
        """Comunicación asíncrona entre módulos"""
        asyncio.create_task(self._procesar_asincrono(modulo_destino, mensaje, callback))
    
    async def _comunicacion_hibrida(self, modulo_destino: str, mensaje: Dict,
                                  callback: Optional[Callable]) -> Any:
        """
        Comunicación híbrida: síncrona para respuestas inmediatas necesarias,
        asíncrona para operaciones de background.
        """
        # Determinar el modo basado en el tipo de mensaje
        if mensaje.get('tipo') in ['consulta', 'planificacion', 'ejecucion_inmediata']:
            return await self._comunicacion_sincrona(modulo_destino, mensaje)
        else:
            if callback:
                await self._comunicacion_asincrona(modulo_destino, mensaje, callback)
            return {'estado': 'procesamiento_asincrono_iniciado'}