from typing import Dict, List, Any, Optional
import re
from loguru import logger

class AnalizadorIntencion:
    """Sistema de análisis de intención y extracción de entidades del usuario"""
    
    def __init__(self, cliente_llm, configuracion: Dict[str, Any]):
        self.llm = cliente_llm
        self.config = configuracion
        self.patrones_intencion = self._cargar_patrones()
    
    async def analizar_mensaje(self, mensaje: str) -> Dict[str, Any]:
        """
        Analiza un mensaje del usuario para determinar intención y extraer entidades.
        
        Args:
            mensaje: Texto de entrada del usuario
        
        Returns:
            Dict: Análisis estructurado de intención y entidades
        """
        # Análisis con patrones predefinidos para intenciones comunes
        analisis_patrones = self._analizar_con_patrones(mensaje)
        
        # Si los patrones no son suficientes, usar LLM para análisis profundo
        if analisis_patrones['confianza'] < 0.7:
            analisis_llm = await self._analizar_con_llm(mensaje)
            return {**analisis_patrones, **analisis_llm}
        
        return analisis_patrones
    
    def _analizar_con_patrones(self, mensaje: str) -> Dict[str, Any]:
        """Análisis basado en patrones predefinidos para intenciones comunes"""
        mensaje_lower = mensaje.lower()
        intenciones_detectadas = []
        
        for intencion, patrones in self.patrones_intencion.items():
            for patron in patrones:
                if re.search(patron, mensaje_lower):
                    intenciones_detectadas.append({
                        'intencion': intencion,
                        'confianza': 0.8,
                        'patron_coincidente': patron
                    })
        
        return {
            'intenciones': intenciones_detectadas,
            'confianza': max([i['confianza'] for i in intenciones_detectadas]) if intenciones_detectadas else 0.0,
            'necesita_clarificacion': len(intenciones_detectadas) != 1
        }
    
    async def _analizar_con_llm(self, mensaje: str) -> Dict[str, Any]:
        """Análisis de intención usando LLM para casos complejos"""
        prompt = f"""
Analiza la siguiente solicitud del usuario e identifica:
1. Intención principal (qué quiere lograr)
2. Entidades clave (qué, quién, cuándo, dónde)
3. Ambigüedades o información faltante

Solicitud: "{mensaje}"

Responde en formato JSON:
{{
  "intencion_principal": "string",
  "entidades": {{
    "que": ["string"],
    "quien": ["string"],
    "cuando": ["string"],
    "donde": ["string"]
  }},
  "ambigüedades": ["string"],
  "informacion_faltante": ["string"],
  "confianza": 0.0
}}
"""
        try:
            respuesta = await self.llm.generar(prompt, temperatura=0.1, max_tokens=500)
            return self._parsear_respuesta_llm(respuesta)
        except Exception as e:
            logger.error(f"Error en análisis con LLM: {e}")
            return {'intenciones': [], 'confianza': 0.0, 'necesita_clarificacion': True}