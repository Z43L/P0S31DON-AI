from typing import Dict, List, Any, Optional
import json
import re
from loguru import logger

class DescomposicionRazonamiento:
    """Estrategia de descomposición mediante razonamiento con modelos de lenguaje"""
    
    def __init__(self, cliente_llm, configuracion: Dict[str, Any]):
        self.llm = cliente_llm
        self.config = configuracion
        self.prompt_templates = self._cargar_templates()
    
    async def descomponer_por_razonamiento(self, objetivo: Dict) -> Dict[str, Any]:
        """
        Descompone un objetivo mediante razonamiento analítico utilizando LLM.
        
        Args:
            objetivo: Objetivo procesado y enriquecido
        
        Returns:
            Dict: Plan generado por razonamiento analítico
        """
        try:
            # 1. Construir prompt para el LLM
            prompt = self._construir_prompt_descomposicion(objetivo)
            
            # 2. Generar descomposición con el LLM
            respuesta = await self.llm.generar(
                prompt,
                temperatura=0.1,
                max_tokens=2000
            )
            
            # 3. Parsear y validar la respuesta
            plan = self._parsear_respuesta_llm(respuesta)
            
            # 4. Enriquecer con metadatos
            plan_estructurado = self._estructurar_plan(plan, objetivo)
            
            return {
                **plan_estructurado,
                'metadatos': {
                    'estrategia': 'razonamiento_llm',
                    'modelo_utilizado': self.llm.model_name,
                    'confianza': 0.7  # Confianza base para planes generados
                }
            }
            
        except Exception as e:
            logger.error(f"Error en descomposición por razonamiento: {e}")
            raise
    
    def _construir_prompt_descomposicion(self, objetivo: Dict) -> str:
        """Construye el prompt para la descomposición mediante LLM"""
        template = self.prompt_templates['descomposicion_base']
        
        return template.format(
            objetivo_texto=objetivo['texto_procesado'],
            tipo_objetivo=objetivo['tipo'],
            entidades=json.dumps(objetivo['entidades'], ensure_ascii=False),
            contexto=json.dumps(objetivo.get('contexto', {}), ensure_ascii=False),
            formato_salida=self._obtener_formato_salida()
        )
    
    def _obtener_formato_salida(self) -> str:
        """Devuelve el formato esperado para la salida del LLM"""
        return json.dumps({
            "objetivo": "string",
            "tareas": [
                {
                    "id": "string",
                    "descripcion": "string",
                    "tipo": "string",
                    "herramienta": "string",
                    "parametros": {},
                    "dependencias": ["string"],
                    "estimacion_duracion": 60
                }
            ],
            "requisitos_recursos": ["string"],
            "restricciones": ["string"]
        }, indent=2)
    
    def _parsear_respuesta_llm(self, respuesta: str) -> Dict[str, Any]:
        """Parsea la respuesta del LLM y extrae el plan estructurado"""
        # Buscar JSON en la respuesta
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', respuesta, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Intentar encontrar JSON sin delimitadores
            json_match = re.search(r'(\{.*\})', respuesta, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                raise ValueError("No se encontró JSON válido en la respuesta")
        
        return json.loads(json_str)