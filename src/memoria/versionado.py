from typing import Dict, List, Any, Optional
from datetime import datetime
from loguru import logger

class GestorVersionado:
    """
    Sistema de gestión de versiones para habilidades de la base de conocimiento.
    Permite el control de cambios y el mantenimiento de historial.
    """
    
    def __init__(self, base_conocimiento, configuracion: Dict[str, Any]):
        self.base = base_conocimiento
        self.config = configuracion
        
    async def crear_version(self, habilidad: Dict, cambios: Dict) -> str:
        """
        Crea una nueva versión de una habilidad.
        
        Args:
            habilidad: Habilidad existente
            cambios: Cambios aplicados a la habilidad
        
        Returns:
            str: ID de la nueva versión
        """
        # Crear nueva versión basada en la existente
        nueva_version = self._aumentar_version(habilidad)
        nueva_version.update(cambios)
        nueva_version['fecha_actualizacion'] = datetime.now().isoformat()
        
        # Guardar nueva versión
        nueva_id = await self.base.guardar_habilidad(nueva_version)
        
        # Mantener referencia a versión anterior
        await self._registrar_relacion_version(
            nueva_id, 
            habilidad.get('id'), 
            'version_anterior'
        )
        
        logger.info(f"Nueva versión creada: {nueva_id} para habilidad {habilidad.get('nombre')}")
        return nueva_id
    
    def _aumentar_version(self, habilidad: Dict) -> Dict:
        """Aumenta el número de versión de una habilidad"""
        version_actual = habilidad.get('version', '1.0.0')
        
        # Lógica simple de aumento de versión (major.minor.patch)
        partes = version_actual.split('.')
        if len(partes) == 3:
            partes[2] = str(int(partes[2]) + 1)  # Aumentar patch version
        nueva_version = '.'.join(partes)
        
        nueva_habilidad = habilidad.copy()
        nueva_habilidad['version'] = nueva_version
        return nueva_habilidad
    
    async def obtener_historial_versions(self, habilidad_id: str) -> List[Dict]:
        """
        Obtiene el historial de versiones de una habilidad.
        
        Args:
            habilidad_id: ID de la habilidad
        
        Returns:
            List[Dict]: Historial de versiones ordenado cronológicamente
        """
        # Buscar relaciones de versionado
        relaciones = await self.base.obtener_relaciones(
            habilidad_id, 
            tipo_relacion='version_anterior'
        )
        
        historial = []
        current_id = habilidad_id
        
        while current_id:
            # Obtener habilidad actual
            habilidad = await self.base.obtener_habilidad(current_id)
            if habilidad:
                historial.append({
                    'id': current_id,
                    'version': habilidad.get('version', ''),
                    'fecha_actualizacion': habilidad.get('fecha_actualizacion', ''),
                    'cambios': habilidad.get('cambios_descripcion', '')
                })
            
            # Buscar versión anterior
            current_id = next((
                rel['origen'] for rel in relaciones 
                if rel['destino'] == current_id and rel['tipo'] == 'version_anterior'
            ), None)
        
        return historial[::-1]  # Devolver en orden cronológico