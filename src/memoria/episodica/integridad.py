from typing import Dict, List, Any, Optional
import hashlib
from loguru import logger

class ValidadorIntegridad:
    """Sistema de validación de integridad para episodios"""
    
    def __init__(self, configuracion: Dict[str, Any]):
        self.config = configuracion
        
    async def validar_episodio(self, episodio: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida la integridad y consistencia de un episodio.
        
        Args:
            episodio: Episodio a validar
        
        Returns:
            Dict: Resultado de la validación
        """
        resultados = {
            'integro': True,
            'errores': [],
            'advertencias': []
        }
        
        # Validar checksum
        if not self._validar_checksum(episodio):
            resultados['integro'] = False
            resultados['errores'].append('Checksum de integridad inválido')
        
        # Validar estructura requerida
        campos_requeridos = ['id', 'objetivo', 'plan_ejecutado', 'resultados_tareas']
        for campo in campos_requeridos:
            if campo not in episodio:
                resultados['integro'] = False
                resultados['errores'].append(f'Campo requerido faltante: {campo}')
        
        # Validar consistencia temporal
        if not self._validar_consistencia_temporal(episodio):
            resultados['advertencias'].append('Inconsistencias temporales detectadas')
        
        # Validar formato de IDs
        if not self._validar_formato_id(episodio.get('id', '')):
            resultados['errores'].append('Formato de ID inválido')
        
        logger.debug(f"Validación de episodio {episodio.get('id')}: {resultados['integro']}")
        return resultados
    
    def _validar_checksum(self, episodio: Dict) -> bool:
        """Valida el checksum de integridad del episodio"""
        checksum_calculado = self._calcular_checksum(episodio)
        checksum_almacenado = episodio.get('checksum_integridad', '')
        return checksum_calculado == checksum_almacenado
    
    def _calcular_checksum(self, episodio: Dict) -> str:
        """Calcula el checksum de integridad"""
        contenido = (
            f"{episodio.get('objetivo', '')}"
            f"{episodio.get('timestamp_inicio', '')}"
            f"{episodio.get('timestamp_fin', '')}"
            f"{episodio.get('version_sistema', '')}"
        )
        return hashlib.sha256(contenido.encode()).hexdigest()
    
    def _validar_consistencia_temporal(self, episodio: Dict) -> bool:
        """Valida la consistencia temporal del episodio"""
        inicio = episodio.get('timestamp_inicio')
        fin = episodio.get('timestamp_fin')
        duracion = episodio.get('duracion_total_segundos', 0)
        
        if not inicio or not fin:
            return False
        
        # Verificar que fin sea después de inicio
        if fin <= inicio:
            return False
        
        # Verificar que la duración coincida con los timestamps
        duracion_calculada = (fin - inicio).total_seconds()
        return abs(duracion_calculada - duracion) < 1.0  # Tolerancia de 1 segundo
    
    def _validar_formato_id(self, episodio_id: str) -> bool:
        """Valida el formato del ID del episodio"""
        return episodio_id.startswith('episodio_') and len(episodio_id) > 20