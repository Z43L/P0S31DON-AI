from typing import Dict, List, Any, Optional
import psutil
from datetime import datetime
from loguru import logger

class CalculadorMetricasAvanzadas:
    """Sistema de cálculo de métricas avanzadas de ejecución"""
    
    def __init__(self, configuracion: Dict[str, Any]):
        self.config = configuracion
    
    def calcular_metricas_avanzadas(self, metadatos_basicos: Dict, 
                                 contexto_ejecucion: Dict) -> Dict[str, Any]:
        """
        Calcula métricas avanzadas de rendimiento y eficiencia.
        
        Args:
            metadatos_basicos: Metadatos básicos de la ejecución
            contexto_ejecucion: Contexto de ejecución
        
        Returns:
            Dict: Métricas avanzadas
        """
        metricas = {}
        
        # Métricas de rendimiento
        metricas.update(self._calcular_metricas_rendimiento(metadatos_basicos))
        
        # Métricas de eficiencia
        metricas.update(self._calcular_metricas_eficiencia(metadatos_basicos, contexto_ejecucion))
        
        # Métricas de calidad
        metricas.update(self._calcular_metricas_calidad(metadatos_basicos))
        
        # Métricas del sistema
        metricas.update(self._capturar_metricas_sistema())
        
        return metricas
    
    def _calcular_metricas_rendimiento(self, metadatos: Dict) -> Dict[str, Any]:
        """Calcula métricas de rendimiento de la ejecución"""
        duracion = metadatos.get('duracion_segundos', 0)
        
        return {
            'rendimiento_duracion_absoluta': duracion,
            'rendimiento_duracion_relativa': self._calcular_duracion_relativa(duracion, metadatos),
            'rendimiento_throughput': 1 / duracion if duracion > 0 else 0,
            'rendimiento_estabilidad': self._calcular_estabilidad(metadatos)
        }
    
    def _calcular_metricas_eficiencia(self, metadatos: Dict, contexto: Dict) -> Dict[str, Any]:
        """Calcula métricas de eficiencia de recursos"""
        duracion = metadatos.get('duracion_segundos', 0)
        herramienta = metadatos.get('herramienta_utilizada', '')
        
        return {
            'eficiencia_recursos_cpu': self._estimar_uso_cpu(herramienta, duracion),
            'eficiencia_recursos_memoria': self._estimar_uso_memoria(herramienta, duracion),
            'eficiencia_costo': self._calcular_costo_ejecucion(herramienta, duracion, contexto),
            'eficiencia_energetica': self._estimar_consumo_energetico(duracion)
        }
    
    def _calcular_metricas_calidad(self, metadatos: Dict) -> Dict[str, Any]:
        """Calcula métricas de calidad del resultado"""
        estado = metadatos.get('estado', '')
        exito = metadatos.get('exito', False)
        
        return {
            'calidad_resultado': 1.0 if exito else 0.0,
            'calidad_confianza': self._calcular_confianza_resultado(metadatos),
            'calidad_completitud': self._evaluar_completitud(metadatos),
            'calidad_precision': self._evaluar_precision(metadatos)
        }
    
    def _capturar_metricas_sistema(self) -> Dict[str, Any]:
        """Captura métricas del sistema durante la ejecución"""
        return {
            'sistema_cpu_porcentaje': psutil.cpu_percent(),
            'sistema_memoria_porcentaje': psutil.virtual_memory().percent,
            'sistema_disco_porcentaje': psutil.disk_usage('/').percent,
            'sistema_red_actividad': self._medir_actividad_red(),
            'sistema_timestamp_captura': datetime.now().isoformat()
        }