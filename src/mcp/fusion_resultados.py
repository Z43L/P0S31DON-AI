from typing import Dict, List, Any, Optional
import numpy as np
from loguru import logger

class FusionadorResultados:
    """Sistema de fusión y reranking de resultados de búsquedas múltiples"""
    
    def __init__(self, configuracion: Dict[str, Any]):
        self.config = configuracion
        self.peso_semantico = configuracion.get('peso_semantico', 0.6)
        self.peso_estructural = configuracion.get('peso_estructural', 0.4)
    
    def fusionar_resultados(self, resultados_semanticos: List[Dict], 
                          resultados_estructurales: List[Dict]) -> List[Dict]:
        """
        Fusiona resultados de búsquedas semánticas y estructurales con reranking.
        
        Args:
            resultados_semanticos: Resultados de búsqueda semántica
            resultados_estructurales: Resultados de búsqueda estructural
        
        Returns:
            List[Dict]: Resultados fusionados y rerankeado
        """
        try:
            # Crear diccionario unificado de resultados
            resultados_unificados = {}
            
            # Procesar resultados semánticos
            for resultado in resultados_semanticos:
                plan_id = resultado['plan'].get('id')
                if plan_id:
                    resultados_unificados[plan_id] = {
                        'plan': resultado['plan'],
                        'score_semantico': resultado['similitud'],
                        'score_estructural': 0.0,
                        'score_combinado': resultado['similitud'] * self.peso_semantico
                    }
            
            # Procesar resultados estructurales y combinar
            for resultado in resultados_estructurales:
                plan_id = resultado['plan'].get('id')
                if plan_id in resultados_unificados:
                    # Plan ya existe, actualizar score estructural
                    resultados_unificados[plan_id]['score_estructural'] = resultado['similitud_estructural']
                    resultados_unificados[plan_id]['score_combinado'] += (
                        resultado['similitud_estructural'] * self.peso_estructural
                    )
                else:
                    # Nuevo plan, agregar al diccionario
                    resultados_unificados[plan_id] = {
                        'plan': resultado['plan'],
                        'score_semantico': 0.0,
                        'score_estructural': resultado['similitud_estructural'],
                        'score_combinado': resultado['similitud_estructural'] * self.peso_estructural
                    }
            
            # Convertir a lista y ordenar por score combinado
            resultados_fusionados = list(resultados_unificados.values())
            resultados_ordenados = sorted(
                resultados_fusionados,
                key=lambda x: x['score_combinado'],
                reverse=True
            )
            
            return resultados_ordenados
            
        except Exception as e:
            logger.error(f"Error en fusión de resultados: {e}")
            return []