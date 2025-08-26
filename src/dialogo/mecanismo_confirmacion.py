from typing import Dict, List, Any, Optional
from loguru import logger
import json

class MecanismoConfirmacion:
    """Sistema de confirmación y validación de objetivos con el usuario"""
    
    def __init__(self, cliente_llm, configuracion: Dict[str, Any]):
        self.llm = cliente_llm
        self.config = configuracion
    
    async def generar_confirmacion(self, objetivo: Dict, contexto: Dict) -> Dict[str, Any]:
        """
        Genera una solicitud de confirmación para un objetivo estructurado.
        
        Args:
            objetivo: Objetivo estructurado a confirmar
            contexto: Contexto del diálogo
        
        Returns:
            Dict: Solicitud de confirmación estructurada
        """
        try:
            # Generar resumen comprensible del objetivo
            resumen = await self._generar_resumen_confirmacion(objetivo)
            
            return {
                'tipo': 'confirmacion',
                'objetivo_id': objetivo.get('id'),
                'mensaje': f"¿He entendido correctamente que desea: {resumen}?",
                'opciones': [
                    {'valor': 'si', 'texto': 'Sí, proceder'},
                    {'valor': 'no', 'texto': 'No, corregir'},
                    {'valor': 'modificar', 'texto': 'Modificar detalles'}
                ],
                'detalles_objetivo': objetivo
            }
            
        except Exception as e:
            logger.error(f"Error generando confirmación: {e}")
            return {
                'tipo': 'confirmacion',
                'mensaje': "¿Desea que proceda con la tarea solicitada?",
                'opciones': ['Sí', 'No']
            }
    
    async def _generar_resumen_confirmacion(self, objetivo: Dict) -> str:
        """Genera un resumen comprensible del objetivo para confirmación"""
        prompt = f"""
Genera un resumen claro y natural en español del siguiente objetivo para confirmación con el usuario:

OBJETIVO: {json.dumps(objetivo, ensure_ascii=False)}

El resumen debe ser:
1. En lenguaje natural y coloquial
2. Incluir todos los elementos clave
3. Ser conciso pero completo
4. En forma de pregunta confirmatoria

Responde ÚNICAMENTE con el texto del resumen.
"""
        
        respuesta = await self.llm.generar(prompt, temperatura=0.3, max_tokens=200)
        return respuesta.strip()
    
    async def procesar_respuesta_confirmacion(self, respuesta_usuario: str, objetivo: Dict) -> Dict[str, Any]:
        """
        Procesa la respuesta del usuario a una solicitud de confirmación.
        
        Args:
            respuesta_usuario: Respuesta del usuario
            objetivo: Objetivo que se estaba confirmando
        
        Returns:
            Dict: Resultado del procesamiento y siguientes pasos
        """
        analisis = await self._analizar_respuesta_confirmacion(respuesta_usuario)
        
        if analisis['confirmado']:
            return {
                'estado': 'confirmado',
                'accion': 'proceder',
                'objetivo': objetivo
            }
        elif analisis['necesita_modificacion']:
            return {
                'estado': 'modificacion',
                'puntos_modificacion': analisis['puntos_modificacion'],
                'accion': 'solicitar_modificaciones'
            }
        else:
            return {
                'estado': 'rechazado',
                'accion': 'solicitar_nuevo_objetivo'
            }