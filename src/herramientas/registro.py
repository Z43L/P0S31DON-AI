from typing import Dict, List, Any, Optional, Type
from collections import defaultdict
from loguru import logger

class RegistroHerramientas:
    """Sistema centralizado de registro y gestión de herramientas"""
    
    def __init__(self, configuracion: Dict[str, Any]):
        self.config = configuracion
        self.herramientas_registradas: Dict[str, Any] = {}
        self.categorias_herramientas: Dict[str, List[str]] = defaultdict(list)
        self._cargar_herramientas_integradas()
    
    def registrar_herramienta(self, herramienta_instance: Any, categorias: List[str] = None) -> bool:
        """
        Registra una nueva herramienta en el sistema.
        
        Args:
            herramienta_instance: Instancia de la herramienta a registrar
            categorias: Lista de categorías para clasificación
        
        Returns:
            bool: True si el registro fue exitoso
        """
        try:
            nombre = herramienta_instance.nombre
            
            if nombre in self.herramientas_registradas:
                logger.warning(f"Herramienta {nombre} ya registrada, actualizando")
            
            self.herramientas_registradas[nombre] = herramienta_instance
            
            # Registrar en categorías
            if categorias:
                for categoria in categorias:
                    self.categorias_herramientas[categoria].append(nombre)
            
            logger.info(f"Herramienta {nombre} registrada exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error registrando herramienta: {e}")
            return False
    
    def obtener_herramienta(self, nombre: str) -> Optional[Any]:
        """
        Obtiene una herramienta por nombre.
        
        Args:
            nombre: Nombre de la herramienta
        
        Returns:
            Optional[Any]: Instancia de la herramienta o None
        """
        return self.herramientas_registradas.get(nombre)
    
    def obtener_herramientas_por_categoria(self, categoria: str) -> List[Any]:
        """
        Obtiene todas las herramientas de una categoría específica.
        
        Args:
            categoria: Categoría de herramientas
        
        Returns:
            List[Any]: Lista de herramientas de la categoría
        """
        nombres = self.categorias_herramientas.get(categoria, [])
        return [self.herramientas_registradas[nombre] for nombre in nombres 
                if nombre in self.herramientas_registradas]
    
    def obtener_herramientas_por_tipo_tarea(self, tipo_tarea: str) -> List[Dict]:
        """
        Obtiene herramientas recomendadas para un tipo de tarea específico.
        
        Args:
            tipo_tarea: Tipo de tarea a ejecutar
        
        Returns:
            List[Dict]: Lista de herramientas con información de idoneidad
        """
        # Mapeo de tipos de tarea a categorías de herramientas
        mapeo_tareas = {
            'busqueda': ['busqueda_web', 'api_rest'],
            'generacion': ['llm', 'generacion_texto'],
            'procesamiento': ['procesamiento_datos', 'analisis'],
            'comunicacion': ['email', 'api_rest']
        }
        
        categorias_recomendadas = mapeo_tareas.get(tipo_tarea, [])
        herramientas = []
        
        for categoria in categorias_recomendadas:
            herramientas.extend(self.obtener_herramientas_por_categoria(categoria))
        
        # Ordenar por métricas de rendimiento
        herramientas_ordenadas = sorted(
            herramientas,
            key=lambda x: x.metricas.get('tasa_exito', 0),
            reverse=True
        )
        
        return [
            {
                'herramienta': h.nombre,
                'categoria': next((cat for cat, tools in self.categorias_herramientas.items() 
                                  if h.nombre in tools), 'general'),
                'metricas': h.metricas,
                'idoneidad': self._calcular_idoneidad(h, tipo_tarea)
            }
            for h in herramientas_ordenadas
        ]
    
    def _calcular_idoneidad(self, herramienta: Any, tipo_tarea: str) -> float:
        """Calcula la idoneidad de una herramienta para un tipo de tarea"""
        # Base de idoneidad por categoría
        idoneidad_base = 0.5
        
        # Ajustar por rendimiento histórico
        tasa_exito = herramienta.metricas.get('tasa_exito', 0.5)
        idoneidad_base += (tasa_exito - 0.5) * 0.3
        
        # Ajustar por experiencia reciente
        if herramienta.metricas.get('ejecuciones_exitosas', 0) > 10:
            idoneidad_base += 0.1
        
        return max(0.1, min(1.0, idoneidad_base))
    
    def _cargar_herramientas_integradas(self):
        """Carga automáticamente las herramientas integradas en el sistema"""
        try:
            from . import busqueda_web, generacion_texto, api_clients
            
            herramientas_integradas = [
                (busqueda_web.BusquedaWebTool(self.config), ['busqueda_web', 'api_rest']),
                (generacion_texto.GeneracionTextoTool(self.config), ['generacion', 'llm']),
                (api_clients.APIRestTool(self.config), ['api_rest', 'comunicacion'])
            ]
            
            for herramienta, categorias in herramientas_integradas:
                self.registrar_herramienta(herramienta, categorias)
                
        except ImportError as e:
            logger.warning(f"No se pudieron cargar algunas herramientas integradas: {e}")