from typing import Dict, Any, Optional
import httpx
from loguru import logger
import json

class ClienteAPIREST:
    """Cliente para comunicación RESTful entre módulos SAAM"""
    
    def __init__(self, config_base: Dict[str, Any]):
        self.config = config_base
        self.sesion = httpx.AsyncClient(timeout=30.0)
        self.endpoints = self._cargar_endpoints()
        
    def _cargar_endpoints(self) -> Dict[str, str]:
        """Carga los endpoints de los diferentes módulos"""
        return {
            'mcp': self.config.get('endpoints', {}).get('mcp', 'http://mcp:8000'),
            'met': self.config.get('endpoints', {}).get('met', 'http://met:8001'),
            'sm3': self.config.get('endpoints', {}).get('sm3', 'http://sm3:8002'),
            'mao': self.config.get('endpoints', {}).get('mao', 'http://mao:8003')
        }
    
    async def enviar_solicitud(
        self,
        modulo_destino: str,
        endpoint: str,
        datos: Dict[str, Any],
        intentos_maximos: int = 3
    ) -> Dict[str, Any]:
        """
        Envía una solicitud RESTful a otro módulo con reintentos automáticos.
        
        Args:
            modulo_destino: Nombre del módulo destino ('mcp', 'met', 'sm3', 'mao')
            endpoint: Endpoint específico del API
            datos: Datos a enviar en la solicitud
            intentos_maximos: Número máximo de reintentos
            
        Returns:
            Dict: Respuesta del módulo destino
        """
        url_base = self.endpoints.get(modulo_destino)
        if not url_base:
            raise ValueError(f"Módulo destino '{modulo_destino}' no configurado")
        
        url = f"{url_base}/{endpoint}"
        headers = {
            'Content-Type': 'application/json',
            'X-SAAM-Correlation-ID': self._generar_correlation_id()
        }
        
        for intento in range(intentos_maximos):
            try:
                respuesta = await self.sesion.post(
                    url,
                    json=datos,
                    headers=headers,
                    timeout=30.0
                )
                
                respuesta.raise_for_status()
                return respuesta.json()
                
            except httpx.TimeoutException:
                logger.warning(f"Timeout en intento {intento + 1} para {modulo_destino}")
                if intento == intentos_maximos - 1:
                    raise
                
            except httpx.HTTPError as e:
                logger.error(f"Error HTTP en intento {intento + 1}: {e}")
                if intento == intentos_maximos - 1:
                    raise
        
        return {}
    
    def _generar_correlation_id(self) -> str:
        """Genera un ID único de correlación para trazar la solicitud"""
        import uuid
        return f"corr_{uuid.uuid4().hex[:16]}"