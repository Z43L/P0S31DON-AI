from typing import Dict, List, Any, Optional
import re
from loguru import logger

class DetectorAmbiguedades:
    """Sistema de detección de ambigüedades y información faltante en objetivos"""
    
    def __init__(self, configuracion: Dict[str, Any]):
        self.config = configuracion
        self.patrones_ambiguedad = self._cargar_patrones_ambiguedad()
    
    async def detectar_ambiguedades(self, objetivo: str, contexto: Dict = None) -> Dict[str, Any]:
        """
        Detecta ambigüedades e información faltante en un objetivo del usuario.
        
        Args:
            objetivo: Objetivo expresado por el usuario
            contexto: Contexto adicional del diálogo
        
        Returns:
            Dict: Ambigüedades detectadas y preguntas de clarificación sugeridas
        """
        ambiguedades = []
        
        # Detectar ambigüedades mediante patrones
        ambiguedades_patrones = self._detectar_por_patrones(objetivo)
        ambiguedades.extend(ambiguedades_patrones)
        
        # Detectar información faltante basada en el tipo de objetivo
        info_faltante = self._detectar_informacion_faltante(objetivo, contexto)
        ambiguedades.extend(info_faltante)
        
        return {
            'ambiguedades': ambiguedades,
            'necesita_clarificacion': len(ambiguedades) > 0,
            'preguntas_clarificacion': self._generar_preguntas_clarificacion(ambiguedades)
        }
    
    def _detectar_por_patrones(self, texto: str) -> List[Dict]:
        """Detecta ambigüedades usando patrones predefinidos"""
        detecciones = []
        texto_lower = texto.lower()
        
        patrones = {
            'termino_ambiguo': r'\b(it|eso|eso|aquello|ell[oa]s?)\b',
            'cuantificador_vago': r'\b(algo|algun[oa]?|varios|much[oa]s?|poc[oa]s?)\b',
            'temporalidad_imprecisa': r'\b(pronto|luego|después|más tarde|en breve)\b',
            'comparativo_ambiguo': r'\b(más|menos|mejor|peor|más rápido|más barato)\b'
        }
        
        for tipo, patron in patrones.items():
            if re.search(patron, texto_lower):
                detecciones.append({
                    'tipo': tipo,
                    'patron': patron,
                    'severidad': 'media',
                    'mensaje': f'Se detectó un {tipo.replace("_", " ")} en el objetivo'
                })
        
        return detecciones
    
    def _generar_preguntas_clarificacion(self, ambiguedades: List[Dict]) -> List[str]:
        """Genera preguntas de clarificación basadas en las ambigüedades detectadas"""
        preguntas = []
        mapeo_preguntas = {
            'termino_ambiguo': "¿A qué se refiere específicamente con '{}'?",
            'cuantificador_vago': "¿Podría especificar la cantidad exacta o el rango?",
            'temporalidad_imprecisa': "¿Hay una fecha límite específica o marco temporal?",
            'comparativo_ambiguo': "¿Comparado con qué o según qué criterio?",
            'informacion_faltante': "¿Podría proporcionar más detalles sobre {}?"
        }
        
        for ambiguedad in ambiguedades:
            tipo = ambiguedad['tipo']
            if tipo in mapeo_preguntas:
                preguntas.append(mapeo_preguntas[tipo])
        
        return list(set(preguntas))  # Eliminar duplicados