from typing import Dict, List, Any, Optional, Callable
import asyncio
import time
from datetime import datetime
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from loguru import logger

class EstadoEjecucion(Enum):
    """Estados posibles durante el ciclo de ejecución de una tarea"""
    PENDIENTE = "pendiente"
    EN_EJECUCION = "en_ejecucion"
    COMPLETADA = "completada"
    FALLIDA = "fallida"
    REINTENTANDO = "reintentando"
    TIMEOUT = "timeout"

class ModuloEjecucionTareas:
    """Módulo principal de Ejecución de Tareas de SAAM - Brazo ejecutor del sistema"""
    
    def __init__(self, sistema_herramientas, sistema_memoria, configuracion: Dict[str, Any]):
        self.herramientas = sistema_herramientas
        self.memoria = sistema_memoria
        self.config = configuracion
        self.estado_global = EstadoEjecucion.PENDIENTE
        
        # Configuración de pools de ejecución para operaciones bloqueantes
        self.thread_pool = ThreadPoolExecutor(
            max_workers=configuracion.get('max_workers', 10)
        )
        self.process_pool = ProcessPoolExecutor(
            max_workers=configuracion.get('max_process_workers', 4)
        )
        
        # Registro de estado de tareas en ejecución
        self.tareas_activas: Dict[str, Dict] = {}
        self.metricas_ejecucion = {
            'tareas_completadas': 0,
            'tareas_fallidas': 0,
            'tiempo_total_ejecucion': 0.0
        }
        
        logger.info("Módulo de Ejecución de Tareas inicializado correctamente")
    
    async def ejecutar_tarea(self, tarea: Dict[str, Any], contexto: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Ejecuta una tarea específica con los parámetros y contexto proporcionados.
        
        Args:
            tarea: Diccionario con la definición completa de la tarea
            contexto: Contexto adicional para la ejecución (historial, preferencias)
        
        Returns:
            Dict: Resultado de la ejecución con metadatos enriquecidos
        """
        tarea_id = tarea.get('id', self._generar_id_tarea())
        logger.info(f"Iniciando ejecución de tarea {tarea_id}")
        
        # Registrar inicio de ejecución en sistema de monitorización
        self._registrar_inicio_tarea(tarea_id, tarea)
        
        try:
            # 1. Validación y preparación de la tarea
            tarea_validada = self._validar_tarea(tarea)
            herramienta = self._seleccionar_herramienta(tarea_validada)
            
            # 2. Ejecución controlada con timeout
            resultado = await self._ejecutar_con_timeout(
                herramienta, tarea_validada, contexto
            )
            
            # 3. Procesamiento y normalización del resultado
            resultado_procesado = self._procesar_resultado(resultado, tarea_validada)
            self._registrar_exito_tarea(tarea_id, resultado_procesado)
            
            logger.success(f"Tarea {tarea_id} completada exitosamente")
            return resultado_procesado
            
        except Exception as e:
            # 4. Manejo robusto de errores con estrategia de reintentos
            resultado_error = await self._manejar_error(e, tarea, contexto)
            self._registrar_fallo_tarea(tarea_id, resultado_error)
            
            logger.error(f"Tarea {tarea_id} falló: {str(e)}")
            return resultado_error
    
    def _generar_id_tarea(self) -> str:
        """Genera un ID único para identificación de la tarea"""
        import uuid
        return f"tarea_{uuid.uuid4().hex[:8]}"
    
    def _validar_tarea(self, tarea: Dict) -> Dict:
        """Valida la estructura integral y parámetros de una tarea"""
        required_keys = {'tipo', 'herramienta', 'parametros'}
        if not all(key in tarea for key in required_keys):
            raise ValueError(f"Tarea inválida: faltan campos requeridos {required_keys}")
        
        # Validación específica según el tipo de tarea
        if tarea['tipo'] == 'busqueda_web' and 'query' not in tarea['parametros']:
            raise ValueError("Búsqueda web requiere parámetro 'query'")
        
        return tarea
    
    def _seleccionar_herramienta(self, tarea: Dict) -> Callable:
        """Selecciona la herramienta óptima para el tipo de tarea"""
        herramienta_nombre = tarea['herramienta']
        herramienta = self.herramientas.obtener_herramienta(herramienta_nombre)
        
        if not herramienta:
            raise ValueError(f"Herramienta '{herramienta_nombre}' no disponible")
        
        return herramienta
    
    async def _ejecutar_con_timeout(self, herramienta: Callable, tarea: Dict, contexto: Dict) -> Any:
        """Ejecuta la herramienta con control estricto de timeout"""
        timeout = tarea.get('timeout', self.config.get('timeout_default', 30))
        
        try:
            if asyncio.iscoroutinefunction(herramienta):
                # Función asíncrona - ejecución directa
                resultado = await asyncio.wait_for(
                    herramienta(**tarea['parametros'], contexto=contexto),
                    timeout=timeout
                )
            else:
                # Función síncrona - ejecución en thread pool
                loop = asyncio.get_event_loop()
                resultado = await loop.run_in_executor(
                    self.thread_pool,
                    lambda: herramienta(**tarea['parametros'], contexto=contexto)
                )
            
            return resultado
            
        except asyncio.TimeoutError:
            raise TimeoutError(f"Timeout después de {timeout} segundos")
        except Exception as e:
            raise e
    
    def _procesar_resultado(self, resultado: Any, tarea: Dict) -> Dict[str, Any]:
        """Procesa y normaliza el resultado según el tipo de tarea"""
        if tarea['tipo'] == 'busqueda_web':
            return self._procesar_resultado_busqueda(resultado)
        elif tarea['tipo'] == 'generacion_texto':
            return self._procesar_resultado_texto(resultado)
        else:
            return {'resultado': resultado}
    
    async def _manejar_error(self, error: Exception, tarea: Dict, contexto: Dict) -> Dict[str, Any]:
        """Maneja errores durante la ejecución con estrategia de reintentos inteligentes"""
        max_reintentos = tarea.get('max_reintentos', self.config.get('max_reintentos', 3))
        reintento_actual = contexto.get('reintento_actual', 0)
        
        if reintento_actual < max_reintentos:
            logger.warning(f"Reintentando tarea ({reintento_actual + 1}/{max_reintentos})")
            
            # Backoff exponencial con jitter para evitar congestión
            await asyncio.sleep(2 ** reintento_actual + random.uniform(0, 1))
            
            contexto['reintento_actual'] = reintento_actual + 1
            return await self.ejecutar_tarea(tarea, contexto)
        else:
            # Reintentos agotados - retorno controlado del error
            return {
                'exito': False,
                'error': str(error),
                'tipo_error': type(error).__name__,
                'reintentos': reintento_actual
            }
    
    def _registrar_inicio_tarea(self, tarea_id: str, tarea: Dict) -> None:
        """Registra el inicio de una tarea en el sistema de monitorización"""
        self.tareas_activas[tarea_id] = {
            'estado': EstadoEjecucion.EN_EJECUCION.value,
            'inicio': time.time(),
            'tarea': tarea
        }
    
    def _registrar_exito_tarea(self, tarea_id: str, resultado: Dict) -> None:
        """Registra la finalización exitosa de una tarea"""
        if tarea_id in self.tareas_activas:
            duracion = time.time() - self.tareas_activas[tarea_id]['inicio']
            
            self.tareas_activas[tarea_id].update({
                'estado': EstadoEjecucion.COMPLETADA.value,
                'duracion': duracion,
                'resultado': resultado
            })
            
            self.metricas_ejecucion['tareas_completadas'] += 1
            self.metricas_ejecucion['tiempo_total_ejecucion'] += duracion
    
    def _registrar_fallo_tarea(self, tarea_id: str, resultado: Dict) -> None:
        """Registra el fallo de una tarea con información de diagnóstico"""
        if tarea_id in self.tareas_activas:
            duracion = time.time() - self.tareas_activas[tarea_id]['inicio']
            
            self.tareas_activas[tarea_id].update({
                'estado': EstadoEjecucion.FALLIDA.value,
                'duracion': duracion,
                'error': resultado.get('error')
            })
            
            self.metricas_ejecucion['tareas_fallidas'] += 1