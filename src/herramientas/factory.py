from typing import Dict, List, Any, Optional, Type
from loguru import logger

class HerramientaFactory:
    """Factory para creación de herramientas con inyección de dependencias"""
    
    def __init__(self, registro_herramientas, gestor_apis, configuracion: Dict[str, Any]):
        self.registro = registro_herramientas
        self.gestor_apis = gestor_apis
        self.config = configuracion
        self.instancias_herramientas = {}
    
    async def crear_herramienta(self, nombre_herramienta: str) -> Any:
        """
        Crea una instancia de herramienta con dependencias inyectadas.
        
        Args:
            nombre_herramienta: Nombre de la herramienta a crear
        
        Returns:
            Any: Instancia de la herramienta
        """
        if nombre_herramienta in self.instancias_herramientas:
            return self.instancias_herramientas[nombre_herramienta]
        
        herramienta_info = self.registro.herramientas_registradas.get(nombre_herramienta)
        if not herramienta_info:
            raise ValueError(f"Herramienta no encontrada: {nombre_herramienta}")
        
        # Configuración específica para esta herramienta
        config_herramienta = self._obtener_config_herramienta(nombre_herramienta)
        
        # Inyectar dependencias
        dependencias = self._inyectar_dependencias(herramienta_info['clase'])
        
        # Crear instancia
        instancia = herramienta_info['clase'](config_herramienta, **dependencias)
        self.instancias_herramientas[nombre_herramienta] = instancia
        
        logger.info(f"Herramienta creada: {nombre_herramienta}")
        return instancia
    
    def _obtener_config_herramienta(self, nombre_herramienta: str) -> Dict[str, Any]:
        """Obtiene configuración específica para una herramienta"""
        config_especifica = self.config.get('herramientas', {}).get(nombre_herramienta, {})
        return {**self.config, **config_especifica}
    
    def _inyectar_dependencias(self, clase_herramienta: Type) -> Dict[str, Any]:
        """Inyecta dependencias en la herramienta basado en su tipo"""
        dependencias = {}
        
        # Aquí se pueden inyectar dependencias específicas basado en el tipo de herramienta
        if hasattr(clase_herramienta, 'dependencias'):
            for dep_name, dep_type in clase_herramienta.dependencias.items():
                if dep_type == 'gestor_apis':
                    dependencias[dep_name] = self.gestor_apis
        
        return dependencias