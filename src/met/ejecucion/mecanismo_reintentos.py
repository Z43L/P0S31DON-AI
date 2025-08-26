from typing import Dict, List, Any, Optional, Callable
import asyncio
import math
from datetime import datetime
from loguru import logger

class MecanismoReintentos:
    """Sistema inteligente de reintentos con backoff adaptativo"""
    
    def __init__(self, configuracion: Dict[str, Any]):
        self.config = configuracion
        self.historial_reintentos = []
    
    async def ejecutar_con_reintentos(self, funcion: Callable, *args, 
                                    estrategia: Dict = None, **kwargs) -> Any:
        """
        Ejecuta una función con estrategia de reintentos inteligente.
        
        Args:
            funcion: Función a ejecutar
            estrategia: Estrategia de reintentos
            *args: Argumentos posicionales
            **kwargs: Argumentos nombrados
        
        Returns:
            Any: Resultado de la ejecución
        """
        estrategia = estrategia or self._estrategia_default()
        reintento_actual = 0
        
        while reintento_actual < estrategia['max_reintentos']:
            try:
                resultado = await funcion(*args, **kwargs)
                if resultado.get('exito', False):
                    return resultado
                
                # Manejar resultado fallido
                reintento_actual = await self._manejar_fallo(
                    reintento_actual, estrategia, resultado.get('error')
                )
                
            except Exception as e:
                reintento_actual = await self._manejar_excepcion(
                    reintento_actual, estrategia, e
                )
        
        raise Exception(f"Fallo después de {reintento_actual} reintentos")
    
    async def _manejar_fallo(self, reintento_actual: int, estrategia: Dict, 
                           error: Any) -> int:
        """Maneja un fallo en la ejecución"""
        reintento_actual += 1
        if reintento_actual >= estrategia['max_reintentos']:
            return reintento_actual
        
        delay = self._calcular_delay(reintento_actual, estrategia)
        logger.warning(f"Reintento {reintento_actual} después de {delay}s - Error: {error}")
        
        await asyncio.sleep(delay)
        return reintento_actual
    
    async def _manejar_excepcion(self, reintento_actual: int, estrategia: Dict, 
                               error: Exception) -> int:
        """Maneja una excepción durante la ejecución"""
        reintento_actual += 1
        if reintento_actual >= estrategia['max_reintentos']:
            raise error
        
        delay = self._calcular_delay(reintento_actual, estrategia)
        logger.warning(f"Reintento {reintento_actual} después de {delay}s - Excepción: {error}")
        
        await asyncio.sleep(delay)
        return reintento_actual
    
    def _calcular_delay(self, reintento_actual: int, estrategia: Dict) -> float:
        """Calcula el delay para el próximo reintento"""
        if estrategia['backoff'] == 'ninguno':
            return estrategia['delay']
        elif estrategia['backoff'] == 'lineal':
            return estrategia['delay'] * reintento_actual
        elif estrategia['backoff'] == 'exponencial':
            return estrategia['delay'] * (estrategia.get('base', 2) ** reintento_actual)
        elif estrategia['backoff'] == 'fibonacci':
            return estrategia['delay'] * self._fibonacci(reintento_actual)
        else:
            return estrategia['delay']
    
    def _fibonacci(self, n: int) -> int:
        """Calcula el número Fibonacci para backoff"""
        a, b = 0, 1
        for _ in range(n):
            a, b = b, a + b
        return a
    
    def _estrategia_default(self) -> Dict:
        """Retorna la estrategia de reintentos por defecto"""
        return {
            'max_reintentos': 3,
            'delay': 2,
            'backoff': 'exponencial',
            'base': 2
        }