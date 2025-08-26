from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from loguru import logger

class MonitorRendimientoHerramientas:
    """Sistema de monitorización continua del rendimiento de herramientas"""
    
    def __init__(self, configuracion: Dict[str, Any]):
        self.config = configuracion
        self.metricas_historico: Dict[str, Any] = {}
        self.alertas_activas: List[Dict] = []
        
    async def monitorear_rendimiento_continuo(self):
        """Ejecuta monitorización continua en segundo plano"""
        import asyncio
        
        intervalo = self.config.get('intervalo_monitoreo', 300)  # 5 minutos
        
        while True:
            try:
                await self._ejecutar_ciclo_monitoreo()
                await asyncio.sleep(intervalo)
            except Exception as e:
                logger.error(f"Error en monitorización: {e}")
                await asyncio.sleep(60)  # Reintentar después de 1 minuto
    
    async def _ejecutar_ciclo_monitoreo(self):
        """Ejecuta un ciclo completo de monitorización"""
        # Obtener episodios recientes
        episodios_recientes = await self._obtener_episodios_recientes()
        
        # Analizar rendimiento
        metricas = await self._analizar_rendimiento_herramientas(episodios_recientes)
        
        # Verificar alertas
        alertas = self._verificar_alertas(metricas)
        
        # Registrar resultados
        await self._registrar_metricas(metricas)
        
        if alertas:
            await self._procesar_alertas(alertas)
    
    def _verificar_alertas(self, metricas: Dict) -> List[Dict]:
        """Verifica condiciones de alerta en las métricas"""
        alertas = []
        
        for tipo_tarea, herramientas in metricas.items():
            for herramienta, datos in herramientas.items():
                # Alerta por degradación de rendimiento
                if (datos.get('tasa_exito', 1.0) < self.config.get('umbral_alerta_exito', 0.6)):
                    alertas.append({
                        'tipo': 'degradacion_rendimiento',
                        'nivel': 'alto',
                        'mensaje': f"{herramienta} para {tipo_tarea} tiene tasa de éxito baja: {datos['tasa_exito']:.3f}",
                        'herramienta': herramienta,
                        'tipo_tarea': tipo_tarea,
                        'metricas': datos
                    })
                
                # Alerta por aumento de latencia
                tiempo_actual = datos.get('tiempo_promedio', 0)
                tiempo_historico = self._obtener_tiempo_historico(tipo_tarea, herramienta)
                
                if tiempo_historico and tiempo_actual > tiempo_historico * 1.5:  # 50% más lento
                    alertas.append({
                        'tipo': 'aumento_latencia',
                        'nivel': 'medio',
                        'mensaje': f"{herramienta} para {tipo_tarea} es {tiempo_actual/tiempo_historico:.1f}x más lenta",
                        'herramienta': herramienta,
                        'tipo_tarea': tipo_tarea,
                        'metricas': datos
                    })
        
        return alertas