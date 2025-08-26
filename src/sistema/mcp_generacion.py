from typing import Dict, List, Any
import json
import re
from datetime import datetime
from loguru import logger

class GeneradorPlanes:
    """Clase especializada en la generación de nuevos planes desde cero"""
    
    def __init__(self, cliente_llm, configuracion: Dict[str, Any]):
        self.llm = cliente_llm
        self.config = configuracion
        self.prompt_templates = self._cargar_templates()
    
    def _cargar_templates(self) -> Dict[str, str]:
        """Carga las plantillas de prompts para generación de planes"""
        return {
            "planificacion_base": """
Eres un planificador experto de tareas. Tu objetivo es descomponer el siguiente objetivo en una secuencia lógica de tareas ejecutables.

OBJETIVO: {objetivo}
CONTEXTO: {contexto}

INSTRUCCIONES:
1. Analiza el objetivo y descomponlo en tareas específicas y accionables
2. Estima el orden lógico de ejecución
3. Para cada tarea, especifica:
   - Descripción clara
   - Tipo de tarea (buscar, generar, analizar, etc.)
   - Herramienta recomendada
   - Parámetros necesarios
   - Dependencias de otras tareas
   - Duración estimada

Formato de salida JSON:
{{
  "objetivo": "string",
  "tareas": [
    {{
      "id": "string",
      "descripcion": "string",
      "tipo": "string",
      "herramienta": "string",
      "parametros": {{}},
      "dependencias": ["string"],
      "estimacion_duracion": number
    }}
  ],
  "requisitos_recursos": ["string"],
  "restricciones": ["string"]
}}

Responde ÚNICAMENTE con el JSON válido.
"""
        }
    
    def generar_nuevo_plan(self, objetivo: str, contexto: Dict = None) -> Dict[str, Any]:
        """Genera un nuevo plan desde cero usando el LLM"""
        try:
            prompt = self.prompt_templates["planificacion_base"].format(
                objetivo=objetivo,
                contexto=json.dumps(contexto or {}, ensure_ascii=False)
            )
            
            respuesta = self.llm.generar(
                prompt,
                temperatura=0.1,
                max_tokens=2000
            )
            
            plan_json = self._extraer_json_respuesta(respuesta)
            plan_validado = self._validar_estructura_plan(plan_json)
            
            plan_validado['metadata'] = {
                'origen': 'generado_nuevo',
                'modelo_utilizado': self.llm.model_name,
                'timestamp_generacion': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            return plan_validado
            
        except Exception as e:
            logger.error(f"Error generando nuevo plan: {e}")
            raise
    
    def _extraer_json_respuesta(self, respuesta: str) -> Dict:
        """Extrae el JSON de la respuesta del LLM"""
        json_pattern = r'```json\s*(\{.*?\})\s*```'
        match = re.search(json_pattern, respuesta, re.DOTALL)
        
        if match:
            json_str = match.group(1)
        else:
            json_pattern = r'(\{.*\})'
            match = re.search(json_pattern, respuesta, re.DOTALL)
            if match:
                json_str = match.group(1)
            else:
                raise ValueError("No se encontró JSON válido en la respuesta")
        
        return json.loads(json_str)
    
    def _validar_estructura_plan(self, plan: Dict) -> Dict:
        """Valida y completa la estructura del plan"""
        if 'tareas' not in plan or not isinstance(plan['tareas'], list):
            raise ValueError("Estructura de plan inválida: falta lista de tareas")
        
        for i, tarea in enumerate(plan['tareas']):
            if 'id' not in tarea:
                tarea['id'] = f"tarea_{i+1:03d}"
            
            tarea.setdefault('dependencias', [])
            tarea.setdefault('parametros', {})
            tarea.setdefault('estimacion_duracion', 60)
        
        return plan