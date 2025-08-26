from typing import Dict, List, Any, Optional
from loguru import logger

# Importar o definir DescomposicionHabilidades y DescomposicionRazonamiento
from mcp.descomposicion_habilidades import DescomposicionHabilidades
from mcp.descomposicion_razonamiento import DescomposicionRazonamiento

class EstrategiaHibrida:
    """Estrategia híbrida que combina múltiples enfoques de descomposición"""
    
    def __init__(self, cliente_llm, sistema_memoria, configuracion: Dict[str, Any]):
        self.llm = cliente_llm
        self.memoria = sistema_memoria
        self.config = configuracion
        
        # Inicializar componentes de estrategias
        self.descomposicion_habilidades = DescomposicionHabilidades(cliente_llm, sistema_memoria, configuracion)
        self.descomposicion_razonamiento = DescomposicionRazonamiento(cliente_llm, configuracion)
    
    async def descomponer_hibrido(self, objetivo: Dict) -> Dict[str, Any]:
        """
        Estrategia híbrida que combina habilidades existentes con razonamiento.
        
        Args:
            objetivo: Objetivo procesado y enriquecido
        
        Returns:
            Dict: Plan generado por estrategia híbrida
        """
        try:
            # 1. Intentar con habilidades existentes primero
            try:
                plan_habilidades = await self.descomposicion_habilidades.descomponer_con_habilidades(objetivo)
                if plan_habilidades['metadatos']['confianza'] > 0.8:
                    return plan_habilidades
            except Exception as e:
                logger.info(f"Habilidades no aplicables, intentando razonamiento: {e}")
            
            # 2. Usar razonamiento para componentes faltantes
            plan_razonamiento = await self.descomposicion_razonamiento.descomponer_por_razonamiento(objetivo)
            
            # 3. Combinar y optimizar
            plan_combinado = await self._combinar_planes(plan_habilidades, plan_razonamiento)
            
            return {
                **plan_combinado,
                'metadatos': {
                    'estrategia': 'hibrida',
                    'confianza': max(
                        plan_habilidades.get('metadatos', {}).get('confianza', 0),
                        plan_razonamiento.get('metadatos', {}).get('confianza', 0)
                    )
                }
            }
            
        except Exception as e:
            logger.error(f"Error en estrategia híbrida: {e}")
            raise
    
    async def _combinar_planes(self, plan_habilidades: Dict, plan_razonamiento: Dict) -> Dict:
        """Combina planes de diferentes estrategias"""
        # Implementación de combinación inteligente de planes
        tareas_combinadas = []
        
        # Agregar tareas de habilidades con alta confianza
        if plan_habilidades and 'tareas' in plan_habilidades:
            tareas_combinadas.extend(plan_habilidades['tareas'])
        
        # Agregar tareas de razonamiento que no estén cubiertas
        if plan_razonamiento and 'tareas' in plan_razonamiento:
            for tarea in plan_razonamiento['tareas']:
                if not self._tarea_existe(tarea, tareas_combinadas):
                    tareas_combinadas.append(tarea)
        
        return {
            'objetivo': plan_razonamiento['objetivo'],
            'tareas': tareas_combinadas,
            'requisitos_recursos': list(set(
                plan_habilidades.get('requisitos_recursos', []) +
                plan_razonamiento.get('requisitos_recursos', [])
            )),
            'restricciones': list(set(
                plan_habilidades.get('restricciones', []) +
                plan_razonamiento.get('restricciones', [])
            ))
        }