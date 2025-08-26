from typing import Dict, List, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from loguru import logger

class BuscadorEstructural:
    """Sistema de búsqueda por similitud estructural basado en características de planes"""
    
    def __init__(self, sistema_memoria, configuracion: Dict[str, Any]):
        self.memoria = sistema_memoria
        self.config = configuracion
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
    
    async def buscar_similares_estructurales(self, objetivo: Dict, 
                                           limite: int = 10) -> List[Dict[str, Any]]:
        """
        Busca planes similares basado en similitud estructural y patrones.
        
        Args:
            objetivo: Objetivo de consulta con características estructurales
            limite: Número máximo de resultados
        
        Returns:
            List[Dict]: Resultados de búsqueda estructural
        """
        try:
            # Obtener planes para análisis estructural
            planes = self.memoria.obtener_todos_planes()
            
            if not planes:
                return []
            
            # Extraer características estructurales
            caracteristicas_planes = self._extraer_caracteristicas_estructurales(planes)
            caracteristicas_objetivo = self._extraer_caracteristicas_objetivo(objetivo)
            
            # Calcular similitudes estructurales
            similitudes = self._calcular_similitud_estructural(
                caracteristicas_objetivo, caracteristicas_planes
            )
            
            # Combinar resultados
            resultados = []
            for i, similitud in enumerate(similitudes):
                if similitud >= self.config.get('umbral_estructural', 0.5):
                    resultados.append({
                        'plan': planes[i],
                        'similitud_estructural': similitud,
                        'tipo_similitud': 'estructural'
                    })
            
            # Ordenar y limitar resultados
            resultados_ordenados = sorted(
                resultados,
                key=lambda x: x['similitud_estructural'],
                reverse=True
            )
            
            return resultados_ordenados[:limite]
            
        except Exception as e:
            logger.error(f"Error en búsqueda estructural: {e}")
            return []
    
    def _extraer_caracteristicas_estructurales(self, planes: List[Dict]) -> List[str]:
        """Extrae características estructurales de los planes para análisis"""
        caracteristicas = []
        
        for plan in planes:
            # Características basadas en la estructura del plan
            num_tareas = len(plan.get('tareas', []))
            tipos_tareas = set(tarea.get('tipo', '') for tarea in plan.get('tareas', []))
            herramientas = set(tarea.get('herramienta', '') for tarea in plan.get('tareas', []))
            
            carac_texto = f"tareas_{num_tareas} tipos_{'_'.join(sorted(tipos_tareas))} herramientas_{'_'.join(sorted(herramientas))}"
            caracteristicas.append(carac_texto)
        
        return caracteristicas
    
    def _calcular_similitud_estructural(self, caracteristicas_objetivo: str, 
                                      caracteristicas_planes: List[str]) -> List[float]:
        """Calcula similitudes estructurales usando TF-IDF y coseno"""
        # Ajustar el vectorizer con todas las características
        todas_caracteristicas = [caracteristicas_objetivo] + caracteristicas_planes
        matriz_tfidf = self.vectorizer.fit_transform(todas_caracteristicas)
        
        # Calcular similitud entre la consulta y cada plan
        similitudes = cosine_similarity(
            matriz_tfidf[0:1],
            matriz_tfidf[1:]
        )[0]
        
        return similitudes