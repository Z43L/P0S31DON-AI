from typing import Dict, List, Any, Optional
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from loguru import logger
import json

class BuscadorConocimiento:
    """
    Sistema de búsqueda semántica para la base de conocimiento.
    Permite encontrar habilidades relevantes basado en similitud semántica.
    """
    
    def __init__(self, base_conocimiento, configuracion: Dict[str, Any]):
        self.base = base_conocimiento
        self.config = configuracion
        self.umbral_similitud = configuracion.get('umbral_similitud', 0.6)
        
    async def buscar_habilidades(self, consulta: str, filtros: Optional[Dict] = None, 
                               limite: int = 5) -> List[Dict[str, Any]]:
        """
        Busca habilidades relevantes usando similitud semántica.
        
        Args:
            consulta: Texto de consulta para búsqueda semántica
            filtros: Filtros adicionales para la búsqueda
            limite: Número máximo de resultados
        
        Returns:
            List[Dict]: Habilidades encontradas ordenadas por relevancia
        """
        try:
            # Generar embedding de la consulta
            embedding_consulta = self._generar_embedding(consulta)
            
            # Realizar búsqueda semántica
            resultados = self.base.coleccion_habilidades.query(
                query_embeddings=[embedding_consulta],
                n_results=limite * 2,  # Buscar más para luego filtrar
                where=filtros,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Procesar y filtrar resultados
            habilidades = self._procesar_resultados(resultados, limite)
            
            return habilidades
            
        except Exception as e:
            logger.error(f"Error en búsqueda de habilidades: {e}")
            return []
    
    def _procesar_resultados(self, resultados: Dict, limite: int) -> List[Dict]:
        """Procesa y filtra los resultados de la búsqueda"""
        habilidades = []
        
        for i, (doc, metadata, distancia) in enumerate(zip(
            resultados['documents'][0],
            resultados['metadatas'][0],
            resultados['distances'][0]
        )):
            # Filtrar por similitud mínima
            similitud = 1 - distancia  # Convertir distancia a similitud
            if similitud < self.umbral_similitud:
                continue
            
            try:
                habilidad = json.loads(doc)
                habilidades.append({
                    'habilidad': habilidad,
                    'metadata': metadata,
                    'similitud': similitud,
                    'id': resultados['ids'][0][i]
                })
            except json.JSONDecodeError:
                logger.warning(f"Error decodificando habilidad: {doc}")
                continue
        
        # Ordenar por similitud y limitar resultados
        habilidades.sort(key=lambda x: x['similitud'], reverse=True)
        return habilidades[:limite]
    
    async def buscar_por_tipo(self, tipo_habilidad: str, 
                            limite: int = 10) -> List[Dict[str, Any]]:
        """
        Busca habilidades por tipo específico.
        
        Args:
            tipo_habilidad: Tipo de habilidad a buscar
            limite: Número máximo de resultados
        
        Returns:
            List[Dict]: Habilidades del tipo especificado
        """
        return await self.buscar_habilidades(
            consulta=tipo_habilidad,
            filtros={"tipo": tipo_habilidad},
            limite=limite
        )