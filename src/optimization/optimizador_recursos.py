from typing import Dict, List
import asyncio
import logging
from datetime import datetime, timedelta

class OptimizadorRecursos:
    """Sistema de optimización automática de recursos para SAAM"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.metricas_historico = []
        self.ajustes_aplicados = []
        
    async def iniciar_optimizacion_continua(self):
        """Inicia el proceso continuo de optimización de recursos"""
        while True:
            try:
                await self._ciclo_optimizacion()
                await asyncio.sleep(self.config['intervalo_optimizacion'])
            except Exception as e:
                logging.error(f"Error en ciclo de optimización: {e}")
                await asyncio.sleep(300)  # Reintentar después de 5 minutos
    
    async def _ciclo_optimizacion(self):
        """Ejecuta un ciclo completo de optimización"""
        # 1. Recolección de métricas
        metricas = await self._recolectar_metricas()
        
        # 2. Análisis de tendencias
        analisis = await self._analizar_tendencias(metricas)
        
        # 3. Identificación de oportunidades
        oportunidades = self._identificar_oportunidades(analisis)
        
        # 4. Aplicación de ajustes
        if oportunidades:
            resultados = await self._aplicar_ajustes(oportunidades)
            await self._registrar_resultados(resultados)
    
    async def _analizar_tendencias(self, metricas: List[Dict]) -> Dict:
        """Analiza tendencias de uso de recursos"""
        from collections import defaultdict
        import numpy as np
        
        tendencias = defaultdict(list)
        
        # Agrupar métricas por tipo y calcular tendencias
        for metrica in metricas[-24:]:  # Últimas 24 horas
            for key, value in metrica.items():
                if isinstance(value, (int, float)):
                    tendencias[key].append(value)
        
        # Calcular tendencias
        analisis = {}
        for key, values in tendencias.items():
            if len(values) >= 2:
                x = range(len(values))
                slope, intercept = np.polyfit(x, values, 1)
                analisis[key] = {
                    'tendencia': slope,
                    'valor_actual': values[-1],
                    'prediccion_24h': slope * 24 + values[-1]
                }
        
        return analisis