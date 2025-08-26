import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
import logging

class ConfiguracionSAAM:
    """Clase singleton para la gestión centralizada de configuración del sistema SAAM"""
    
    _instancia = None
    
    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super(ConfiguracionSAAM, cls).__new__(cls)
            cls._instancia._inicializar()
        return cls._instancia
    
    def _inicializar(self):
        """Inicializa la configuración cargando variables de entorno y archivos YAML"""
        # Cargar variables de entorno
        load_dotenv()
        
        # Determinar entorno actual
        self.entorno = os.getenv('SAAM_ENV', 'development')
        
        # Cargar configuración desde archivos YAML
        self.config = self._cargar_configuracion_archivos()
        
        # Configurar logging
        self._configurar_logging()
    
    def _cargar_configuracion_archivos(self) -> Dict[str, Any]:
        """Carga la configuración desde archivos YAML según el entorno"""
        config_base = {}
        config_path = Path(__file__).parent.parent.parent / 'config'
        
        # Cargar configuración base
        base_config_path = config_path / 'base.yaml'
        if base_config_path.exists():
            with open(base_config_path, 'r') as f:
                config_base = yaml.safe_load(f) or {}
        
        # Cargar configuración específica del entorno
        env_config_path = config_path / f'{self.entorno}.yaml'
        if env_config_path.exists():
            with open(env_config_path, 'r') as f:
                env_config = yaml.safe_load(f) or {}
                config_base.update(env_config)
        
        # Sobrescribir con variables de entorno (prioridad máxima)
        self._sobrescribir_con_variables_entorno(config_base)
        
        return config_base
    
    def _sobrescribir_con_variables_entorno(self, config: Dict[str, Any]):
        """Sobrescribe valores de configuración con variables de entorno"""
        for key_path in os.environ:
            if key_path.startswith('SAAM_'):
                # Convertir SAAM_DB_HOST a db.host
                config_key = key_path[5:].lower().replace('_', '.')
                self._establecer_valor_anidado(config, config_key.split('.'), os.environ[key_path])
    
    def _establecer_valor_anidado(self, config_dict: Dict, keys: list, value: Any):
        """Establece un valor en un diccionario anidado usando lista de keys"""
        current = config_dict
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value
    
    def _configurar_logging(self):
        """Configura el sistema de logging basado en la configuración"""
        log_level = self.config.get('logging', {}).get('level', 'INFO')
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def obtener(self, clave: str, default: Any = None) -> Any:
        """Obtiene un valor de configuración usando notación de puntos"""
        keys = clave.split('.')
        value = self.config
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

# Instancia global de configuración
config = ConfiguracionSAAM()