from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
from loguru import logger

class AnalizadorExitoFracaso:
    """
    Sistema principal de análisis de éxito/fracaso para evaluar ejecuciones
    y identificar factores determinantes del rendimiento del sistema.
    """
    
    def __init__(self, sistema_memoria, configuracion: Dict[str, Any]):
        self.memoria = sistema_memoria
        self.config = configuracion
        self.modelo: Optional[RandomForestClassifier] = None
        self.ultimo_entrenamiento: Optional[datetime] = None
        self.metricas_modelo: Dict[str, Any] = {}
        
        logger.info("Analizador de Éxito/Fracaso inicializado")
    
    async def analizar_episodios(self, episodios: List[Dict], retrenar_modelo: bool = False) -> Dict[str, Any]:
        """
        Analiza un conjunto de episodios para identificar patrones de éxito/fracaso.
        
        Args:
            episodios: Lista de episodios a analizar
            retrenar_modelo: Si se debe reentrenar el modelo de clasificación
        
        Returns:
            Dict: Resultados del análisis con insights y recomendaciones
        """
        try:
            # 1. Preprocesamiento de datos
            df_episodios = self._preprocesar_episodios(episodios)
            
            # 2. Extracción de características
            caracteristicas, objetivo = self._extraer_caracteristicas(df_episodios)
            
            # 3. Análisis estadístico
            analisis_estadistico = self._realizar_analisis_estadistico(caracteristicas, objetivo)
            
            # 4. Entrenamiento/evaluación del modelo
            if retrenar_modelo or self.modelo is None:
                metricas_modelo = await self._entrenar_modelo(caracteristicas, objetivo)
                self.metricas_modelo = metricas_modelo
            
            # 5. Identificación de factores clave
            factores_clave = self._identificar_factores_clave(caracteristicas, objetivo)
            
            # 6. Generación de recomendaciones
            recomendaciones = self._generar_recomendaciones(analisis_estadistico, factores_clave)
            
            return {
                'estadisticas': analisis_estadistico,
                'factores_clave': factores_clave,
                'recomendaciones': recomendaciones,
                'metricas_modelo': self.metricas_modelo,
                'total_episodios_analizados': len(episodios),
                'timestamp_analisis': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error en análisis de éxito/fracaso: {e}")
            raise
    
    def _preprocesar_episodios(self, episodios: List[Dict]) -> pd.DataFrame:
        """Preprocesa los episodios para análisis"""
        datos = []
        
        for episodio in episodios:
            fila = {
                'id': episodio.get('id'),
                'objetivo': episodio.get('objetivo', ''),
                'estado': episodio.get('estado_global', 'desconocido'),
                'duracion_total': episodio.get('duracion_total_segundos', 0),
                'num_tareas': len(episodio.get('resultados_tareas', [])),
                'exito': 1 if episodio.get('estado_global') == 'exito' else 0,
                'timestamp': episodio.get('timestamp_creacion')
            }
            
            # Extraer métricas de tareas individuales
            tareas_exitosas = sum(1 for t in episodio.get('resultados_tareas', []) if t.get('exito', False))
            fila['tasa_exito_tareas'] = tareas_exitosas / fila['num_tareas'] if fila['num_tareas'] > 0 else 0
            
            # Extraer características de herramientas utilizadas
            herramientas = set()
            for tarea in episodio.get('resultados_tareas', []):
                if 'herramienta_utilizada' in tarea:
                    herramientas.add(tarea['herramienta_utilizada'])
            
            fila['num_herramientas_unicas'] = len(herramientas)
            fila['herramientas_utilizadas'] = list(herramientas)
            
            datos.append(fila)
        
        return pd.DataFrame(datos)