from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from loguru import logger

class MonitorRendimientoHerramientas:
    """Sistema de monitorización del rendimiento de herramientas"""
    
    def __init__(self, configuracion: Dict[str, Any]):
        self.config = configuracion
        self.metricas_herramientas: Dict[str, List[Dict]] = {}
        self.alertas_activas: List[Dict] = []
        
    def registrar_ejecucion(self, nombre_herramienta: str, resultado: Dict):
        """Registra una ejecución de herramienta"""
        if nombre_herramienta not in self.metricas_herramientas:
            self.metricas_herramientas[nombre_herramienta] = []
        
        metricas = {
            'timestamp': datetime.now(),
            'exito': resultado.get('exito', False),
            'duracion': resultado.get('duracion', 0),
            'error': resultado.get('error'),
            'herramienta': nombre_herramienta
        }
        
        self.metricas_herramientas[nombre_herramienta].append(metricas)
        
        # Limitar historial
        if len(self.metricas_herramientas[nombre_herramienta]) > 1000:
            self.metricas_herramientas[nombre_herramienta] = self.metricas_herramientas[nombre_herramienta][-1000:]
        
        # Verificar alertas
        self._verificar_alertas(nombre_herramienta, metricas)
    
    def _verificar_alertas(self, nombre_herramienta: str, metricas: Dict):
        """Verifica si se deben generar alertas"""
        # Alertas de error
        if not metricas['exito']:
            self._generar_alerta({
                'tipo': 'error',
                'herramienta': nombre_herramienta,
                'mensaje': f"Error en {nombre_herramienta}: {metricas['error']}",
                'nivel': 'alto'
            })
        
        # Alertas de rendimiento
        umbral_lento = self.config.get('umbral_rendimiento_lento', 5.0)
        if metricas['duracion'] > umbral_lento:
            self._generar_alerta({
                'tipo': 'rendimiento',
                'herramienta': nombre_herramienta,
                'mensaje': f"{nombre_herramienta} lenta: {metricas['duracion']}s",
                'nivel': 'medio'
            })
    
    def _generar_alerta(self, alerta: Dict):
        """Genera una alerta"""
        alerta['timestamp'] = datetime.now()
        self.alertas_activas.append(alerta)
        logger.warning(f"ALERTA: {alerta['mensaje']}")
    
    def obtener_estadisticas(self, nombre_herramienta: str) -> Dict[str, Any]:
        """Obtiene estadísticas de una herramienta"""
        if nombre_herramienta not in self.metricas_herramientas:
            return {}
        
        ejecuciones = self.metricas_herramientas[nombre_herramienta]
        ejecuciones_recientes = [e for e in ejecuciones 
                               if datetime.now() - e['timestamp'] < timedelta(hours=24)]
        
        if not ejecuciones_recientes:
            return {}
        
        exitos = sum(1 for e in ejecuciones_recientes if e['exito'])
        total = len(ejecuciones_recientes)
        
        return {
            'tasa_exito': exitos / total if total > 0 else 0,
            'total_ejecuciones': total,
            'duracion_promedio': sum(e['duracion'] for e in ejecuciones_recientes) / total if total > 0 else 0,
            'ultima_ejecucion': max(e['timestamp'] for e in ejecuciones_recientes) if ejecuciones_recientes else None
        }