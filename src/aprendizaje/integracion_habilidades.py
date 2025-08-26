from typing import Dict, List, Any, Optional
from loguru import logger

class GestorIntegracionHabilidades:
    """Gestor para la integración de nuevas habilidades en el sistema"""
    
    def __init__(self, sistema_memoria, configuracion: Dict[str, Any]):
        self.memoria = sistema_memoria
        self.config = configuracion
    
    async def integrar_habilidad(self, habilidad: Dict, metricas_calidad: Dict) -> Dict[str, Any]:
        """
        Integra una nueva habilidad en el sistema de conocimiento.
        
        Args:
            habilidad: Habilidad a integrar
            metricas_calidad: Métricas de calidad de la generalización
        
        Returns:
            Dict: Resultado de la integración
        """
        try:
            # Verificar calidad mínima
            if not metricas_calidad.get('calidad_suficiente', False):
                logger.warning(f"Habilidad {habilidad.get('nombre')} no cumple calidad mínima")
                return {'exito': False, 'razon': 'calidad_insuficiente'}
            
            # Verificar si ya existe habilidad similar
            habilidades_similares = await self._buscar_habilidades_similares(habilidad)
            if habilidades_similares:
                # Decidir si reemplazar o mantener ambas
                decision = await self._decidir_reemplazo(habilidad, habilidades_similares, metricas_calidad)
                if decision['accion'] == 'reemplazar':
                    await self._reemplazar_habilidad(decision['habilidad_existente'], habilidad)
                    return {'exito': True, 'accion': 'reemplazada', 'id_existente': decision['habilidad_existente']}
                elif decision['accion'] == 'mantener_ambas':
                    # Continuar con inserción normal
                    pass
            
            # Almacenar nueva habilidad
            habilidad_id = await self.memoria.guardar_habilidad(habilidad)
            
            # Actualizar índices y relaciones
            await self._actualizar_indices(habilidad_id, habilidad)
            
            logger.info(f"Habilidad integrada: {habilidad_id} - {habilidad.get('nombre')}")
            return {'exito': True, 'accion': 'creada', 'habilidad_id': habilidad_id}
            
        except Exception as e:
            logger.error(f"Error integrando habilidad: {e}")
            return {'exito': False, 'error': str(e)}
    
    async def _buscar_habilidades_similares(self, habilidad: Dict) -> List[Dict]:
        """Busca habilidades existentes similares a la nueva"""
        # Búsqueda por nombre y características similares
        habilidades_similares = []
        
        # Buscar por nombre (similitud semántica)
        try:
            resultados = await self.memoria.buscar_habilidades(
                habilidad.get('nombre', ''),
                filtros={'tipo': 'procedimiento'},
                limite=5
            )
            
            for resultado in resultados:
                if self._son_habilidades_similares(habilidad, resultado['habilidad']):
                    habilidades_similares.append(resultado['habilidad'])
                    
        except Exception as e:
            logger.warning(f"Error buscando habilidades similares: {e}")
        
        return habilidades_similares
    
    def _son_habilidades_similares(self, habilidad1: Dict, habilidad2: Dict) -> bool:
        """Determina si dos habilidades son lo suficientemente similares"""
        # Comparar based en nombre, estructura y objetivos
        similitud_nombre = self._calcular_similitud_texto(
            habilidad1.get('nombre', ''), 
            habilidad2.get('nombre', '')
        )
        
        # Otras comparaciones de estructura...
        return similitud_nombre > 0.7  # Umbral configurable