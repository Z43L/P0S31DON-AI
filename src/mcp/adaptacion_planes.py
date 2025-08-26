from typing import Dict, List, Any, Optional
from loguru import logger
import json

class AdaptadorPlanes:
    """Sistema de adaptación de planes similares para nuevos objetivos"""
    
    def __init__(self, cliente_llm, configuracion: Dict[str, Any]):
        self.llm = cliente_llm
        self.config = configuracion
    
    async def adaptar_plan(self, plan_base: Dict, objetivo_nuevo: Dict) -> Dict[str, Any]:
        """
        Adapta un plan existente a un nuevo objetivo específico.
        
        Args:
            plan_base: Plan base de la base de conocimiento
            objetivo_nuevo: Nuevo objetivo a planificar
        
        Returns:
            Dict: Plan adaptado al nuevo objetivo
        """
        try:
            # 1. Análisis de diferencias entre objetivos
            diferencias = await self._analizar_diferencias(plan_base, objetivo_nuevo)
            
            # 2. Generar plan adaptado
            if diferencias['similitud'] > 0.8:
                # Alta similitud - adaptación mínima
                plan_adaptado = await self._adaptacion_minima(plan_base, objetivo_nuevo, diferencias)
            else:
                # Baja similitud - adaptación significativa
                plan_adaptado = await self._adaptacion_significativa(plan_base, objetivo_nuevo, diferencias)
            
            # 3. Validar plan adaptado
            plan_validado = await self._validar_plan_adaptado(plan_adaptado)
            
            return {
                **plan_validado,
                'metadatos': {
                    'origen': 'adaptado',
                    'plan_base': plan_base.get('id'),
                    'similitud_original': diferencias['similitud'],
                    'adaptaciones_realizadas': diferencias['puntos_diferencia']
                }
            }
            
        except Exception as e:
            logger.error(f"Error adaptando plan: {e}")
            raise
    
    async def _analizar_diferencias(self, plan_base: Dict, objetivo_nuevo: Dict) -> Dict[str, Any]:
        """Analiza las diferencias entre el plan base y el nuevo objetivo"""
        prompt = f"""
Analiza las diferencias entre el plan base y el nuevo objetivo:

PLAN BASE:
{json.dumps(plan_base['objetivo'], ensure_ascii=False)}

NUEVO OBJETIVO:
{json.dumps(objetivo_nuevo, ensure_ascii=False)}

Identifica:
1. Similitud general (0-1)
2. Puntos específicos de diferencia
3. Elementos que necesitan adaptación

Responde en formato JSON.
"""
        
        respuesta = await self.llm.generar(prompt, temperatura=0.1, max_tokens=500)
        return json.loads(respuesta)