from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from sklearn.cluster import DBSCAN, OPTICS
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from loguru import logger

class ClusterizadorPatrones:
    """Sistema de clusterización para identificación de patrones similares"""
    
    def __init__(self, configuracion: Dict[str, Any]):
        self.config = configuracion
        self.algortimo = configuracion.get('algoritmo_clustering', 'dbscan')
    
    def clusterizar_episodios(self, caracteristicas: List[List[float]]) -> List[int]:
        """
        Agrupa episodios basado en similitud de características.
        
        Args:
            caracteristicas: Lista de vectores de características
        
        Returns:
            List: Etiquetas de cluster para cada episodio
        """
        if len(caracteristicas) < 2:
            return [0] * len(caracteristicas)
        
        try:
            # Escalar características
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(caracteristicas)
            
            # Aplicar algoritmo de clustering
            if self.algortimo == 'dbscan':
                etiquetas = self._aplicar_dbscan(X_scaled)
            elif self.algortimo == 'optics':
                etiquetas = self._aplicar_optics(X_scaled)
            else:
                etiquetas = self._aplicar_clustering_basico(X_scaled)
            
            # Calcular métricas de calidad
            if len(set(etiquetas)) > 1:
                silueta = silhouette_score(X_scaled, etiquetas)
                logger.debug(f"Calidad de clustering: {silueta:.3f}")
            
            return etiquetas
            
        except Exception as e:
            logger.error(f"Error en clusterización: {e}")
            return [0] * len(caracteristicas)
    
    def _aplicar_dbscan(self, X: np.ndarray) -> List[int]:
        """Aplica clustering DBSCAN"""
        # Parámetros configurables
        eps = self.config.get('dbscan_eps', 0.5)
        min_samples = self.config.get('dbscan_min_samples', 2)
        
        clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(X)
        return clustering.labels_.tolist()
    
    def _aplicar_optics(self, X: np.ndarray) -> List[int]:
        """Aplica clustering OPTICS"""
        min_samples = self.config.get('optics_min_samples', 2)
        
        clustering = OPTICS(min_samples=min_samples).fit(X)
        return clustering.labels_.tolist()
    
    def _aplicar_clustering_basico(self, X: np.ndarray) -> List[int]:
        """Clustering básico cuando otros métodos fallan"""
        # Agrupar por similitud simple
        from sklearn.cluster import AgglomerativeClustering
        clustering = AgglomerativeClustering(n_clusters=min(5, len(X))).fit(X)
        return clustering.labels_.tolist()