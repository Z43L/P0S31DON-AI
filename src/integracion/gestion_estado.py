from typing import Dict, Any, Optional
from contextlib import asynccontextmanager
from loguru import logger

class GestorEstadoCompartido:
    """
    Gestiona el estado compartido entre módulos con mecanismos de consistencia.
    """
    
    def __init__(self, sistema_memoria, configuracion: Dict[str, Any]):
        self.sm3 = sistema_memoria
        self.config = configuracion
        self.locks = {}
        
    @asynccontextmanager
    async def contexto_consistencia(self, recurso: str, timeout: int = 30):
        """
        Context manager para acceso consistente a recursos compartidos.
        
        Args:
            recurso: Identificador del recurso compartido
            timeout: Timeout para adquisición del lock
        """
        lock = self._obtener_lock(recurso)
        
        try:
            adquirido = await lock.acquire(timeout=timeout)
            if not adquirido:
                raise TimeoutError(f"Timeout adquiriendo lock para {recurso}")
            
            yield
            
        finally:
            if lock.locked():
                lock.release()
    
    async def actualizar_estado_compartido(self, recurso: str, actualizaciones: Dict[str, Any], 
                                         contexto: Optional[str] = None) -> bool:
        """
        Actualiza estado compartido con consistencia garantizada.
        
        Args:
            recurso: Recurso a actualizar
            actualizaciones: Diccionario con actualizaciones
            contexto: Contexto de la actualización para logging
        
        Returns:
            bool: True si la actualización fue exitosa
        """
        async with self.contexto_consistencia(recurso):
            try:
                # Obtener estado actual
                estado_actual = await self.sm3.obtener_estado(recurso)
                
                # Aplicar actualizaciones
                estado_actualizado = {**estado_actual, **actualizaciones}
                
                # Guardar estado actualizado
                exito = await self.sm3.guardar_estado(recurso, estado_actualizado)
                
                if exito and contexto:
                    logger.info(f"Estado {recurso} actualizado desde contexto: {contexto}")
                
                return exito
                
            except Exception as e:
                logger.error(f"Error actualizando estado compartido {recurso}: {e}")
                return False