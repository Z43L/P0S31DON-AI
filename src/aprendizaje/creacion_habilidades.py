from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib
from loguru import logger
import numpy as np

class GeneradorHabilidades:
    """Sistema de creación y formalización de habilidades estructuradas"""
    
    def __init__(self, configuracion: Dict[str, Any]):
        self.config = configuracion
    
    async def crear_habilidad_estructurada(self, procedimiento_abstracto: Dict, 
                                           episodios_base: List[Dict]) -> Dict[str, Any]:
        """
        Crea una habilidad estructurada a partir de un procedimiento abstractado.
        
        Args:
            procedimiento_abstracto: Procedimiento generalizado
            episodios_base: Episodios utilizados para la generalización
        
        Returns:
            Dict: Habilidad estructurada lista para almacenamiento
        """
        try:
            # Construir la estructura completa de la habilidad
            habilidad = {
                # Identificación y metadata
                'id': self._generar_id_habilidad(procedimiento_abstracto),
                'nombre': procedimiento_abstracto.get('nombre', ''),
                'tipo': 'procedimiento_generalizado',
                'version': '1.0.0',
                
                # Descripción y contexto
                'descripcion': procedimiento_abstracto.get('descripcion', ''),
                'objetivos': self._extraer_objetivos(episodios_base),
                'categorias': self._inferir_categorias(procedimiento_abstracto),
                
                # Contenido procedural
                'procedimiento': procedimiento_abstracto.get('procedimiento', []),
                'precondiciones': procedimiento_abstracto.get('precondiciones', []),
                'parametros': procedimiento_abstracto.get('parametros_generalizados', {}),
                
                # Información de rendimiento
                'metricas_rendimiento': self._calcular_metricas_base(episodios_base),
                'estadisticas_uso': {
                    'veces_utilizada': 0,
                    'tasa_exito': self._calcular_tasa_exito_base(episodios_base),
                    'episodios_base': len(episodios_base)
                },
                
                # Control de versiones y procedencia
                'fecha_creacion': datetime.now().isoformat(),
                'fecha_actualizacion': datetime.now().isoformat(),
                'autor': 'sistema_autoaprendizaje',
                'episodios_referencia': [e['id'] for e in episodios_base],
                
                # Configuración de ejecución
                'timeout_estimado': self._calcular_timeout_estimado(episodios_base),
                'recursos_estimados': self._estimar_recursos(episodios_base)
            }
            
            # Validar habilidad antes de retornar
            if self._validar_habilidad(habilidad):
                return habilidad
            else:
                raise ValueError("Habilidad no válida")
                
        except Exception as e:
            logger.error(f"Error creando habilidad: {e}")
            raise
    
    def _generar_id_habilidad(self, procedimiento: Dict) -> str:
        """Genera un ID único para la habilidad"""
        contenido = f"{procedimiento.get('nombre', '')}{datetime.now().timestamp()}"
        hash_id = hashlib.md5(contenido.encode()).hexdigest()[:12]
        return f"habilidad_{hash_id}"
    
    def _calcular_metricas_base(self, episodios: List[Dict]) -> Dict[str, float]:
        """Calcula métricas de rendimiento basado en episodios de referencia"""
        if not episodios:
            return {}
        
        duraciones = [e.get('duracion_total_segundos', 0) for e in episodios]
        exitos = [1 for e in episodios if e.get('estado_global') == 'exito']
        
        return {
            'duracion_promedio': np.mean(duraciones) if duraciones else 0,
            'duracion_std': np.std(duraciones) if len(duraciones) > 1 else 0,
            'tasa_exito': len(exitos) / len(episodios) if episodios else 0,
            'eficiencia_promedio': self._calcular_eficiencia_promedio(episodios)
        }
    
    def _validar_habilidad(self, habilidad: Dict) -> bool:
        """Valida que la habilidad cumpla con los requisitos mínimos"""
        requisitos = [
            ('id', str),
            ('nombre', str),
            ('procedimiento', list),
            ('metricas_rendimiento', dict),
            ('estadisticas_uso', dict)
        ]
        
        for campo, tipo in requisitos:
            if campo not in habilidad or not isinstance(habilidad[campo], tipo):
                logger.warning(f"Habilidad inválida: falta o tipo incorrecto para {campo}")
                return False
        
        # Validar procedimiento no vacío
        if len(habilidad['procedimiento']) == 0:
            logger.warning("Habilidad inválida: procedimiento vacío")
            return False
        
        return True