from typing import Dict, List, Any, Optional
import uuid
from datetime import datetime
from loguru import logger
import threading
import time

# Importar o definir la clase MemoriaTrabajo
from trabajo import MemoriaTrabajo  # Ajusta el import según la ubicación real

class GestorSesiones:
    """
    Gestor centralizado de sesiones con memoria de trabajo.
    Administra múltiples sesiones simultáneas con aislamiento completo.
    """
    
    def __init__(self, configuracion: Dict[str, Any]):
        self.config = configuracion
        self.sesiones_activas: Dict[str, MemoriaTrabajo] = {}
        self.timeout_sesion = configuracion.get('timeout_sesion', 7200)  # 2 horas por defecto
        self._lock = threading.RLock()
        
        logger.info("Gestor de sesiones inicializado")
    
    def crear_sesion(self, session_id: Optional[str] = None) -> str:
        """
        Crea una nueva sesión con memoria de trabajo.
        
        Args:
            session_id: ID específico para la sesión (opcional)
        
        Returns:
            str: ID de la sesión creada
        """
        with self._lock:
            session_id = session_id or f"session_{uuid.uuid4().hex[:16]}"
            
            if session_id in self.sesiones_activas:
                logger.warning(f"Sesión {session_id} ya existe, reinicializando")
                self.eliminar_sesion(session_id)
            
            self.sesiones_activas[session_id] = MemoriaTrabajo(self.timeout_sesion)
            logger.info(f"Nueva sesión creada: {session_id}")
            
            return session_id
    
    def obtener_sesion(self, session_id: str) -> Optional[MemoriaTrabajo]:
        """
        Obtiene la memoria de trabajo de una sesión específica.
        
        Args:
            session_id: ID de la sesión
        
        Returns:
            Optional[MemoriaTrabajo]: Instancia de memoria de trabajo o None
        """
        with self._lock:
            return self.sesiones_activas.get(session_id)
    
    def eliminar_sesion(self, session_id: str) -> bool:
        """
        Elimina una sesión y libera sus recursos.
        
        Args:
            session_id: ID de la sesión a eliminar
        
        Returns:
            bool: True si la sesión existía y fue eliminada
        """
        with self._lock:
            if session_id in self.sesiones_activas:
                self.sesiones_activas[session_id].limpiar_todo()
                del self.sesiones_activas[session_id]
                logger.info(f"Sesión eliminada: {session_id}")
                return True
            return False
    
    def obtener_estadisticas_globales(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas globales de todas las sesiones.
        
        Returns:
            Dict: Métricas agregadas de todas las sesiones
        """
        with self._lock:
            stats = {
                'total_sesiones': len(self.sesiones_activas),
                'sesiones_activas': [],
                'estadisticas_agregadas': {
                    'total_entradas': 0,
                    'tamano_total_estimado': 0
                }
            }
            
            for session_id, memoria in self.sesiones_activas.items():
                session_stats = memoria.obtener_estadisticas()
                stats['sesiones_activas'].append({
                    'session_id': session_id,
                    'estadisticas': session_stats
                })
                stats['estadisticas_agregadas']['total_entradas'] += session_stats['total_entradas']
                stats['estadisticas_agregadas']['tamano_total_estimado'] += session_stats['tamano_estimado']
            
            return stats
    
    def limpiar_sesiones_expiradas(self) -> int:
        """
        Limpia sesiones que han excedido su tiempo de vida.
        
        Returns:
            int: Número de sesiones eliminadas
        """
        with self._lock:
            sesiones_a_eliminar = []
            ahora = time.time()
            
            for session_id, memoria in self.sesiones_activas.items():
                # Verificar si la sesión ha estado inactiva por más del timeout
                stats = memoria.obtener_estadisticas()
                if ahora - stats['timestamp_ultima_limpieza'] > self.timeout_sesion:
                    sesiones_a_eliminar.append(session_id)
            
            for session_id in sesiones_a_eliminar:
                self.eliminar_sesion(session_id)
            
            logger.info(f"Eliminadas {len(sesiones_a_eliminar)} sesiones expiradas")
            return len(sesiones_a_eliminar)