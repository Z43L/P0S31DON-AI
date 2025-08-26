from typing import Dict, List, Any, Optional, Callable
import asyncio
from datetime import datetime
from enum import Enum
from loguru import logger

class EstadoEjecucion(Enum):
    """Estados del ciclo de vida de una tarea"""
    PENDIENTE = "pendiente"
    EN_EJECUCION = "en_ejecucion"
    COMPLETADA = "completada"
    FALLIDA = "fallida"
    REINTENTANDO = "reintentando"

class MotorEjecucion:
    """Motor principal de ejecución de tareas del MET"""
    
    def __init__(self, registro_herramientas, configuracion: Dict[str, Any]):
        self.registro = registro_herramientas
        self.config = configuracion
        self.tareas_activas: Dict[str, Dict] = {}
        self.estadisticas = {
            'tareas_completadas': 0,
            'tareas_fallidas': 0,
            'tiempo_total_ejecucion': 0.0
        }
        
        logger.info("Motor de Ejecución inicializado correctamente")
    
    async def ejecutar_tarea(self, tarea: Dict, contexto: Dict = None) -> Dict[str, Any]:
        """
        Ejecuta una tarea con gestión completa del ciclo de vida.
        
        Args:
            tarea: Definición completa de la tarea a ejecutar
            contexto: Información contextual para la ejecución
        
        Returns:
            Dict: Resultado de la ejecución con metadatos
        """
        tarea_id = tarea.get('id', self._generar_id_tarea())
        logger.info(f"Iniciando ejecución de tarea {tarea_id}")
        
        try:
            # Registrar inicio de ejecución
            self._registrar_inicio_tarea(tarea_id, tarea)
            
            # 1. Validar y preparar la tarea
            tarea_validada = await self._validar_tarea(tarea)
            herramienta = self._seleccionar_herramienta(tarea_validada)
            
            # 2. Ejecutar con estrategia de reintentos
            resultado = await self._ejecutar_con_reintentos(
                herramienta, tarea_validada, contexto
            )
            
            # 3. Procesar resultado
            resultado_procesado = self._procesar_resultado(resultado, tarea_validada)
            self._registrar_exito_tarea(tarea_id, resultado_procesado)
            
            logger.success(f"Tarea {tarea_id} completada exitosamente")
            return resultado_procesado
            
        except Exception as e:
            # 4. Manejo de errores no recuperables
            resultado_error = self._manejar_error_irrecuperable(e, tarea)
            self._registrar_fallo_tarea(tarea_id, resultado_error)
            
            logger.error(f"Tarea {tarea_id} falló: {str(e)}")
            return resultado_error
    
    async def _ejecutar_con_reintentos(self, herramienta: Callable, tarea: Dict, 
                                     contexto: Dict) -> Dict[str, Any]:
        """
        Ejecuta una tarea con estrategia de reintentos inteligente.
        
        Args:
            herramienta: Función de la herramienta a ejecutar
            tarea: Tarea validada
            contexto: Contexto de ejecución
        
        Returns:
            Dict: Resultado de la ejecución
        """
        max_reintentos = tarea.get('max_reintentos', self.config.get('max_reintentos', 3))
        reintento_actual = 0
        
        while reintento_actual <= max_reintentos:
            try:
                resultado = await self._ejecutar_simple(herramienta, tarea, contexto)
                if resultado['exito']:
                    return resultado
                
                # Si falló pero es recuperable, reintentar
                if self._es_error_recuperable(resultado['error']):
                    reintento_actual += 1
                    await self._manejar_reintento(reintento_actual, resultado['error'])
                else:
                    break
                    
            except Exception as e:
                reintento_actual += 1
                if reintento_actual > max_reintentos or not self._es_error_recuperable(e):
                    raise
                await self._manejar_reintento(reintento_actual, e)
        
        raise Exception(f"Fallo después de {reintento_actual} intentos")
    
    async def _ejecutar_simple(self, herramienta: Callable, tarea: Dict, 
                             contexto: Dict) -> Dict[str, Any]:
        """
        Ejecución simple de una tarea con control de timeout.
        
        Args:
            herramienta: Función de la herramienta
            tarea: Tarea a ejecutar
            contexto: Contexto de ejecución
        
        Returns:
            Dict: Resultado de la ejecución
        """
        timeout = tarea.get('timeout', self.config.get('timeout_default', 30))
        
        try:
            if asyncio.iscoroutinefunction(herramienta):
                # Ejecución asíncrona
                resultado = await asyncio.wait_for(
                    herramienta(**tarea['parametros'], contexto=contexto),
                    timeout=timeout
                )
            else:
                # Ejecución síncrona en thread pool
                loop = asyncio.get_event_loop()
                resultado = await loop.run_in_executor(
                    None,  # Usar executor por defecto
                    lambda: herramienta(**tarea['parametros'], contexto=contexto)
                )
            
            return {
                'exito': True,
                'resultado': resultado,
                'error': None
            }
            
        except asyncio.TimeoutError:
            return {
                'exito': False,
                'resultado': None,
                'error': f"Timeout después de {timeout} segundos"
            }
        except Exception as e:
            return {
                'exito': False,
                'resultado': None,
                'error': str(e)
            }