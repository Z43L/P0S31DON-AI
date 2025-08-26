from typing import Dict, List, Any, Optional
import time
from datetime import datetime, timedelta
import threading
from loguru import logger

class MemoriaTrabajo:
    """
    Sistema de memoria de trabajo volátil para gestión de estado de sesión.
    Almacena información temporal necesaria para la ejecución del objetivo actual.
    """
    
    def __init__(self, timeout: int = 3600):
        """
        Inicializa una nueva instancia de memoria de trabajo.
        
        Args:
            timeout: Tiempo de vida máximo en segundos para entradas (por defecto 1 hora)
        """
        self._almacen: Dict[str, Any] = {}
        self._timestamp_acceso: Dict[str, float] = {}
        self._timestamp_creacion: Dict[str, float] = {}
        self.timeout = timeout
        self._lock = threading.RLock()
        self._iniciar_limpieza_automatica()
        
        logger.info(f"Memoria de trabajo inicializada con timeout {timeout} segundos")
    
    def _iniciar_limpieza_automatica(self):
        """Inicia el hilo de limpieza automática de entradas expiradas"""
        def limpiador():
            while True:
                time.sleep(300)  # Ejecutar limpieza cada 5 minutos
                self._limpiar_expirados()
        
        thread = threading.Thread(target=limpiador, daemon=True)
        thread.start()
        logger.debug("Hilo de limpieza automática iniciado")
    
    def _limpiar_expirados(self):
        """Elimina entradas que han excedido su tiempo de vida"""
        with self._lock:
            ahora = time.time()
            claves_a_eliminar = [
                clave for clave, timestamp in self._timestamp_acceso.items()
                if ahora - timestamp > self.timeout
            ]
            
            for clave in claves_a_eliminar:
                del self._almacen[clave]
                del self._timestamp_acceso[clave]
                del self._timestamp_creacion[clave]
            
            if claves_a_eliminar:
                logger.debug(f"Limpiadas {len(claves_a_eliminar)} entradas expiradas")
    
    def guardar(self, clave: str, valor: Any, expiration: Optional[int] = None) -> None:
        """
        Guarda un valor en la memoria de trabajo.
        
        Args:
            clave: Identificador único para el valor
            valor: Dato a almacenar
            expiration: Tiempo de expiración específico en segundos (opcional)
        """
        with self._lock:
            timestamp_actual = time.time()
            self._almacen[clave] = valor
            self._timestamp_acceso[clave] = timestamp_actual
            self._timestamp_creacion[clave] = timestamp_actual
            
            if expiration:
                # Programar expiración específica para esta clave
                threading.Timer(expiration, lambda: self.eliminar(clave)).start()
            
            logger.debug(f"Guardado en memoria de trabajo: {clave}")
    
    def obtener(self, clave: str, default: Any = None) -> Any:
        """
        Obtiene un valor de la memoria de trabajo.
        
        Args:
            clave: Identificador del valor a recuperar
            default: Valor por defecto si la clave no existe
        
        Returns:
            Any: Valor almacenado o valor por defecto
        """
        with self._lock:
            if clave in self._almacen:
                # Actualizar timestamp de acceso
                self._timestamp_acceso[clave] = time.time()
                logger.debug(f"Acceso a memoria de trabajo: {clave}")
                return self._almacen[clave]
            return default
    
    def eliminar(self, clave: str) -> bool:
        """
        Elimina una clave de la memoria de trabajo.
        
        Args:
            clave: Identificador de la entrada a eliminar
        
        Returns:
            bool: True si la clave existía y fue eliminada
        """
        with self._lock:
            if clave in self._almacen:
                del self._almacen[clave]
                del self._timestamp_acceso[clave]
                del self._timestamp_creacion[clave]
                logger.debug(f"Eliminado de memoria de trabajo: {clave}")
                return True
            return False
    
    def obtener_todo_contexto(self) -> Dict[str, Any]:
        """
        Obtiene todo el contenido actual de la memoria de trabajo.
        
        Returns:
            Dict: Copia del estado actual de la memoria
        """
        with self._lock:
            return self._almacen.copy()
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de uso de la memoria de trabajo.
        
        Returns:
            Dict: Métricas de utilización de la memoria
        """
        with self._lock:
            ahora = time.time()
            return {
                'total_entradas': len(self._almacen),
                'entradas_activas': sum(1 for ts in self._timestamp_acceso.values() 
                                      if ahora - ts <= self.timeout),
                'tamano_estimado': sum(len(str(v)) for v in self._almacen.values()),
                'timestamp_ultima_limpieza': ahora
            }
    
    def limpiar_todo(self) -> None:
        """
        Limpia completamente la memoria de trabajo.
        """
        with self._lock:
            self._almacen.clear()
            self._timestamp_acceso.clear()
            self._timestamp_creacion.clear()
            logger.info("Memoria de trabajo limpiada completamente")