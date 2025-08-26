from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from loguru import logger

class GestorMetricas:
    """
    Sistema de seguimiento y análisis de métricas de rendimiento de habilidades.
    """
    
    def __init__(self, base_conocimiento, configuracion: Dict[str, Any]):
        self.base = base_conocimiento
        self.config = configuracion
        
    async def registrar_ejecucion(self, habilidad_id: str, resultado: Dict):
        """
        Registra los resultados de una ejecución de habilidad.
        
        Args:
            habilidad_id: ID de la habilidad ejecutada
            resultado: Resultados de la ejecución
        """
        try:
            # Obtener métricas actuales
            habilidad = await self.base.obtener_habilidad(habilidad_id)
            if not habilidad:
                logger.warning(f"Habilidad no encontrada: {habilidad_id}")
                return
            
            metricas_actuales = habilidad.get('metricas_rendimiento', {})
            estadisticas_actuales = habilidad.get('estadisticas_uso', {})
            
            # Actualizar métricas
            nuevas_metricas = self._calcular_nuevas_metricas(metricas_actuales, resultado)
            nuevas_estadisticas = self._actualizar_estadisticas(estadisticas_actuales, resultado)
            
            # Actualizar habilidad
            await self.base.actualizar_habilidad(
                habilidad_id,
                {
                    'metricas_rendimiento': nuevas_metricas,
                    'estadisticas_uso': nuevas_estadisticas,
                    'fecha_actualizacion': datetime.now().isoformat()
                }
            )
            
            logger.debug(f"Métricas actualizadas para habilidad {habilidad_id}")
            
        except Exception as e:
            logger.error(f"Error registrando ejecución: {e}")
    
    def _calcular_nuevas_metricas(self, metricas_actuales: Dict, resultado: Dict) -> Dict:
        """Calcula nuevas métricas basado en el resultado de ejecución"""
        nuevas_metricas = metricas_actuales.copy()
        
        # Tasa de éxito (media móvil exponencial)
        exito_actual = 1.0 if resultado.get('exito') else 0.0
        tasa_exito_anterior = metricas_actuales.get('tasa_exito', 0.5)
        alpha = self.config.get('alpha_metricas', 0.1)  # Factor de suavizado
        
        nuevas_metricas['tasa_exito'] = (
            alpha * exito_actual + (1 - alpha) * tasa_exito_anterior
        )
        
        # Tiempo de ejecución (media móvil)
        tiempo_ejecucion = resultado.get('duracion', 0)
        if tiempo_ejecucion > 0:
            tiempo_promedio_anterior = metricas_actuales.get('tiempo_promedio', 0)
            if tiempo_promedio_anterior == 0:
                nuevas_metricas['tiempo_promedio'] = tiempo_ejecucion
            else:
                nuevas_metricas['tiempo_promedio'] = (
                    alpha * tiempo_ejecucion + (1 - alpha) * tiempo_promedio_anterior
                )
        
        return nuevas_metricas
    
    def _actualizar_estadisticas(self, estadisticas_actuales: Dict, resultado: Dict) -> Dict:
        """Actualiza las estadísticas de uso de la habilidad"""
        nuevas_estadisticas = estadisticas_actuales.copy()
        
        # Contadores básicos
        nuevas_estadisticas['total_ejecuciones'] = nuevas_estadisticas.get('total_ejecuciones', 0) + 1
        if resultado.get('exito'):
            nuevas_estadisticas['ejecuciones_exitosas'] = nuevas_estadisticas.get('ejecuciones_exitosas', 0) + 1
        else:
            nuevas_estadisticas['ejecuciones_fallidas'] = nuevas_estadisticas.get('ejecuciones_fallidas', 0) + 1
        
        # Última ejecución
        nuevas_estadisticas['ultima_ejecucion'] = datetime.now().isoformat()
        
        return nuevas_estadisticas
    
    async def obtener_metricas_consolidadas(self, dias: int = 30) -> Dict[str, Any]:
        """
        Obtiene métricas consolidadas de todas las habilidades.
        
        Args:
            dias: Número de días hacia atrás para consolidar
        
        Returns:
            Dict: Métricas consolidadas
        """
        # Obtener todas las habilidades
        todas_habilidades = await self.base.obtener_todas_habilidades()
        
        metricas_consolidadas = {
            'total_habilidades': len(todas_habilidades),
            'habilidades_activas': 0,
            'tasa_exito_promedio': 0.0,
            'tiempo_ejecucion_promedio': 0.0,
            'ejecuciones_totales': 0,
            'por_categoria': {},
            'por_tipo': {}
        }
        
        for habilidad in todas_habilidades:
            metricas = habilidad.get('metricas_rendimiento', {})
            stats = habilidad.get('estadisticas_uso', {})
            
            # Contar habilidades activas (usadas recientemente)
            ultima_ejecucion = stats.get('ultima_ejecucion')
            if ultima_ejecucion:
                ultima_fecha = datetime.fromisoformat(ultima_ejecucion.replace('Z', '+00:00'))
                if (datetime.now() - ultima_fecha) < timedelta(days=dias):
                    metricas_consolidadas['habilidades_activas'] += 1
            
            # Acumular métricas
            metricas_consolidadas['tasa_exito_promedio'] += metricas.get('tasa_exito', 0)
            metricas_consolidadas['tiempo_ejecucion_promedio'] += metricas.get('tiempo_promedio', 0)
            metricas_consolidadas['ejecuciones_totales'] += stats.get('total_ejecuciones', 0)
            
            # Por categoría
            for categoria in habilidad.get('categorias', ['general']):
                if categoria not in metricas_consolidadas['por_categoria']:
                    metricas_consolidadas['por_categoria'][categoria] = {
                        'count': 0, 'tasa_exito': 0.0, 'tiempo_promedio': 0.0
                    }
                metricas_consolidadas['por_categoria'][categoria]['count'] += 1
                metricas_consolidadas['por_categoria'][categoria]['tasa_exito'] += metricas.get('tasa_exito', 0)
                metricas_consolidadas['por_categoria'][categoria]['tiempo_promedio'] += metricas.get('tiempo_promedio', 0)
            
            # Por tipo
            tipo = habilidad.get('tipo', 'procedimiento')
            if tipo not in metricas_consolidadas['por_tipo']:
                metricas_consolidadas['por_tipo'][tipo] = {
                    'count': 0, 'tasa_exito': 0.0, 'tiempo_promedio': 0.0
                }
            metricas_consolidadas['por_tipo'][tipo]['count'] += 1
            metricas_consolidadas['por_tipo'][tipo]['tasa_exito'] += metricas.get('tasa_exito', 0)
            metricas_consolidadas['por_tipo'][tipo]['tiempo_promedio'] += metricas.get('tiempo_promedio', 0)
        
        # Calcular promedios
        if metricas_consolidadas['total_habilidades'] > 0:
            metricas_consolidadas['tasa_exito_promedio'] /= metricas_consolidadas['total_habilidades']
            metricas_consolidadas['tiempo_ejecucion_promedio'] /= metricas_consolidadas['total_habilidades']
        
        return metricas_consolidadas