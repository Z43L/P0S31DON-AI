from typing import Dict, List, Any, Optional, Callable
import importlib
from loguru import logger

class GestorHerramientas:
    """Gestor centralizado para registro, descubrimiento y administración de herramientas"""
    
    def __init__(self, config_herramientas: Dict[str, Any]):
        self.config = config_herramientas
        self.herramientas_registradas: Dict[str, Dict] = {}
        self._cargar_herramientas_integradas()
        
    def _cargar_herramientas_integradas(self) -> None:
        """Carga automática de herramientas integradas en el sistema"""
        herramientas_integradas = {
            'busqueda_web': 'src.herramientas.busqueda_web',
            'generacion_texto': 'src.herramientas.generacion_texto',
            'llamada_api': 'src.herramientas.api_clients',
            'procesamiento_datos': 'src.herramientas.procesamiento_datos'
        }
        
        for nombre, modulo_path in herramientas_integradas.items():
            try:
                modulo = importlib.import_module(modulo_path)
                herramienta = getattr(modulo, f'ejecutar_{nombre}', None)
                
                if herramienta and callable(herramienta):
                    self.registrar_herramienta(nombre, herramienta)
                    logger.info(f"Herramienta integrada '{nombre}' cargada exitosamente")
                    
            except ImportError as e:
                logger.warning(f"No se pudo cargar herramienta {nombre}: {e}")
    
    def registrar_herramienta(self, nombre: str, funcion: Callable, metadata: Dict = None) -> bool:
        """Registra una nueva herramienta en el sistema con metadatos descriptivos"""
        if nombre in self.herramientas_registradas:
            logger.warning(f"Herramienta '{nombre}' ya registrada, sobrescribiendo")
        
        self.herramientas_registradas[nombre] = {
            'funcion': funcion,
            'metadata': metadata or {},
            'estadisticas': {
                'veces_utilizada': 0,
                'exitos': 0,
                'fallos': 0,
                'tiempo_total': 0.0
            }
        }
        
        logger.info(f"Herramienta '{nombre}' registrada exitosamente")
        return True
    
    def obtener_herramienta(self, nombre: str) -> Optional[Callable]:
        """Obtiene una herramienta por nombre y actualiza sus estadísticas de uso"""
        if nombre in self.herramientas_registradas:
            self.herramientas_registradas[nombre]['estadisticas']['veces_utilizada'] += 1
            return self.herramientas_registradas[nombre]['funcion']
        return None
    
    def obtener_herramientas_por_tipo(self, tipo_tarea: str) -> List[Dict]:
        """Obtiene herramientas adecuadas para un tipo de tarea específico, ordenadas por efectividad"""
        herramientas_adecuadas = []
        
        for nombre, datos in self.herramientas_registradas.items():
            if datos['metadata'].get('tipos_tarea', []).count(tipo_tarea) > 0:
                herramientas_adecuadas.append({
                    'nombre': nombre,
                    'estadisticas': datos['estadisticas'],
                    'metadata': datos['metadata']
                })
        
        return sorted(herramientas_adecuadas, key=lambda x: x['estadisticas']['exitos'], reverse=True)
    
    def actualizar_estadisticas(self, nombre: str, exito: bool, duracion: float) -> None:
        """Actualiza las estadísticas de uso de una herramienta basado en resultados de ejecución"""
        if nombre in self.herramientas_registradas:
            stats = self.herramientas_registradas[nombre]['estadisticas']
            if exito:
                stats['exitos'] += 1
            else:
                stats['fallos'] += 1
            stats['tiempo_total'] += duracion
    
    def obtener_estadisticas_globales(self) -> Dict[str, Any]:
        """Obtiene estadísticas agregadas de todas las herramientas registradas"""
        return {
            'total_herramientas': len(self.herramientas_registradas),
            'herramientas_mas_usadas': sorted(
                self.herramientas_registradas.items(),
                key=lambda x: x[1]['estadisticas']['veces_utilizada'],
                reverse=True
            )[:5]
        }