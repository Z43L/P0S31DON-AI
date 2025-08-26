from typing import Dict, List, Any, Optional, Type
import importlib
import inspect
from pathlib import Path
from loguru import logger

class RegistroHerramientas:
    """Sistema centralizado de registro y descubrimiento de herramientas"""
    
    def __init__(self, configuracion: Dict[str, Any]):
        self.config = configuracion
        self.herramientas_registradas: Dict[str, Dict] = {}
        self.categorias_herramientas: Dict[str, List[str]] = {}
        self._inicializar_registro()
    
    def _inicializar_registro(self):
        """Inicializa el registro con herramientas integradas y personalizadas"""
        # Cargar herramientas integradas
        self._cargar_herramientas_integradas()
        
        # Cargar herramientas personalizadas desde directorios configurados
        directorios_herramientas = self.config.get('herramientas', {}).get('directorios', [])
        for directorio in directorios_herramientas:
            self._cargar_herramientas_directorio(directorio)
        
        logger.info(f"Registro de herramientas inicializado con {len(self.herramientas_registradas)} herramientas")
    
    def _cargar_herramientas_integradas(self):
        """Carga las herramientas integradas en el sistema"""
        herramientas_integradas = [
            'src.herramientas.busqueda_web',
            'src.herramientas.generacion_texto',
            'src.herramientas.api_clients',
            'src.herramientas.procesamiento_datos',
            'src.herramientas.analisis_contenido'
        ]
        
        for modulo_path in herramientas_integradas:
            try:
                modulo = importlib.import_module(modulo_path)
                self._registrar_modulo_herramientas(modulo)
            except ImportError as e:
                logger.warning(f"No se pudo cargar módulo {modulo_path}: {e}")
    
    def _cargar_herramientas_directorio(self, directorio: str):
        """Carga herramientas desde un directorio específico"""
        try:
            path_dir = Path(directorio)
            if not path_dir.exists():
                logger.warning(f"Directorio de herramientas no existe: {directorio}")
                return
            
            # Buscar archivos Python en el directorio
            for archivo in path_dir.glob("**/*.py"):
                if archivo.name == "__init__.py":
                    continue
                
                # Convertir ruta a módulo
                modulo_path = self._ruta_a_modulo(archivo)
                try:
                    modulo = importlib.import_module(modulo_path)
                    self._registrar_modulo_herramientas(modulo)
                except ImportError as e:
                    logger.warning(f"Error importando {modulo_path}: {e}")
                    
        except Exception as e:
            logger.error(f"Error cargando herramientas desde {directorio}: {e}")
    
    def _registrar_modulo_herramientas(self, modulo):
        """Registra todas las herramientas de un módulo"""
        for nombre, objeto in inspect.getmembers(modulo):
            if (inspect.isclass(objeto) and 
                hasattr(objeto, 'es_herramienta') and 
                objeto.es_herramienta):
                
                herramienta_info = {
                    'clase': objeto,
                    'modulo': modulo.__name__,
                    'metadata': getattr(objeto, 'metadata', {}),
                    'instancia': None
                }
                
                self.herramientas_registradas[nombre] = herramienta_info
                
                # Registrar en categorías
                categorias = herramienta_info['metadata'].get('categorias', ['general'])
                for categoria in categorias:
                    if categoria not in self.categorias_herramientas:
                        self.categorias_herramientas[categoria] = []
                    self.categorias_herramientas[categoria].append(nombre)
                
                logger.debug(f"Herramienta registrada: {nombre}")
    
    def obtener_herramienta(self, nombre: str) -> Optional[Any]:
        """Obtiene una herramienta por nombre"""
        if nombre not in self.herramientas_registradas:
            return None
        
        info = self.herramientas_registradas[nombre]
        
        # Crear instancia si no existe
        if info['instancia'] is None:
            info['instancia'] = info['clase'](self.config)
        
        return info['instancia']
    
    def obtener_herramientas_por_categoria(self, categoria: str) -> List[Dict]:
        """Obtiene herramientas de una categoría específica"""
        if categoria not in self.categorias_herramientas:
            return []
        
        return [
            self.herramientas_registradas[nombre]
            for nombre in self.categorias_herramientas[categoria]
            if nombre in self.herramientas_registradas
        ]