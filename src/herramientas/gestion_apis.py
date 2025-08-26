from typing import Dict, List, Any, Optional
import os
from dotenv import load_dotenv
from loguru import logger

class GestorAPIs:
    """Sistema de gestión de APIs externas y credenciales"""
    
    def __init__(self, configuracion: Dict[str, Any]):
        self.config = configuracion
        self.credenciales = {}
        self._cargar_credenciales()
    
    def _cargar_credenciales(self):
        """Carga credenciales desde variables de entorno y configuración"""
        # Cargar desde .env
        load_dotenv()
        
        # APIs configuradas
        apis_config = self.config.get('apis', {})
        
        # OpenAI
        if apis_config.get('openai', {}).get('habilitado', False):
            self.credenciales['openai'] = {
                'api_key': os.getenv('OPENAI_API_KEY') or apis_config['openai'].get('api_key'),
                'modelo_default': apis_config['openai'].get('modelo_default', 'gpt-3.5-turbo')
            }
        
        # Google Search
        if apis_config.get('google_search', {}).get('habilitado', False):
            self.credenciales['google_search'] = {
                'api_key': os.getenv('GOOGLE_API_KEY') or apis_config['google_search'].get('api_key'),
                'search_engine_id': os.getenv('GOOGLE_SEARCH_ENGINE_ID') or apis_config['google_search'].get('search_engine_id')
            }
        
        # Verificar credenciales esenciales
        self._validar_credenciales()
    
    def _validar_credenciales(self):
        """Valida que las credenciales esenciales estén configuradas"""
        credenciales_faltantes = []
        
        if 'openai' in self.credenciales and not self.credenciales['openai']['api_key']:
            credenciales_faltantes.append('OpenAI API Key')
        
        if 'google_search' in self.credenciales and not self.credenciales['google_search']['api_key']:
            credenciales_faltantes.append('Google API Key')
        
        if credenciales_faltantes:
            logger.warning(f"Credenciales faltantes: {', '.join(credenciales_faltantes)}")
    
    def obtener_credencial(self, servicio: str) -> Optional[Dict]:
        """Obtiene credenciales para un servicio específico"""
        return self.credenciales.get(servicio)
    
    def actualizar_credencial(self, servicio: str, credencial: Dict):
        """Actualiza credenciales para un servicio"""
        self.credenciales[servicio] = credencial
        logger.info(f"Credenciales actualizadas para {servicio}")