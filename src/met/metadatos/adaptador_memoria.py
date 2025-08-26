from typing import Dict, List, Any, Optional
from datetime import datetime
from loguru import logger

class AdaptadorMemoriaMetadatos:
    """Adaptador para almacenamiento de metadatos en el Sistema de Memoria de Triple Capa"""
    
    def __init__(self, sistema_memoria, configuracion: Dict[str, Any]):
        self.memoria = sistema_memoria
        self.config = configuracion
    
    async def guardar_metadatos(self, metadatos: Dict) -> str:
        """
        Almacena metadatos en las diferentes capas de memoria.
        
        Args:
            metadatos: Metadatos a almacenar
        
        Returns:
            str: ID del registro creado
        """
        try:
            # 1. Almacenar en Memoria Episódica (capa 3)
            episodio_id = await self._guardar_en_memoria_episodica(metadatos)
            
            # 2. Almacenar en Base de Conocimiento (capa 2) si es exitoso
            if metadatos.get('exito') and metadatos.get('estado') == 'exito':
                await self._extraer_a_base_conocimiento(metadatos)
            
            # 3. Mantener en Memoria de Trabajo (capa 1) temporalmente
            await self._mantener_en_memoria_trabajo(metadatos, episodio_id)
            
            return episodio_id
            
        except Exception as e:
            logger.error(f"Error almacenando metadatos: {e}")
            raise
    
    async def _guardar_en_memoria_episodica(self, metadatos: Dict) -> str:
        """Almacena metadatos en la memoria episódica"""
        episodio = {
            'tipo': 'ejecucion_tarea',
            'timestamp': datetime.now().isoformat(),
            'objetivo': f"Ejecución de tarea {metadatos.get('tarea_id')}",
            'plan_ejecutado': {
                'tarea_id': metadatos.get('tarea_id'),
                'herramienta': metadatos.get('herramienta_utilizada'),
                'parametros': metadatos.get('parametros_ejecucion', {})
            },
            'resultados': {
                'exito': metadatos.get('exito', False),
                'estado': metadatos.get('estado', 'desconocido'),
                'duracion': metadatos.get('duracion_segundos', 0),
                'resultado': metadatos.get('resultado')
            },
            'metricas': {
                'rendimiento': metadatos.get('metricas_rendimiento', {}),
                'eficiencia': metadatos.get('metricas_eficiencia', {}),
                'calidad': metadatos.get('metricas_calidad', {})
            },
            'diagnostico': metadatos.get('diagnostico', {})
        }
        
        return await self.memoria.guardar_episodio(episodio)
    
    async def _extraer_a_base_conocimiento(self, metadatos: Dict):
        """Extrae conocimiento a la base de conocimiento"""
        conocimiento = {
            'tipo': 'patron_ejecucion',
            'tarea_id': metadatos.get('tarea_id'),
            'tipo_tarea': metadatos.get('tipo_tarea'),
            'herramienta': metadatos.get('herramienta_utilizada'),
            'parametros_optimos': metadatos.get('parametros_ejecucion', {}),
            'metricas_rendimiento': metadatos.get('metricas_rendimiento', {}),
            'timestamp': datetime.now().isoformat(),
            'numero_ejecuciones': 1,
            'tasa_exito': 1.0
        }
        
        await self.memoria.guardar_habilidad(conocimiento)
    
    async def _mantener_en_memoria_trabajo(self, metadatos: Dict, episodio_id: str):
        """Mantiene referencia en memoria de trabajo"""
        clave = f"metadatos_{metadatos.get('tarea_id')}"
        valor = {
            'episodio_id': episodio_id,
            'timestamp': datetime.now().isoformat(),
            'estado': metadatos.get('estado'),
            'resumen': self._generar_resumen(metadatos)
        }
        
        await self.memoria.guardar_contexto(clave, valor, expiration=3600)  # 1 hora