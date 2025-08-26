from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from memoria.trabajo import MemoriaTrabajo
from memoria.conocimiento import BaseConocimiento
from memoria.episodica import MemoriaEpisodica
from loguru import logger

class SistemaMemoriaTripleCapa:
    """Sistema unificado que gestiona las tres capas de memoria de SAAM"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Inicializar las tres capas de memoria
        self.memoria_trabajo = MemoriaTrabajo(
            timeout=config.get('memoria', {}).get('trabajo', {}).get('timeout', 3600)
        )
        
        self.base_conocimiento = BaseConocimiento(
            ruta_bd=config.get('memoria', {}).get('conocimiento', {}).get('ruta', './data/conocimiento')
        )
        
        self.memoria_episodica = MemoriaEpisodica(
            cadena_conexion=config.get('memoria', {}).get('episodica', {}).get('ruta', 'sqlite:///./data/episodica.db')
        )
        
        logger.info("Sistema de Memoria Triple Capa inicializado")
    
    # --- Métodos de Memoria de Trabajo ---
    def guardar_contexto(self, clave: str, valor: Any, expiration: Optional[int] = None) -> None:
        """Guarda información en la memoria de trabajo"""
        self.memoria_trabajo.guardar(clave, valor, expiration)
    
    def obtener_contexto(self, clave: str, default: Any = None) -> Any:
        """Obtiene información de la memoria de trabajo"""
        return self.memoria_trabajo.obtener(clave, default)
    
    def obtener_todo_contexto(self) -> Dict[str, Any]:
        """Obtiene todo el contexto actual"""
        return self.memoria_trabajo.obtener_todo_contexto()
    
    def limpiar_contexto(self) -> None:
        """Limpia la memoria de trabajo"""
        self.memoria_trabajo.limpiar_todo()
    
    # --- Métodos de Base de Conocimiento ---
    def guardar_habilidad(self, habilidad: Dict[str, Any]) -> str:
        """Guarda una nueva habilidad en la base de conocimiento"""
        return self.base_conocimiento.guardar_habilidad(habilidad)
    
    def buscar_habilidades(self, consulta: str, filtros: Optional[Dict] = None, 
                          limite: int = 5) -> List[Dict[str, Any]]:
        """Busca habilidades relevantes en la base de conocimiento"""
        return self.base_conocimiento.buscar_habilidades(consulta, filtros, limite)
    
    def actualizar_estadisticas_habilidad(self, habilidad_id: str, exito: bool) -> None:
        """Actualiza las estadísticas de uso de una habilidad"""
        self.base_conocimiento.actualizar_estadisticas_habilidad(habilidad_id, exito)
    
    # --- Métodos de Memoria Episódica ---
    def guardar_episodio(self, episodio: Dict[str, Any]) -> str:
        """Guarda un episodio completo en la memoria episódica"""
        return self.memoria_episodica.guardar_episodio(episodio)
    
    def obtener_episodios(self, filtros: Optional[Dict] = None, 
                         limite: int = 100) -> List[Dict[str, Any]]:
        """Obtiene episodios con filtros opcionales"""
        return self.memoria_episodica.obtener_episodios(filtros, limite)
    
    def obtener_episodios_por_tipo_tarea(self, tipo_tarea: str, 
                                       limite: int = 50) -> List[Dict[str, Any]]:
        """Obtiene episodios relacionados con un tipo específico de tarea"""
        return self.memoria_episodica.obtener_episodios_por_tipo_tarea(tipo_tarea, limite)
    
    # --- Métodos de Utilidad ---
    def obtener_estadisticas_globales(self) -> Dict[str, Any]:
        """Obtiene estadísticas globales del sistema de memoria"""
        try:
            # Estadísticas de memoria episódica
            episodios = self.obtener_episodios(limite=1000)
            total_episodios = len(episodios)
            exitosos = sum(1 for e in episodios if e.get('estado') == 'exito')
            tasa_exito = (exitosos / total_episodios * 100) if total_episodios > 0 else 0
            
            return {
                'total_episodios': total_episodios,
                'episodios_exitosos': exitosos,
                'tasa_exito_global': f"{tasa_exito:.1f}%",
                'tamano_memoria_trabajo': len(self.memoria_trabajo.obtener_todo_contexto())
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas globales: {e}")
            return {}