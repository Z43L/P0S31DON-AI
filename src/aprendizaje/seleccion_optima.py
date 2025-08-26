from typing import Dict, List, Any, Optional
import numpy as np
from scipy import stats
from loguru import logger

class IdentificadorMejoresHerramientas:
    """Sistema para identificar las herramientas óptimas para cada tipo de tarea"""
    
    def __init__(self, configuracion: Dict[str, Any]):
        self.config = configuracion
        self.umbral_significancia = configuracion.get('umbral_significancia', 0.05)
        self.min_ejecuciones = configuracion.get('min_ejecuciones', 10)
    
    def identificar_mejores_herramientas(self, metricas_herramientas: Dict) -> Dict[str, Any]:
        """
        Identifica las mejores herramientas para cada tipo de tarea.
        
        Args:
            metricas_herramientas: Métricas de rendimiento por herramienta y tipo de tarea
        
        Returns:
            Dict: Herramientas óptimas identificadas
        """
        optimizaciones = {}
        
        for tipo_tarea, herramientas_metricas in metricas_herramientas.items():
            # Filtrar herramientas con suficientes ejecuciones
            herramientas_validas = {
                h: m for h, m in herramientas_metricas.items()
                if m['ejecuciones_totales'] >= self.min_ejecuciones
            }
            
            if len(herramientas_validas) < 2:
                continue
            
            # Encontrar la mejor herramienta basado en métricas compuestas
            mejor_herramienta = self._seleccionar_mejor_herramienta(herramientas_validas)
            
            if mejor_herramienta:
                optimizaciones[tipo_tarea] = {
                    'herramienta_recomendada': mejor_herramienta,
                    'metricas': herramientas_validas[mejor_herramienta],
                    'herramientas_comparadas': list(herramientas_validas.keys()),
                    'confianza': self._calcular_confianza_seleccion(herramientas_validas, mejor_herramienta)
                }
        
        return optimizaciones
    
    def _seleccionar_mejor_herramienta(self, herramientas: Dict[str, Any]) -> Optional[str]:
        """Selecciona la mejor herramienta basado en métricas de rendimiento"""
        # Calcular puntuación para cada herramienta
        puntuaciones = {}
        
        for herramienta, metricas in herramientas.items():
            # Ponderar tasa de éxito (60%) y velocidad (40%)
            puntuacion_exito = metricas.get('tasa_exito', 0) * 0.6
            
            # Invertir y normalizar tiempo (menor tiempo = mayor puntuación)
            tiempo_promedio = metricas.get('tiempo_promedio', 0)
            if tiempo_promedio > 0:
                # Usar log para normalizar distribución
                puntuacion_tiempo = (1 / np.log1p(tiempo_promedio)) * 0.4
            else:
                puntuacion_tiempo = 0
            
            puntuaciones[herramienta] = puntuacion_exito + puntuacion_tiempo
        
        if not puntuaciones:
            return None
        
        return max(puntuaciones.items(), key=lambda x: x[1])[0]
    
    def _calcular_confianza_seleccion(self, herramientas: Dict[str, Any], mejor_herramienta: str) -> float:
        """Calcula la confianza en la selección de la mejor herramienta"""
        metricas_mejor = herramientas[mejor_herramienta]
        
        # Factores de confianza
        confianza_muestral = min(1.0, metricas_mejor['ejecuciones_totales'] / 50)  # Máx confianza en 50 ejecuciones
        consistencia = 1.0 - (metricas_mejor.get('tiempo_std', 0) / metricas_mejor.get('tiempo_promedio', 1)) if metricas_mejor.get('tiempo_promedio', 0) > 0 else 0.5
        
        return (confianza_muestral * 0.6) + (consistencia * 0.4)