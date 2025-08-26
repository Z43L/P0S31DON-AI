from typing import Dict, List, Any, Optional
import time
from datetime import datetime
import psutil
from loguru import logger

class MonitorEjecucion:
    """Sistema de monitorización en tiempo real de la ejecución de tareas"""
    
    def __init__(self, configuracion: Dict[str, Any]):
        self.config = configuracion
        self.metricas_tiempo_real = {
            'tareas_activas': 0,
            'uso_cpu': 0.0,
            'uso_memoria': 0.0,
            'latencia_promedio': 0.0
        }
        self.historial_metricas = []
        
    async def iniciar_monitorizacion(self):
        """Inicia la monitorización continua en segundo plano"""
        import asyncio
        
        while True:
            try:
                await self._actualizar_metricas()
                await asyncio.sleep(self.config.get('intervalo_monitoreo', 5))
            except Exception as e:
                logger.error(f"Error en monitorización: {e}")
                await asyncio.sleep(30)
    
    async def _actualizar_metricas(self):
        """Actualiza las métricas del sistema"""
        self.metricas_tiempo_real.update({
            'timestamp': datetime.now(),
            'tareas_activas': self._contar_tareas_activas(),
            'uso_cpu': psutil.cpu_percent(),
            'uso_memoria': psutil.virtual_memory().percent,
            'latencia_promedio': self._calcular_latencia_promedio()
        })
        
        # Guardar en historial
        self.historial_metricas.append(self.metricas_tiempo_real.copy())
        
        # Limitar tamaño del historial
        if len(self.historial_metricas) > self.config.get('max_historial', 1000):
            self.historial_metricas = self.historial_metricas[-1000:]
    
    def _contar_tareas_activas(self) -> int:
        """Cuenta las tareas activas en el sistema"""
        # Implementación específica depende del tracking de tareas
        return 0  # Placeholder
    
    def _calcular_latencia_promedio(self) -> float:
        """Calcula la latencia promedio de ejecución"""
        # Implementación específica depende del tracking de tareas
        return 0.0  # Placeholder
    
    def obtener_estado_sistema(self) -> Dict[str, Any]:
        """Obtiene el estado actual del sistema"""
        return {
            **self.metricas_tiempo_real,
            'estado': self._determinar_estado_sistema(),
            'alertas_activas': self._verificar_alertas()
        }
    
    def _determinar_estado_sistema(self) -> str:
        """Determina el estado general del sistema"""
        if self.metricas_tiempo_real['uso_cpu'] > 90:
            return 'critico'
        elif self.metricas_tiempo_real['uso_memoria'] > 85:
            return 'alerta'
        elif self.metricas_tiempo_real['tareas_activas'] > 100:
            return 'sobrecarga'
        else:
            return 'normal'
    
    def _verificar_alertas(self) -> List[Dict]:
        """Verifica y genera alertas del sistema"""
        alertas = []
        
        if self.metricas_tiempo_real['uso_cpu'] > 90:
            alertas.append({
                'nivel': 'critico',
                'mensaje': 'Uso de CPU crítico',
                'metricas': {'uso_cpu': self.metricas_tiempo_real['uso_cpu']}
            })
        
        if self.metricas_tiempo_real['uso_memoria'] > 85:
            alertas.append({
                'nivel': 'alerta',
                'mensaje': 'Uso de memoria alto',
                'metricas': {'uso_memoria': self.metricas_tiempo_real['uso_memoria']}
            })
        
        return alertas