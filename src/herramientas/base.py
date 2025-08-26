from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime
import inspect
from loguru import logger

class HerramientaBase(ABC):
    """Clase base abstracta para todas las herramientas del sistema"""
    
    # Marcar que esta clase es una herramienta
    es_herramienta = True
    
    def __init__(self, configuracion: Dict[str, Any]):
        self.config = configuracion
        self.nombre = self.__class__.__name__
        self.version = "1.0.0"
        self.estado = "inactivo"
        self.metricas = {
            'ejecuciones_totales': 0,
            'ejecuciones_exitosas': 0,
            'ejecuciones_fallidas': 0,
            'tiempo_total_ejecucion': 0.0,
            'ultima_ejecucion': None
        }
        self.metadata = self._generar_metadata()
        self._inicializar()
    
    def _inicializar(self):
        """Inicialización de la herramienta"""
        self.estado = "activo"
        logger.info(f"Herramienta {self.nombre} inicializada")
    
    @abstractmethod
    async def ejecutar(self, **parametros) -> Any:
        """
        Método abstracto para ejecución de la herramienta.
        Debe ser implementado por cada herramienta concreta.
        """
        pass
    
    async def ejecutar_segura(self, **parametros) -> Dict[str, Any]:
        """
        Ejecución segura con manejo de errores y registro de métricas.
        
        Returns:
            Dict: Resultado con metadata de ejecución
        """
        inicio = datetime.now()
        
        try:
            resultado = await self.ejecutar(**parametros)
            duracion = (datetime.now() - inicio).total_seconds()
            
            # Actualizar métricas
            self._actualizar_metricas(True, duracion)
            
            return {
                'exito': True,
                'resultado': resultado,
                'duracion': duracion,
                'error': None,
                'herramienta': self.nombre
            }
            
        except Exception as e:
            duracion = (datetime.now() - inicio).total_seconds()
            self._actualizar_metricas(False, duracion)
            
            logger.error(f"Error en {self.nombre}: {str(e)}")
            
            return {
                'exito': False,
                'resultado': None,
                'duracion': duracion,
                'error': str(e),
                'herramienta': self.nombre
            }
    
    def _actualizar_metricas(self, exito: bool, duracion: float):
        """Actualiza las métricas de la herramienta"""
        self.metricas['ejecuciones_totales'] += 1
        
        if exito:
            self.metricas['ejecuciones_exitosas'] += 1
        else:
            self.metricas['ejecuciones_fallidas'] += 1
        
        self.metricas['tiempo_total_ejecucion'] += duracion
        self.metricas['ultima_ejecucion'] = datetime.now().isoformat()
    
    def _generar_metadata(self) -> Dict[str, Any]:
        """Genera metadata automáticamente desde la clase"""
        signature = inspect.signature(self.ejecutar)
        parametros = []
        
        for name, param in signature.parameters.items():
            if name != 'self':
                parametros.append({
                    'nombre': name,
                    'tipo': str(param.annotation) if param.annotation != param.empty else 'Any',
                    'default': param.default if param.default != param.empty else None,
                    'requerido': param.default == param.empty
                })
        
        return {
            'nombre': self.nombre,
            'version': self.version,
            'descripcion': self.__doc__ or "Sin descripción",
            'parametros': parametros,
            'categorias': ['general'],
            'estado': self.estado,
            'metricas': self.metricas
        }
    
    def obtener_info(self) -> Dict[str, Any]:
        """Retorna información completa de la herramienta"""
        return self.metadata