import aiohttp
import json
from typing import Dict, List, Any, Optional
from .base import HerramientaBase
from loguru import logger

class APIRestTool(HerramientaBase):
    """
    Herramienta para realizar llamadas HTTP a APIs RESTful con manejo
    avanzado de errores, reintentos y procesamiento de respuestas.
    """
    
    def __init__(self, configuracion: Dict[str, Any]):
        super().__init__(configuracion)
        self.config_api = configuracion.get('api_clients', {})
        self.timeout_default = self.config_api.get('timeout', 30)
        self.max_reintentos = self.config_api.get('max_reintentos', 3)
        self.session = None
        
    async def ejecutar(self, url: str, metodo: str = 'GET', 
                      parametros: Dict = None, headers: Dict = None,
                      cuerpo: Any = None, timeout: int = None,
                      **kwargs) -> Dict[str, Any]:
        """
        Ejecuta una llamada HTTP a una API RESTful.
        
        Args:
            url: URL del endpoint
            metodo: Método HTTP (GET, POST, PUT, DELETE)
            parametros: Parámetros de query string
            headers: Headers HTTP
            cuerpo: Cuerpo de la solicitud
            timeout: Timeout en segundos
            **kwargs: Parámetros adicionales
        
        Returns:
            Dict: Respuesta de la API con metadata
        """
        timeout = timeout or self.timeout_default
        headers = headers or {}
        parametros = parametros or {}
        
        # Headers por defecto
        headers.setdefault('Content-Type', 'application/json')
        headers.setdefault('User-Agent', 'SAAM-API-Client/1.0')
        
        # Inicializar sesión si no existe
        if self.session is None:
            self.session = aiohttp.ClientSession()
        
        for intento in range(self.max_reintentos):
            try:
                async with self.session.request(
                    method=metodo.upper(),
                    url=url,
                    params=parametros,
                    headers=headers,
                    json=cuerpo,
                    timeout=timeout,
                    **kwargs
                ) as response:
                    
                    contenido = await self._procesar_respuesta(response)
                    
                    return {
                        'estado': response.status,
                        'headers': dict(response.headers),
                        'datos': contenido,
                        'exito': response.status < 400,
                        'intentos': intento + 1
                    }
                    
            except aiohttp.ClientError as e:
                if intento == self.max_reintentos - 1:
                    raise
                logger.warning(f"Intento {intento + 1} fallido: {e}")
                continue
    
    async def _procesar_respuesta(self, response) -> Any:
        """Procesa la respuesta HTTP según el content-type"""
        content_type = response.headers.get('Content-Type', '').lower()
        
        if 'application/json' in content_type:
            return await response.json()
        elif 'text/' in content_type:
            return await response.text()
        else:
            return await response.read()
    
    async def cerrar(self):
        """Cierra la sesión HTTP"""
        if self.session:
            await self.session.close()
            self.session = None