from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from loguru import logger

class RegistradorMetadatos:
    """Sistema de registro y almacenamiento de metadatos de ejecución"""
    
    def __init__(self, sistema_memoria, configuracion: Dict[str, Any]):
        self.memoria = sistema_memoria
        self.config = configuracion
        self.buffer_metadatos = []
        self.tamano_buffer = configuracion.get('tamano_buffer', 100)
        
    async def registrar_metadatos(self, metadatos: Dict, almacenamiento_inmediato: bool = False) -> str:
        """
        Registra metadatos de ejecución en el sistema de memoria.
        
        Args:
            metadatos: Metadatos a registrar
            almacenamiento_inmediato: Si debe almacenarse inmediatamente
        
        Returns:
            str: ID del registro creado
        """
        try:
            # Enriquecer metadatos con información adicional
            metadatos_completos = self._enriquecer_metadatos(metadatos)
            
            if almacenamiento_inmediato:
                # Almacenamiento inmediato
                registro_id = await self._almacenar_directo(metadatos_completos)
            else:
                # Almacenamiento en buffer para procesamiento por lotes
                self.buffer_metadatos.append(metadatos_completos)
                registro_id = f"buffered_{len(self.buffer_metadatos)}"
                
                # Verificar si el buffer está lleno
                if len(self.buffer_metadatos) >= self.tamano_buffer:
                    await self._procesar_buffer()
            
            logger.info(f"Metadatos registrados: {registro_id}")
            return registro_id
            
        except Exception as e:
            logger.error(f"Error registrando metadatos: {e}")
            return f"error_{datetime.now().timestamp()}"
    
    async def _almacenar_directo(self, metadatos: Dict) -> str:
        """Almacena metadatos directamente en la memoria"""
        # Almacenar en memoria episódica
        registro_id = await self.memoria.guardar_episodio(metadatos)
        
        # Almacenar en base de conocimiento si la ejecución fue exitosa
        if metadatos.get('estado') == 'exito':
            await self._extraer_conocimiento(metadatos)
        
        return registro_id
    
    async def _procesar_buffer(self):
        """Procesa el buffer de metadatos pendientes"""
        if not self.buffer_metadatos:
            return
        
        try:
            # Almacenar todos los metadatos del buffer
            for metadatos in self.buffer_metadatos:
                await self._almacenar_directo(metadatos)
            
            # Limpiar buffer
            self.buffer_metadatos.clear()
            
            logger.info(f"Buffer de metadatos procesado: {len(self.buffer_metadatos)} registros")
            
        except Exception as e:
            logger.error(f"Error procesando buffer: {e}")
    
    def _enriquecer_metadatos(self, metadatos: Dict) -> Dict[str, Any]:
        """Enriquece los metadatos con información adicional"""
        timestamp = datetime.now()
        
        metadatos_enriquecidos = {
            **metadatos,
            'version_metadatos': '1.0',
            'timestamp_registro': timestamp.isoformat(),
            'hash_ejecucion': self._generar_hash_ejecucion(metadatos),
            'contexto_global': self._capturar_contexto_global()
        }
        
        return metadatos_enriquecidos
    
    async def _extraer_conocimiento(self, metadatos: Dict):
        """Extrae conocimiento de metadatos de ejecuciones exitosas"""
        if metadatos.get('estado') != 'exito':
            return
        
        # Extraer patrones de ejecución exitosa
        patron = {
            'tipo_tarea': metadatos.get('tipo_tarea'),
            'herramienta': metadatos.get('herramienta_utilizada'),
            'parametros_optimos': metadatos.get('parametros_ejecucion', {}),
            'duracion_promedio': metadatos.get('duracion_segundos', 0),
            'metricas_rendimiento': {
                k: v for k, v in metadatos.items() 
                if k.startswith('rendimiento_') or k.startswith('eficiencia_')
            },
            'numero_muestras': 1
        }
        
        # Guardar en base de conocimiento
        await self.memoria.guardar_habilidad(patron)