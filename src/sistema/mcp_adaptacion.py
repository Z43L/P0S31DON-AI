from typing import Dict, List, Any
import json
import re
from datetime import datetime
from loguru import logger

class AdaptadorPlanes:
    """Clase especializada en adaptar planes existentes a nuevos objetivos"""
    
    def __init__(self, cliente_llm, configuracion: Dict[str, Any]):
        self.llm = cliente_llm
        self.config = configuracion
        self.prompt_templates = self._cargar_templates()
    
    def _cargar_templates(self) -> Dict[str, str]:
        """Carga las plantillas de prompts para adaptación de planes"""
        return {
            "adaptacion_plan": """
Eres un experto en adaptar planes existentes a nuevos objetivos. 
Tu tarea es modificar el plan existente para adecuarlo al nuevo objetivo.

PLAN ORIGINAL:
{plan_existente}

NUEVO OBJETIVO:
{nuevo_objetivo}

CONTEXTO:
{contexto}

INSTRUCCIONES:
1. Mantén la estructura y mejores prácticas del plan original
2. Adapta las tareas al nuevo objetivo específico
3. Ajusta parámetros, dependencias y secuencia según sea necesario
4. Conserva los metadatos importantes del plan original

Formato de salida JSON (misma estructura que el plan original):
{estructura_json}

Responde ÚNICAMENTE con el JSON válido del plan adaptado.
"""
        }
    
    def adaptar_plan_existente(self, plan_existente: Dict, nuevo_objetivo: str, 
                              contexto: Dict = None) -> Dict[str, Any]:
        """Adapta un plan existente a un nuevo objetivo"""
        try:
            prompt = self.prompt_templates["adaptacion_plan"].format(
                plan_existente=json.dumps(plan_existente, ensure_ascii=False, indent=2),
                nuevo_objetivo=nuevo_objetivo,
                contexto=json.dumps(contexto or {}, ensure_ascii=False),
                estructura_json=json.dumps({
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
                    "metadata": {
                        "origen": "adaptado",
                        "plan_base": "string",
                        "adaptaciones": ["string"]
                    }
                }, indent=2)
            )
            
            respuesta = self.llm.generar(
                prompt,
                temperatura=0.1,
                max_tokens=2500
            )
            
            plan_adaptado_json = self._extraer_json_respuesta(respuesta)
            plan_validado = self._validar_plan_adaptado(plan_adaptado_json, plan_existente)
            
            if 'metadata' not in plan_validado:
                plan_validado['metadata'] = {}
            
            plan_validado['metadata'].update({
                'origen': 'adaptado',
                'plan_base': plan_existente.get('metadata', {}).get('origen', 'desconocido'),
                'timestamp_adaptacion': datetime.now().isoformat(),
                'modelo_adaptacion': self.llm.model_name
            })
            
            return plan_validado
            
        except Exception as e:
            logger.error(f"Error adaptando plan existente: {e}")
            raise
    
    def _validar_plan_adaptado(self, plan_adaptado: Dict, plan_original: Dict) -> Dict:
        """Valida que el plan adaptado mantenga la estructura del original"""
        if 'tareas' not in plan_adaptado:
            raise ValueError("Plan adaptado no contiene tareas")
        
        estructura_original = set(plan_original.keys())
        estructura_adaptada = set(plan_adaptado.keys())
        
        if not estructura_original.issubset(estructura_adaptada):
            logger.warning("Plan adaptado no mantiene toda la estructura original")
        
        return plan_adaptado