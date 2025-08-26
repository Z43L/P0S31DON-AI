import aiohttp
from typing import Dict, List, Any, Optional
from .base import HerramientaBase
from loguru import logger

class BusquedaWebTool(HerramientaBase):
    """
    Herramienta avanzada de búsqueda web con soporte para múltiples motores
    y estrategia de fallback automático.
    """
    
    def __init__(self, configuracion: Dict[str, Any]):
        super().__init__(configuracion)
        self.config_busqueda = configuracion.get('busqueda_web', {})
        self.motores = self._inicializar_motores()
        self.timeout = self.config_busqueda.get('timeout', 15)
        
    def _inicializar_motores(self) -> List[Dict]:
        """Inicializa los motores de búsqueda configurados"""
        motores = []
        config_motores = self.config_busqueda.get('motores', {})
        
        if config_motores.get('google', {}).get('habilitado', False):
            motores.append({
                'nombre': 'google',
                'prioridad': 1,
                'config': config_motores['google']
            })
        
        if config_motores.get('bing', {}).get('habilitado', False):
            motores.append({
                'nombre': 'bing',
                'prioridad': 2,
                'config': config_motores['bing']
            })
        
        # Ordenar por prioridad
        motores.sort(key=lambda x: x['prioridad'])
        return motores
    
    async def ejecutar(self, query: str, max_resultados: int = 10, 
                      motor: str = None, **kwargs) -> List[Dict[str, Any]]:
        """
        Ejecuta una búsqueda web utilizando los motores configurados.
        
        Args:
            query: Términos de búsqueda
            max_resultados: Número máximo de resultados
            motor: Motor específico a usar (opcional)
            **kwargs: Parámetros adicionales
        
        Returns:
            List[Dict]: Resultados de búsqueda
        """
        if motor:
            # Motor específico solicitado
            return await self._buscar_con_motor(motor, query, max_resultados, kwargs)
        
        # Búsqueda con estrategia de fallback
        resultados = []
        for motor_info in self.motores:
            try:
                motor_resultados = await self._buscar_con_motor(
                    motor_info['nombre'], query, max_resultados, kwargs
                )
                resultados.extend(motor_resultados)
                
                if len(resultados) >= max_resultados:
                    break
                    
            except Exception as e:
                logger.warning(f"Error con motor {motor_info['nombre']}: {e}")
                continue
        
        return resultados[:max_resultados]
    
    async def _buscar_con_motor(self, motor: str, query: str, 
                               max_resultados: int, kwargs: Dict) -> List[Dict]:
        """Búsqueda con un motor específico"""
        if motor == 'google':
            return await self._buscar_google(query, max_resultados, kwargs)
        elif motor == 'bing':
            return await self._buscar_bing(query, max_resultados, kwargs)
        else:
            raise ValueError(f"Motor no soportado: {motor}")
    
    async def _buscar_google(self, query: str, max_resultados: int, 
                           kwargs: Dict) -> List[Dict]:
        """Implementación de búsqueda con Google Custom Search API"""
        config = next((m['config'] for m in self.motores if m['nombre'] == 'google'), {})
        api_key = config.get('api_key')
        search_engine_id = config.get('search_engine_id')
        
        if not api_key or not search_engine_id:
            raise ValueError("Configuración de Google Search incompleta")
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': api_key,
            'cx': search_engine_id,
            'q': query,
            'num': min(max_resultados, 10)
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=self.timeout) as response:
                response.raise_for_status()
                data = await response.json()
                
                return [
                    {
                        'titulo': item.get('title', ''),
                        'url': item.get('link', ''),
                        'snippet': item.get('snippet', ''),
                        'fuente': 'google',
                        'score': item.get('score', 0.0)
                    }
                    for item in data.get('items', [])
                ]