from typing import Dict, List, Any, Optional
from loguru import logger
import json

class IntegradorMCP:
    """Sistema de integración entre el diálogo y el Módulo de Comprensión y Planificación"""
    
    def __init__(self, modulo_mcp, configuracion: Dict[str, Any]):
        self.mcp = modulo_mcp
        self.config = configuracion
    
    async def procesar_objetivo_confimado(self, objetivo: Dict, contexto: Dict) -> Dict[str, Any]:
        """
        Procesa un objetivo confirmado por el usuario a través del MCP.
        
        Args:
            objetivo: Objetivo confirmado por el usuario
            contexto: Contexto completo del diálogo
        
        Returns:
            Dict: Resultado del procesamiento con el plan generado
        """
        try:
            # Generar plan utilizando el MCP
            plan = await self.mcp.generar_plan(
                objetivo=objetivo['descripcion'],
                contexto={
                    **contexto,
                    'objetivo_estructurado': objetivo
                }
            )
            
            # Generar resumen del plan para el usuario
            resumen_plan = await self._generar_resumen_plan(plan)
            
            return {
                'exito': True,
                'plan': plan,
                'resumen_usuario': resumen_plan,
                'siguientes_pasos': 'ejecucion'
            }
            
        except Exception as e:
            logger.error(f"Error procesando objetivo con MCP: {e}")
            return {
                'exito': False,
                'error': str(e),
                'mensaje_usuario': "Lo siento, encontré dificultades al planificar esta tarea. ¿Podría reformular el objetivo?"
            }
    
    async def _generar_resumen_plan(self, plan: Dict) -> str:
        """Genera un resumen comprensible del plan para el usuario"""
        prompt = f"""
Genera un resumen claro y amigable en español del siguiente plan de ejecución:

PLAN: {json.dumps(plan, ensure_ascii=False)}

El resumen debe:
1. Ser en lenguaje natural y coloquial
2. Explicar los pasos principales de manera concisa
3. Incluir la estimación de tiempo total si está disponible
4. Ser alentador y profesional

Responde ÚNICAMENTE con el texto del resumen.
"""
        
        respuesta = await self.llm.generar(prompt, temperatura=0.3, max_tokens=300)
        return respuesta.strip()