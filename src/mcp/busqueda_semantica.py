from typing import Dict, List, Any, Optional
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from loguru import logger

class BuscadorSemantico:
    """Sistema de búsqueda por similitud semántica utilizando embeddings"""
    
    def __init__(self, sistema_memoria, configuracion: Dict[str, Any]):
        self.memoria = sistema_memoria
        self.config = configuracion
    
    async def buscar_similares_semanticos(self, embedding_consulta: np.ndarray, 
                                        limite: int = 10) -> List[Dict[str, Any]]:
        """
        Busca planes similares basado en similitud coseno entre embeddings.
        
        Args:
            embedding_consulta: Vector de embedding del objetivo de consulta
            limite: Número máximo de resultados
        
        Returns:
            List[Dict]: Resultados de búsqueda semántica
        """
        try:
            # Obtener todos los embeddings de planes de la base de conocimiento
            planes_con_embedding = self.memoria.obtener_planes_con_embedding()
            
            if not planes_con_embedding:
                return []
            
            # Calcular similitudes
            similitudes = self._calcular_similitudes(embedding_consulta, planes_con_embedding)
            
            # Ordenar por similitud y filtrar
            resultados_ordenados = sorted(
                zip(planes_con_embedding, similitudes),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Aplicar umbral de similitud
            resultados_filtrados = [
                {'plan': plan, 'similitud': similitud}
                for plan, similitud in resultados_ordenados
                if similitud >= self.config.get('umbral_similitud', 0.6)
            ]
            
            return resultados_filtrados[:limite]
            
        except Exception as e:
            logger.error(f"Error en búsqueda semántica: {e}")
            return []
    
    def _calcular_similitudes(self, embedding_consulta: np.ndarray, 
                            planes: List[Dict]) -> List[float]:
        """Calcula similitudes coseno entre el embedding de consulta y los planes"""
        embeddings_planes = []
        planes_validos = []
        
        for plan in planes:
            if 'embedding' in plan and plan['embedding'] is not None:
                embeddings_planes.append(plan['embedding'])
                planes_validos.append(plan)
        
        if not embeddings_planes:
            return []
        
        # Calcular similitud coseno
        similitudes = cosine_similarity(
            [embedding_consulta],
            embeddings_planes
        )[0]
        
        return similitudes.tolist()