from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from loguru import logger
from datetime import datetime

class DetectorPatrones:
    """Sistema de detección de patrones para creación automática de habilidades"""
    
    def __init__(self, config_patrones: Dict[str, Any]):
        self.config = config_patrones
        self.umbral_similitud = config_patrones.get('umbral_similitud', 0.8)
        self.min_muestras = config_patrones.get('min_muestras', 5)
    
    async def detectar_patrones_ejecucion(self, df_episodios: pd.DataFrame) -> Dict[str, Any]:
        """
        Detecta patrones recurrentes en la ejecución de tareas para crear nuevas habilidades.
        
        Args:
            df_episodios: DataFrame con datos de episodios para análisis
        
        Returns:
            Dict: Patrones detectados y habilidades recomendadas
        """
        try:
            # 1. Extraer secuencias de ejecución exitosas
            secuencias_exitosas = self._extraer_secuencias_exitosas(df_episodios)
            
            if not secuencias_exitosas:
                return {'patrones_detectados': 0, 'habilidades_recomendadas': []}
            
            # 2. Clusterizar secuencias similares
            clusters = self._clusterizar_secuencias(secuencias_exitosas)
            
            # 3. Generar habilidades para clusters significativos
            habilidades = self._generar_habilidades_desde_clusters(clusters)
            
            return {
                'patrones_detectados': len(clusters),
                'total_secuencias': len(secuencias_exitosas),
                'habilidades_recomendadas': habilidades,
                'detalles_clusters': clusters
            }
            
        except Exception as e:
            logger.error(f"Error en detección de patrones: {e}")
            return {'error': str(e)}
    
    def _extraer_secuencias_exitosas(self, df: pd.DataFrame) -> List[List[Dict]]:
        """Extrae secuencias de tareas de episodios exitosos"""
        secuencias = []
        
        for _, episodio in df[df['exito_global'] > 0.7].iterrows():
            # Reconstruir la secuencia de tareas del episodio
            tareas_episodio = []
            
            for col in df.columns:
                if col.startswith('tarea_') and col.endswith('_herramienta'):
                    tarea_id = col.split('_')[1]
                    
                    if pd.notna(episodio[col]):
                        tarea = {
                            'id': tarea_id,
                            'herramienta': episodio[col],
                            'exito': episodio.get(f'tarea_{tarea_id}_exito', False),
                            'duracion': episodio.get(f'tarea_{tarea_id}_duracion', 0)
                        }
                        tareas_episodio.append(tarea)
            
            # Ordenar tareas por algún criterio (ej: orden de ejecución)
            tareas_episodio.sort(key=lambda x: x['id'])
            
            if tareas_episodio:
                secuencias.append(tareas_episodio)
        
        return secuencias
    
    def _clusterizar_secuencias(self, secuencias: List[List[Dict]]) -> Dict[int, List[List[Dict]]]:
        """Agrupa secuencias similares usando algoritmos de clustering"""
        # Convertir secuencias a vectores para clustering
        vectores = self._secuencias_a_vectores(secuencias)
        
        if len(vectores) < self.min_muestras:
            return {}
        
        # Usar DBSCAN para encontrar clusters de secuencias similares
        clustering = DBSCAN(eps=0.5, min_samples=self.min_muestras).fit(vectores)
        
        clusters = {}
        for i, etiqueta in enumerate(clustering.labels_):
            if etiqueta != -1:  # Ignorar outliers
                if etiqueta not in clusters:
                    clusters[etiqueta] = []
                clusters[etiqueta].append(secuencias[i])
        
        return clusters
    
    def _secuencias_a_vectores(self, secuencias: List[List[Dict]]) -> np.ndarray:
        """Convierte secuencias de tareas en vectores para clustering"""
        # Extraer todas las herramientas únicas
        herramientas_unicas = set()
        for secuencia in secuencias:
            for tarea in secuencia:
                herramientas_unicas.add(tarea['herramienta'])
        
        herramientas_lista = sorted(herramientas_unicas)
        vectores = []
        
        for secuencia in secuencias:
            vector = [0] * len(herramientas_lista)
            for tarea in secuencia:
                if tarea['herramienta'] in herramientas_lista:
                    idx = herramientas_lista.index(tarea['herramienta'])
                    vector[idx] += 1  # Contar frecuencia de herramienta
            
            vectores.append(vector)
        
        return np.array(vectores)
    
    def _generar_habilidades_desde_clusters(self, clusters: Dict[int, List[List[Dict]]]) -> List[Dict]:
        """Genera habilidades a partir de clusters de secuencias similares"""
        habilidades = []
        
        for cluster_id, secuencias_cluster in clusters.items():
            if len(secuencias_cluster) >= self.min_muestras:
                # Extraer patrón común del cluster
                patron_comun = self._extraer_patron_comun(secuencias_cluster)
                
                # Crear definición de habilidad
                habilidad = {
                    'nombre': f"habilidad_auto_{cluster_id}_{int(datetime.now().timestamp())}",
                    'tipo': 'procedimiento_autogenerado',
                    'patron_ejecucion': patron_comun,
                    'secuencia_recomendada': self._generar_secuencia_optimizada(secuencias_cluster),
                    'estadisticas': {
                        'tasa_exito_promedio': self._calcular_tasa_exito(secuencias_cluster),
                        'duracion_promedio': self._calcular_duracion_promedio(secuencias_cluster),
                        'numero_muestras': len(secuencias_cluster)
                    },
                    'metadata': {
                        'fecha_creacion': datetime.now().isoformat(),
                        'origen': 'auto_generado',
                        'cluster_id': cluster_id
                    }
                }
                
                habilidades.append(habilidad)
        
        return habilidades
    
    def _extraer_patron_comun(self, secuencias: List[List[Dict]]) -> List[Dict]:
        """Extrae el patrón común de un conjunto de secuencias"""
        if not secuencias:
            return []
        
        # Encontrar la secuencia más representativa (la de longitud media)
        longitudes = [len(seq) for seq in secuencias]
        longitud_media = int(np.mean(longitudes))
        
        secuencias_filtradas = [seq for seq in secuencias if len(seq) == longitud_media]
        
        if not secuencias_filtradas:
            # Tomar la secuencia más común si no hay de longitud exacta
            secuencias_filtradas = [max(secuencias, key=lambda x: len(x))]
        
        # Para simplificar, tomamos la primera secuencia del mismo tamaño
        return secuencias_filtradas[0]