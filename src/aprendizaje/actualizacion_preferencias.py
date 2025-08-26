from typing import Dict, List, Any, Optional
from datetime import datetime
from loguru import logger

class ActualizadorPreferencias:
    """Sistema de actualización y gestión de preferencias de herramientas"""
    
    def __init__(self, sistema_memoria, configuracion: Dict[str, Any]):
        self.memoria = sistema_memoria
        self.config = configuracion
        self.umbral_mejora = configuracion.get('umbral_mejora', 0.1)
    
    async def aplicar_optimizaciones(self, optimizaciones: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aplica las optimizaciones identificadas al sistema.
        
        Args:
            optimizaciones: Optimizaciones propuestas
        
        Returns:
            Dict: Optimizaciones aplicadas con resultados
        """
        cambios_aplicados = {}
        
        for tipo_tarea, optimizacion in optimizaciones.items():
            herramienta_actual = await self._obtener_herramienta_actual(tipo_tarea)
            herramienta_recomendada = optimizacion['herramienta_recomendada']
            
            if herramienta_actual != herramienta_recomendada:
                # Calcular mejora esperada
                mejora = self._calcular_mejora_esperada(optimizacion, herramienta_actual)
                
                if mejora >= self.umbral_mejora:
                    # Aplicar cambio
                    exito = await self._actualizar_preferencia(
                        tipo_tarea, herramienta_recomendada, optimizacion
                    )
                    
                    if exito:
                        cambios_aplicados[tipo_tarea] = {
                            'herramienta_anterior': herramienta_actual,
                            'herramienta_nueva': herramienta_recomendada,
                            'mejora_esperada': mejora,
                            'confianza': optimizacion.get('confianza', 0.5)
                        }
        
        return cambios_aplicados
    
    async def _obtener_herramienta_actual(self, tipo_tarea: str) -> Optional[str]:
        """Obtiene la herramienta actualmente preferida para un tipo de tarea"""
        try:
            preferencias = await self.memoria.obtener_preferencias_herramientas()
            return preferencias.get(tipo_tarea, {}).get('herramienta_preferida')
        except Exception as e:
            logger.warning(f"Error obteniendo preferencia actual: {e}")
            return None
    
    def _calcular_mejora_esperada(self, optimizacion: Dict, herramienta_actual: str) -> float:
        """Calcula la mejora esperada al cambiar de herramienta"""
        # Implementación simplificada - en realidad se necesitarían métricas
        # de la herramienta actual para comparación
        return optimizacion.get('metricas', {}).get('tasa_exito', 0.7) * 0.5  # Placeholder
    
    async def _actualizar_preferencia(self, tipo_tarea: str, herramienta: str, 
                                    optimizacion: Dict) -> bool:
        """Actualiza la preferencia de herramienta para un tipo de tarea"""
        try:
            preferencia = {
                'tipo_tarea': tipo_tarea,
                'herramienta_preferida': herramienta,
                'metricas_rendimiento': optimizacion.get('metricas', {}),
                'fecha_actualizacion': datetime.now().isoformat(),
                'confianza': optimizacion.get('confianza', 0.5),
                'version': '1.0'
            }
            
            await self.memoria.actualizar_preferencia_herramienta(preferencia)
            logger.info(f"Preferencia actualizada: {tipo_tarea} -> {herramienta}")
            return True
            
        except Exception as e:
            logger.error(f"Error actualizando preferencia: {e}")
            return False