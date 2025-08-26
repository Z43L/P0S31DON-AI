from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime, timedelta
from loguru import logger

class MonitorImpactoOptimizaciones:
    """Monitor del impacto de las optimizaciones aplicadas en el sistema"""
    
    def __init__(self, sistema_memoria, config_monitor: Dict[str, Any]):
        self.memoria = sistema_memoria
        self.config = config_monitor
        self.optimizaciones_monitoreadas = {}
    
    async def monitorear_impacto(self):
        """Monitorea continuamente el impacto de las optimizaciones aplicadas"""
        import asyncio
        
        while True:
            try:
                await self._evaluar_impacto_optimizaciones()
                await asyncio.sleep(self.config.get('intervalo_monitoreo', 86400))  # 24 horas
            except Exception as e:
                logger.error(f"Error en monitoreo de impacto: {e}")
                await asyncio.sleep(3600)  # Reintentar después de 1 hora
    
    async def _evaluar_impacto_optimizaciones(self):
        """Evalúa el impacto de las optimizaciones aplicadas recientemente"""
        # Obtener optimizaciones aplicadas en los últimos días
        optimizaciones_recientes = [
            opt for opt in self.optimizaciones_monitoreadas.values()
            if opt['timestamp'] > datetime.now() - timedelta(days=7)
        ]
        
        if not optimizaciones_recientes:
            return
        
        # Obtener datos de episodios posteriores a las optimizaciones
        for optimizacion in optimizaciones_recientes:
            impacto = await self._evaluar_impacto_individual(optimizacion)
            
            if impacto:
                self._actualizar_estado_optimizacion(optimizacion['id'], impacto)
                logger.info(f"Impacto evaluado para optimización {optimizacion['id']}: {impacto}")
    
    async def _evaluar_impacto_individual(self, optimizacion: Dict) -> Optional[Dict]:
        """Evalúa el impacto individual de una optimización específica"""
        tipo_optimizacion = optimizacion.get('tipo')
        
        if tipo_optimizacion == 'preferencia_herramienta':
            return await self._evaluar_impacto_preferencia_herramienta(optimizacion)
        elif tipo_optimizacion == 'nueva_habilidad':
            return await self._evaluar_impacto_nueva_habilidad(optimizacion)
        
        return None
    
    async def _evaluar_impacto_preferencia_herramienta(self, optimizacion: Dict) -> Dict:
        """Evalúa el impacto de un cambio de preferencia de herramienta"""
        tipo_tarea = optimizacion['tipo_tarea']
        herramienta_nueva = optimizacion['herramienta']
        
        # Obtener métricas antes y después de la optimización
        metricas_antes = self._obtener_metricas_periodo(
            optimizacion['timestamp'] - timedelta(days=7),
            optimizacion['timestamp']
        )
        
        metricas_despues = self._obtener_metricas_periodo(
            optimizacion['timestamp'],
            datetime.now()
        )
        
        # Calcular diferencia de rendimiento
        diferencia_exito = metricas_despues.get('tasa_exito', 0) - metricas_antes.get('tasa_exito', 0)
        diferencia_duracion = metricas_despues.get('duracion_promedio', 0) - metricas_antes.get('duracion_promedio', 0)
        
        return {
            'tipo': 'preferencia_herramienta',
            'diferencia_exito': diferencia_exito,
            'diferencia_duracion': diferencia_duracion,
            'impacto_positivo': diferencia_exito > 0 or diferencia_duracion < 0,
            'metricas_antes': metricas_antes,
            'metricas_despues': metricas_despues
        }