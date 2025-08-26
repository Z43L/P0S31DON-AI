from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy import stats
from loguru import logger

class OptimizadorHerramientas:
    """
    Sistema principal de optimización de selección y configuración de herramientas.
    Analiza el rendimiento histórico para determinar las mejores herramientas
    para cada tipo de tarea y contexto.
    """
    
    def __init__(self, sistema_memoria, configuracion: Dict[str, Any]):
        self.memoria = sistema_memoria
        self.config = configuracion
        self.preferencias_actuales: Dict[str, Any] = {}
        self._cargar_preferencias()
        
        logger.info("Optimizador de Herramientas inicializado")
    
    async def optimizar_herramientas(self, episodios: List[Dict]) -> Dict[str, Any]:
        """
        Ejecuta el proceso completo de optimización de herramientas.
        
        Args:
            episodios: Episodios recientes para análisis
        
        Returns:
            Dict: Resultados de la optimización con cambios aplicados
        """
        try:
            # 1. Extraer métricas de rendimiento de herramientas
            metricas_herramientas = await self._extraer_metricas_herramientas(episodios)
            
            # 2. Identificar mejores herramientas por tipo de tarea
            optimizaciones = self._identificar_mejores_herramientas(metricas_herramientas)
            
            # 3. Aplicar cambios si hay mejoras significativas
            cambios_aplicados = await self._aplicar_optimizaciones(optimizaciones)
            
            # 4. Actualizar preferencias y configuraciones
            await self._actualizar_preferencias(cambios_aplicados)
            
            return {
                'optimizaciones_propuestas': optimizaciones,
                'cambios_aplicados': cambios_aplicados,
                'total_episodios_analizados': len(episodios),
                'timestamp_optimizacion': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error en optimización de herramientas: {e}")
            return {'error': str(e)}
    
    async def _extraer_metricas_herramientas(self, episodios: List[Dict]) -> Dict[str, Any]:
        """Extrae métricas de rendimiento para cada herramienta por tipo de tarea"""
        metricas = {}
        
        for episodio in episodios:
            for resultado_tarea in episodio.get('resultados_tareas', []):
                herramienta = resultado_tarea.get('herramienta_utilizada')
                tipo_tarea = resultado_tarea.get('tipo_tarea', 'desconocido')
                exito = resultado_tarea.get('exito', False)
                duracion = resultado_tarea.get('duracion_segundos', 0)
                
                if not herramienta or not tipo_tarea:
                    continue
                
                # Inicializar estructuras si no existen
                if tipo_tarea not in metricas:
                    metricas[tipo_tarea] = {}
                if herramienta not in metricas[tipo_tarea]:
                    metricas[tipo_tarea][herramienta] = {
                        'ejecuciones_totales': 0,
                        'ejecuciones_exitosas': 0,
                        'tiempos_ejecucion': [],
                        'ultima_ejecucion': None
                    }
                
                # Actualizar métricas
                metricas[tipo_tarea][herramienta]['ejecuciones_totales'] += 1
                if exito:
                    metricas[tipo_tarea][herramienta]['ejecuciones_exitosas'] += 1
                if duracion > 0:
                    metricas[tipo_tarea][herramienta]['tiempos_ejecucion'].append(duracion)
                metricas[tipo_tarea][herramienta]['ultima_ejecucion'] = datetime.now().isoformat()
        
        # Calcular métricas agregadas
        for tipo_tarea in metricas:
            for herramienta in metricas[tipo_tarea]:
                datos = metricas[tipo_tarea][herramienta]
                if datos['ejecuciones_totales'] > 0:
                    datos['tasa_exito'] = datos['ejecuciones_exitosas'] / datos['ejecuciones_totales']
                if datos['tiempos_ejecucion']:
                    datos['tiempo_promedio'] = np.mean(datos['tiempos_ejecucion'])
                    datos['tiempo_std'] = np.std(datos['tiempos_ejecucion'])
        
        return metricas