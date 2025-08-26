from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.cluster import DBSCAN
from loguru import logger

class MecanismoGeneralizacion:
    """
    Sistema principal de generalización y creación de habilidades.
    Transforma episodios exitosos en habilidades procedurales reutilizables.
    """
    
    def __init__(self, sistema_memoria, configuracion: Dict[str, Any]):
        self.memoria = sistema_memoria
        self.config = configuracion
        self.umbral_similitud = configuracion.get('umbral_similitud', 0.7)
        self.min_episodios_grupo = configuracion.get('min_episodios_grupo', 3)
        
        logger.info("Mecanismo de Generalización inicializado")
    
    async def generalizar_desde_episodios(self, episodios: List[Dict]) -> List[Dict[str, Any]]:
        """
        Generaliza habilidades a partir de un conjunto de episodios exitosos.
        
        Args:
            episodios: Lista de episodios para análisis
        
        Returns:
            List[Dict]: Habilidades generalizadas creadas
        """
        try:
            # 1. Filtrar episodios exitosos
            episodios_exitosos = [e for e in episodios if e.get('estado_global') == 'exito']
            
            if len(episodios_exitosos) < self.min_episodios_grupo:
                logger.warning(f"Episodios insuficientes para generalización: {len(episodios_exitosos)}")
                return []
            
            # 2. Extraer y agrupar patrones
            grupos_patrones = await self._agrupar_patrones(episodios_exitosos)
            
            # 3. Generalizar habilidades desde cada grupo
            habilidades_generadas = []
            for grupo_id, episodios_grupo in grupos_patrones.items():
                if len(episodios_grupo) >= self.min_episodios_grupo:
                    habilidad = await self._generalizar_habilidad(episodios_grupo, grupo_id)
                    if habilidad:
                        habilidades_generadas.append(habilidad)
            
            # 4. Almacenar habilidades generalizadas
            habilidades_almacenadas = []
            for habilidad in habilidades_generadas:
                habilidad_id = await self.memoria.guardar_habilidad(habilidad)
                habilidades_almacenadas.append({
                    'habilidad_id': habilidad_id,
                    'habilidad': habilidad,
                    'episodios_base': len([g for g in grupos_patrones.values() 
                                         if any(ep['id'] in [e['id'] for e in episodios_grupo] 
                                                for ep in episodios_grupo)])
                })
            
            logger.info(f"Generalizadas {len(habilidades_almacenadas)} nuevas habilidades")
            return habilidades_almacenadas
            
        except Exception as e:
            logger.error(f"Error en generalización: {e}")
            return []
    
    async def _agrupar_patrones(self, episodios: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Agrupa episodios por similitud de patrones de ejecución.
        
        Args:
            episodios: Episodios exitosos para agrupar
        
        Returns:
            Dict: Grupos de episodios con patrones similares
        """
        # Extraer características estructurales de los episodios
        caracteristicas = self._extraer_caracteristicas_estructurales(episodios)
        
        if len(caracteristicas) < self.min_episodios_grupo:
            return {}
        
        # Agrupar usando clustering
        clusters = self._clusterizar_episodios(caracteristicas)
        
        # Organizar episodios por grupo
        grupos = {}
        for i, (episodio, cluster_id) in enumerate(zip(episodios, clusters)):
            if cluster_id not in grupos:
                grupos[cluster_id] = []
            grupos[cluster_id].append(episodio)
        
        return grupos
    
    def _extraer_caracteristicas_estructurales(self, episodios: List[Dict]) -> List[List[float]]:
        """Extrae características estructurales de episodios para clustering"""
        caracteristicas = []
        
        for episodio in episodios:
            # Características basadas en la estructura del plan ejecutado
            plan = episodio.get('plan_ejecutado', {})
            tareas = plan.get('tareas', [])
            
            # Vector de características
            vec = [
                len(tareas),  # Número de tareas
                sum(1 for t in tareas if t.get('tipo') == 'busqueda'),  # Tareas de búsqueda
                sum(1 for t in tareas if t.get('tipo') == 'generacion'),  # Tareas de generación
                sum(1 for t in tareas if t.get('tipo') == 'procesamiento'),  # Tareas de procesamiento
                episodio.get('duracion_total_segundos', 0) / 60,  # Duración en minutos
                len(set(t.get('herramienta', '') for t in tareas))  # Herramientas únicas
            ]
            
            caracteristicas.append(vec)
        
        return caracteristicas