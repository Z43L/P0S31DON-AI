from typing import Dict, List, Any
import asyncio
from datetime import datetime
from loguru import logger

class DashboardMonitorizacion:
    """
    Dashboard en tiempo real para monitorización del flujo PERA.
    """
    
    def __init__(self, configuracion: Dict[str, Any]):
        self.config = configuracion
        self.metricas_tiempo_real: Dict[str, Any] = {
            'estado_sistema': 'inicializando',
            'metricas_por_modulo': {},
            'traces_activos': 0,
            'sesiones_activas': 0,
            'ultima_actualizacion': datetime.now().isoformat()
        }
        
    async def iniciar_monitorizacion(self):
        """Inicia la monitorización continua del sistema"""
        while True:
            try:
                await self._actualizar_metricas()
                await asyncio.sleep(self.config.get('intervalo_actualizacion', 5))
            except Exception as e:
                logger.error(f"Error en monitorización: {e}")
                await asyncio.sleep(30)
    
    async def _actualizar_metricas(self):
        """Actualiza las métricas del sistema en tiempo real"""
        # Obtener métricas de cada módulo (implementación específica)
        metricas_actualizadas = {
            'estado_sistema': 'operacional',
            'metricas_por_modulo': {
                'mcp': await self._obtener_metricas_mcp(),
                'met': await self._obtener_metricas_met(),
                'sm3': await self._obtener_metricas_sm3(),
                'mao': await self._obtener_metricas_mao()
            },
            'traces_activos': len(self.tracing.traces_activos),
            'sesiones_activas': self.sm3.obtener_numero_sesiones_activas(),
            'ultima_actualizacion': datetime.now().isoformat()
        }
        
        self.metricas_tiempo_real = metricas_actualizadas
        
    def obtener_estado_sistema(self) -> Dict[str, Any]:
        """Devuelve el estado actual del sistema para el dashboard"""
        return self.metricas_tiempo_real
    
    def generar_reporte_performance(self) -> Dict[str, Any]:
        """Genera un reporte de performance del sistema"""
        return {
            'timestamp': datetime.now().isoformat(),
            'uptime': self._calcular_uptime(),
            'metricas_generales': self._calcular_metricas_generales(),
            'estado_modulos': self._obtener_estado_modulos(),
            'alertas_activas': self._obtener_alertas_activas()
        }