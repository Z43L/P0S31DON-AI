from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from enum import Enum
import json
from loguru import logger

class TipoAnalisis(Enum):
    """Tipos de análisis que puede realizar el MAO"""
    RENDIMIENTO_HERRAMIENTAS = "rendimiento_herramientas"
    PATRONES_EJECUCION = "patrones_ejecucion"
    OPTIMIZACION_SECUENCIA = "optimizacion_secuencia"
    DETECCION_ANOMALIAS = "deteccion_anomalias"
    CREACION_HABILIDADES = "creacion_habilidades"

class ModuloAprendizajeOptimizacion:
    """Módulo principal de Aprendizaje y Optimización de SAAM"""
    
    def __init__(self, sistema_memoria, configuracion: Dict[str, Any]):
        self.memoria = sistema_memoria
        self.config = configuracion
        self.estado_analisis = {}
        self.ultimo_analisis = None
        
        # Configuración de umbrales y parámetros
        self.umbrales = self.config.get('umbrales', {})
        self.intervalo_analisis = self.config.get('intervalo_analisis', 3600)  # 1 hora
        
        logger.info("Módulo de Aprendizaje y Optimización inicializado")
    
    async def iniciar_ciclo_aprendizaje(self):
        """Inicia el ciclo continuo de aprendizaje y optimización"""
        import asyncio
        
        while True:
            try:
                await self._ejecutar_ciclo_completo()
                await asyncio.sleep(self.intervalo_analisis)
            except Exception as e:
                logger.error(f"Error en ciclo de aprendizaje: {e}")
                await asyncio.sleep(300)  # Reintentar después de 5 minutos
    
    async def _ejecutar_ciclo_completo(self):
        """Ejecuta un ciclo completo de análisis y optimización"""
        logger.info("Iniciando ciclo de análisis y optimización")
        
        # 1. Recolección de datos recientes
        episodios_recientes = await self._obtener_episodios_recientes()
        
        if not episodios_recientes:
            logger.info("No hay episodios recientes para analizar")
            return
        
        # 2. Ejecución de análisis en paralelo
        resultados_analisis = await self._ejecutar_analisis_paralelos(episodios_recientes)
        
        # 3. Procesamiento de recomendaciones
        recomendaciones = await self._generar_recomendaciones(resultados_analisis)
        
        # 4. Aplicación de optimizaciones
        if recomendaciones:
            await self._aplicar_optimizaciones(recomendaciones)
        
        logger.success("Ciclo de aprendizaje completado exitosamente")
    
    async def _obtener_episodios_recientes(self, horas: int = 24) -> List[Dict]:
        """Obtiene episodios recientes para análisis"""
        try:
            desde = datetime.now() - timedelta(hours=horas)
            filtros = {'desde': desde}
            
            episodios = self.memoria.obtener_episodios(filtros, limite=1000)
            return episodios
            
        except Exception as e:
            logger.error(f"Error obteniendo episodios recientes: {e}")
            return []
    
    async def _ejecutar_analisis_paralelos(self, episodios: List[Dict]) -> Dict[str, Any]:
        """Ejecuta todos los tipos de análisis en paralelo"""
        import asyncio
        
        # Crear DataFrame para análisis
        df_episodios = self._crear_dataframe_episodios(episodios)
        
        # Ejecutar análisis en paralelo
        tareas = [
            self._analizar_rendimiento_herramientas(df_episodios),
            self._analizar_patrones_ejecucion(df_episodios),
            self._analizar_optimizacion_secuencia(df_episodios),
            self._detectar_anomalias(df_episodios)
        ]
        
        resultados = await asyncio.gather(*tareas, return_exceptions=True)
        
        return {
            'rendimiento_herramientas': resultados[0],
            'patrones_ejecucion': resultados[1],
            'optimizacion_secuencia': resultados[2],
            'deteccion_anomalias': resultados[3]
        }
    
    def _crear_dataframe_episodios(self, episodios: List[Dict]) -> pd.DataFrame:
        """Convierte los episodios en un DataFrame para análisis"""
        datos = []
        
        for episodio in episodios:
            fila = {
                'id': episodio.get('id'),
                'timestamp': episodio.get('timestamp'),
                'objetivo': episodio.get('objetivo'),
                'estado': episodio.get('estado'),
                'duracion_total': episodio.get('duracion_total', 0),
                'num_tareas': len(episodio.get('resultados', [])),
                'exito_global': episodio.get('metricas', {}).get('exito', 0)
            }
            
            # Extraer métricas por tarea
            for tarea in episodio.get('resultados', []):
                tarea_id = tarea.get('id', '')
                prefijo = f'tarea_{tarea_id}_'
                
                fila.update({
                    f'{prefijo}exito': tarea.get('metadatos', {}).get('exito', False),
                    f'{prefijo}duracion': tarea.get('metadatos', {}).get('duracion', 0),
                    f'{prefijo}herramienta': tarea.get('metadatos', {}).get('herramienta', ''),
                    f'{prefijo}error': tarea.get('metadatos', {}).get('error', '')
                })
            
            datos.append(fila)
        
        return pd.DataFrame(datos)