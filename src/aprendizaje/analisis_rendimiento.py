from typing import Dict, List, Any, Tuple
import pandas as pd
import numpy as np
from scipy import stats
from loguru import logger

class AnalizadorRendimiento:
    """Analizador especializado en rendimiento de herramientas y configuraciones"""
    
    def __init__(self, config_analisis: Dict[str, Any]):
        self.config = config_analisis
        self.umbral_confianza = config_analisis.get('umbral_confianza', 0.95)
    
    async def analizar_rendimiento_herramientas(self, df_episodios: pd.DataFrame) -> Dict[str, Any]:
        """
        Analiza el rendimiento comparativo de diferentes herramientas para los mismos tipos de tareas.
        
        Args:
            df_episodios: DataFrame con datos de episodios para análisis
        
        Returns:
            Dict: Resultados del análisis con recomendaciones
        """
        try:
            # Extraer datos de herramientas por tipo de tarea
            datos_herramientas = self._extraer_datos_herramientas(df_episodios)
            
            resultados = {}
            recomendaciones = []
            
            for tipo_tarea, herramientas in datos_herramientas.items():
                if len(herramientas) >= 2:  # Necesitamos al menos 2 herramientas para comparar
                    analisis_comparativo = self._comparar_herramientas(herramientas)
                    
                    if analisis_comparativo['diferencia_significativa']:
                        recomendacion = self._generar_recomendacion_herramienta(
                            tipo_tarea, analisis_comparativo
                        )
                        recomendaciones.append(recomendacion)
                    
                    resultados[tipo_tarea] = analisis_comparativo
            
            return {
                'resultados_detallados': resultados,
                'recomendaciones': recomendaciones,
                'metricas_globales': self._calcular_metricas_globales(datos_herramientas)
            }
            
        except Exception as e:
            logger.error(f"Error en análisis de rendimiento: {e}")
            return {'error': str(e)}
    
    def _extraer_datos_herramientas(self, df: pd.DataFrame) -> Dict[str, List[Dict]]:
        """Extrae y organiza los datos de herramientas por tipo de tarea"""
        datos_herramientas = {}
        
        # Iterar sobre las columns del DataFrame para encontrar datos de herramientas
        for col in df.columns:
            if col.startswith('tarea_') and col.endswith('_herramienta'):
                # Extraer el ID de la tarea del nombre de la columna
                tarea_id = col.split('_')[1]
                
                # Determinar el tipo de tarea basado en el objetivo
                # (En implementación real, esto sería más sofisticado)
                tipo_tarea = self._inferir_tipo_tarea(df, tarea_id)
                
                if tipo_tarea not in datos_herramientas:
                    datos_herramientas[tipo_tarea] = []
                
                # Recopilar datos de esta herramienta
                for _, fila in df.iterrows():
                    herramienta = fila[col]
                    exito_col = f'tarea_{tarea_id}_exito'
                    duracion_col = f'tarea_{tarea_id}_duracion'
                    
                    if pd.notna(herramienta) and pd.notna(fila.get(exito_col)):
                        datos_herramientas[tipo_tarea].append({
                            'herramienta': herramienta,
                            'exito': fila[exito_col],
                            'duracion': fila.get(duracion_col, 0),
                            'timestamp': fila['timestamp']
                        })
        
        return datos_herramientas
    
    def _inferir_tipo_tarea(self, df: pd.DataFrame, tarea_id: str) -> str:
        """Infiere el tipo de tarea basado en los objetivos (simplificado)"""
        # En implementación real, usaría NLP para clasificar los objetivos
        objetivos = df['objetivo'].astype(str).str.lower()
        
        if objetivos.str.contains('buscar|search|find').any():
            return 'busqueda'
        elif objetivos.str.contains('generar|create|write').any():
            return 'generacion'
        elif objetivos.str.contains('analizar|analyze|process').any():
            return 'analisis'
        else:
            return 'general'
    
    def _comparar_herramientas(self, datos_herramientas: List[Dict]) -> Dict[str, Any]:
        """Compara estadísticamente el rendimiento de diferentes herramientas"""
        # Agrupar datos por herramienta
        grupos = {}
        for dato in datos_herramientas:
            herramienta = dato['herramienta']
            if herramienta not in grupos:
                grupos[herramienta] = []
            grupos[herramienta].append(dato)
        
        # Calcular métricas por herramienta
        metricas_herramientas = {}
        for herramienta, datos in grupos.items():
            exitos = [d['exito'] for d in datos]
            duraciones = [d['duracion'] for d in datos if d['duracion'] > 0]
            
            metricas_herramientas[herramienta] = {
                'n': len(datos),
                'tasa_exito': np.mean(exitos) if exitos else 0,
                'duracion_promedio': np.mean(duraciones) if duraciones else 0,
                'duracion_std': np.std(duraciones) if duraciones else 0,
                'confianza': self._calcular_intervalo_confianza(duraciones) if duraciones else (0, 0)
            }
        
        # Realizar test estadístico si hay suficientes datos
        herramientas_comparables = [h for h in grupos if len(grupos[h]) >= 10]
        diferencia_significativa = False
        
        if len(herramientas_comparables) >= 2:
            # Comparar las dos herramientas más utilizadas
            herramientas_ordenadas = sorted(
                herramientas_comparables, 
                key=lambda x: len(grupos[x]), 
                reverse=True
            )
            
            herramienta_a, herramienta_b = herramientas_ordenadas[:2]
            datos_a = [d['duracion'] for d in grupos[herramienta_a] if d['duracion'] > 0]
            datos_b = [d['duracion'] for d in grupos[herramienta_b] if d['duracion'] > 0]
            
            if len(datos_a) >= 10 and len(datos_b) >= 10:
                # Test t para muestras independientes
                t_stat, p_value = stats.ttest_ind(datos_a, datos_b)
                diferencia_significativa = p_value < (1 - self.umbral_confianza)
        
        return {
            'metricas_por_herramienta': metricas_herramientas,
            'diferencia_significativa': diferencia_significativa,
            'herramienta_recomendada': self._seleccionar_mejor_herramienta(metricas_herramientas)
        }
    
    def _calcular_intervalo_confianza(self, datos: List[float]) -> Tuple[float, float]:
        """Calcula el intervalo de confianza del 95% para los datos"""
        if not datos:
            return (0, 0)
        
        media = np.mean(datos)
        std_err = stats.sem(datos)
        intervalo = stats.t.interval(self.umbral_confianza, len(datos)-1, loc=media, scale=std_err)
        
        return intervalo
    
    def _seleccionar_mejor_herramienta(self, metricas: Dict[str, Any]) -> str:
        """Selecciona la mejor herramienta basado en métricas compuestas"""
        # Ponderar tasa de éxito (60%) y duración (40%)
        mejores_puntajes = {}
        
        for herramienta, metrica in metricas.items():
            if metrica['n'] >= 5:  # Mínimo de muestras
                puntaje_exito = metrica['tasa_exito'] * 0.6
                puntaje_velocidad = (1 / (metrica['duracion_promedio'] + 0.1)) * 0.4
                puntaje_total = puntaje_exito + puntaje_velocidad
                
                mejores_puntajes[herramienta] = puntaje_total
        
        return max(mejores_puntajes.items(), key=lambda x: x[1])[0] if mejores_puntajes else ""