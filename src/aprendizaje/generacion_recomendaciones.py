from typing import Dict, List, Any, Optional
from datetime import datetime
from loguru import logger

class GeneradorRecomendaciones:
    """Sistema de generación de recomendaciones basadas en análisis de éxito/fracaso"""
    
    def __init__(self, configuracion: Dict[str, Any]):
        self.config = configuracion
        self.plantillas_recomendaciones = self._cargar_plantillas()
    
    def generar_recomendaciones(self, analisis_estadistico: Dict, 
                              factores_clave: Dict) -> List[Dict[str, Any]]:
        """
        Genera recomendaciones accionables basadas en el análisis.
        
        Args:
            analisis_estadistico: Resultados del análisis estadístico
            factores_clave: Factores identificados como importantes
        
        Returns:
            List[Dict]: Recomendaciones estructuradas
        """
        recomendaciones = []
        
        # Recomendaciones basadas en análisis estadístico
        recomendaciones.extend(self._generar_recomendaciones_estadisticas(analisis_estadistico))
        
        # Recomendaciones basadas en factores clave
        recomendaciones.extend(self._generar_recomendaciones_factores(factores_clave))
        
        # Priorizar recomendaciones
        recomendaciones_priorizadas = self._priorizar_recomendaciones(recomendaciones)
        
        return recomendaciones_priorizadas
    
    def _generar_recomendaciones_estadisticas(self, analisis: Dict) -> List[Dict]:
        """Genera recomendaciones basadas en análisis estadístico"""
        recomendaciones = []
        
        # Ejemplo: Recomendación basada en duración
        if 'duracion_total' in analisis.get('comparativas', {}):
            comp = analisis['comparativas']['duracion_total']
            if comp.get('diferencia_significativa', False):
                if comp['media_grupo1'] > comp['media_grupo2']:  # Éxitos más largos
                    recomendaciones.append({
                        'tipo': 'optimizacion_tiempo',
                        'prioridad': 'alta',
                        'mensaje': 'Las ejecuciones exitosas tienden a ser más largas. Considera aumentar los timeouts o optimizar la planificación.',
                        'evidencia': f'Diferencia media: {comp["diferencia_medias"]:.2f}s (p={comp["p_value"]:.4f})',
                        'accion': 'revisar_timeouts'
                    })
        
        # Ejemplo: Recomendación basada en número de tareas
        if 'num_tareas' in analisis.get('comparativas', {}):
            comp = analisis['comparativas']['num_tareas']
            if comp.get('diferencia_significativa', False):
                recomendaciones.append({
                    'tipo': 'optimizacion_planificacion',
                    'prioridad': 'media',
                    'mensaje': 'El número de tareas afecta significativamente el éxito. Optimiza la granularidad de la planificación.',
                    'evidencia': f'Éxitos: {comp["media_grupo1"]:.1f} tareas vs Fallos: {comp["media_grupo2"]:.1f} tareas',
                    'accion': 'optimizar_granularidad'
                })
        
        return recomendaciones
    
    def _generar_recomendaciones_factores(self, factores: Dict) -> List[Dict]:
        """Genera recomendaciones basadas en factores clave"""
        recomendaciones = []
        
        for factor, info in factores.items():
            if info.get('importancia', 0) > 0.1:  # Factores importantes
                recomendacion = self._crear_recomendacion_por_factor(factor, info)
                if recomendacion:
                    recomendaciones.append(recomendacion)
        
        return recomendaciones
    
    def _crear_recomendacion_por_factor(self, factor: str, info: Dict) -> Optional[Dict]:
        """Crea una recomendación específica para un factor"""
        # Mapeo de factores a recomendaciones
        mapeo_recomendaciones = {
            'tasa_exito_tareas': {
                'tipo': 'optimizacion_ejecucion',
                'prioridad': 'alta',
                'mensaje': 'La tasa de éxito de tareas individuales es crucial. Mejora la selección de herramientas y el manejo de errores.',
                'accion': 'mejorar_seleccion_herramientas'
            },
            'num_herramientas_unicas': {
                'tipo': 'optimizacion_recursos',
                'prioridad': 'media',
                'mensaje': 'El número de herramientas únicas utilizadas afecta el rendimiento. Considera estandarizar herramientas para tipos de tareas similares.',
                'accion': 'estandarizar_herramientas'
            },
            'duracion_total': {
                'tipo': 'optimizacion_tiempo',
                'prioridad': 'alta',
                'mensaje': 'La duración total es un factor predictivo importante. Optimiza la planificación y ejecución para reducir tiempos.',
                'accion': 'optimizar_planificacion'
            }
        }
        
        if factor in mapeo_recomendaciones:
            recomendacion = mapeo_recomendaciones[factor].copy()
            recomendacion['evidencia'] = f'Importancia del factor: {info["importancia"]:.3f} (Ranking: {info["ranking"]})'
            return recomendacion
        
        return None