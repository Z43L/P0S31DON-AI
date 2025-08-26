from typing import Dict, Any, Optional
import zlib
import json
from loguru import logger

class OptimizadorMemoria:
    """
    Sistema de optimización para la memoria de trabajo.
    Aplica compresión y técnicas de caching para mejorar el rendimiento.
    """
    
    def __init__(self, configuracion: Dict[str, Any]):
        self.config = configuracion
        self.cache_comprimido: Dict[str, bytes] = {}
        self.estadisticas_compresion: Dict[str, int] = {
            'total_comprimido': 0,
            'total_original': 0,
            'ratio_promedio': 0.0
        }
    
    def comprimir_valor(self, valor: Any, umbral: int = 1024) -> Any:
        """
        Comprime valores grandes para ahorrar memoria.
        
        Args:
            valor: Valor a comprimir
            umbral: Tamaño mínimo para comprimir (bytes)
        
        Returns:
            Any: Valor original o comprimido
        """
        if not self.config.get('compresion_habilitada', True):
            return valor
        
        # Serializar a JSON para comprimir
        valor_json = json.dumps(valor)
        tamano_original = len(valor_json.encode('utf-8'))
        
        if tamano_original < umbral:
            return valor
        
        # Comprimir usando zlib
        valor_comprimido = zlib.compress(valor_json.encode('utf-8'))
        tamano_comprimido = len(valor_comprimido)
        
        # Actualizar estadísticas
        self.estadisticas_compresion['total_original'] += tamano_original
        self.estadisticas_compresion['total_comprimido'] += tamano_comprimido
        self.estadisticas_compresion['ratio_promedio'] = (
            self.estadisticas_compresion['total_comprimido'] / 
            self.estadisticas_compresion['total_original']
            if self.estadisticas_compresion['total_original'] > 0 else 0.0
        )
        
        logger.debug(f"Valor comprimido: {tamano_original} → {tamano_comprimido} bytes")
        return {'_comprimido': True, 'datos': valor_comprimido}
    
    def descomprimir_valor(self, valor: Any) -> Any:
        """
        Descomprime valores previamente comprimidos.
        
        Args:
            valor: Valor posiblemente comprimido
        
        Returns:
            Any: Valor descomprimido
        """
        if isinstance(valor, dict) and valor.get('_comprimido', False):
            try:
                datos_comprimidos = valor['datos']
                datos_json = zlib.decompress(datos_comprimidos).decode('utf-8')
                return json.loads(datos_json)
            except Exception as e:
                logger.error(f"Error descomprimiendo valor: {e}")
                return valor
        
        return valor
    
    def aplicar_optimizaciones(self, clave: str, valor: Any) -> Any:
        """
        Aplica todas las optimizaciones configuradas a un valor.
        
        Args:
            clave: Clave del valor (para caching)
            valor: Valor a optimizar
        
        Returns:
            Any: Valor optimizado
        """
        valor_optimizado = valor
        
        # Aplicar compresión si está habilitada
        if self.config.get('compresion_habilitada', True):
            valor_optimizado = self.comprimir_valor(
                valor_optimizado, 
                self.config.get('compresion_umbral', 1024)
            )
        
        return valor_optimizado
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de optimización.
        
        Returns:
            Dict: Métricas de compresión y optimización
        """
        return self.estadisticas_compresion.copy()