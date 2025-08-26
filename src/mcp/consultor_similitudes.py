from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from datetime import datetime
from loguru import logger

class ConsultorSimilitudes:
    """Sistema principal de consulta de similitudes para la Base de Conocimiento"""
    
    def __init__(self, cliente_embedding, sistema_memoria, configuracion: Dict[str, Any]):
        self.embedding = cliente_embedding
        self.memoria = sistema_memoria
        self.config = configuracion
        self.umbral_similitud = configuracion.get('umbral_similitud', 0.7)
        
        logger.info("Consultor de Similitudes inicializado correctamente")
    
    async def buscar_planes_similares(self, objetivo: Dict, limite: int = 5) -> List[Dict[str, Any]]:
        """
        Busca planes similares en la Base de Conocimiento basado en el objetivo proporcionado.
        
        Args:
            objetivo: Objetivo procesado y enriquecido
            limite: Número máximo de resultados a retornar
        
        Returns:
            List[Dict]: Lista de planes similares ordenados por relevancia
        """
        try:
            # 1. Generar representación vectorial del objetivo
            embedding_objetivo = await self._generar_embedding_objetivo(objetivo)
            
            # 2. Búsqueda por similitud semántica
            resultados_semanticos = await self._buscar_similitud_semantica(
                embedding_objetivo, limite * 2
            )
            
            # 3. Búsqueda por similitud estructural
            resultados_estructurales = await self._buscar_similitud_estructural(
                objetivo, limite * 2
            )
            
            # 4. Fusionar y rerankear resultados
            resultados_combinados = self._fusionar_resultados(
                resultados_semanticos, resultados_estructurales
            )
            
            # 5. Filtrar y limitar resultados
            resultados_filtrados = self._filtrar_resultados(resultados_combinados, limite)
            
            logger.info(f"Encontrados {len(resultados_filtrados)} planes similares")
            return resultados_filtrados
            
        except Exception as e:
            logger.error(f"Error en búsqueda de similitudes: {e}")
            return []
    
    async def _generar_embedding_objetivo(self, objetivo: Dict) -> np.ndarray:
        """Genera la representación vectorial del objetivo para búsqueda semántica"""
        texto_embedding = f"{objetivo['texto_procesado']} {objetivo['tipo']}"
        
        if objetivo.get('entidades'):
            texto_embedding += " " + " ".join(
                f"{k}:{v}" for k, v in objetivo['entidades'].items()
            )
        
        return await self.embedding.generar_embedding(texto_embedding)