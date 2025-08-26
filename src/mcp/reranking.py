from typing import Dict, List, Any, Optional
from loguru import logger

class RerankerInteligente:
    """Sistema de reranking inteligente basado en múltiples factores de relevancia"""
    
    def __init__(self, sistema_memoria, configuracion: Dict[str, Any]):
        self.memoria = sistema_memoria
        self.config = configuracion
    
    async def aplicar_reranking(self, resultados: List[Dict], objetivo: Dict) -> List[Dict]:
        """
        Aplica reranking inteligente considerando múltiples factores de relevancia.
        
        Args:
            resultados: Resultados de búsqueda fusionados
            objetivo: Objetivo original de consulta
        
        Returns:
            List[Dict]: Resultados rerankeado
        """
        try:
            resultados_rerankeado = []
            
            for resultado in resultados:
                plan = resultado['plan']
                score_final = resultado['score_combinado']
                
                # Ajustar score basado en rendimiento histórico
                score_rendimiento = self._ajustar_por_rendimiento(plan)
                score_final *= score_rendimiento
                
                # Ajustar score basado en relevancia temporal
                score_temporal = self._ajustar_por_temporalidad(plan)
                score_final *= score_temporal
                
                # Ajustar score basado en complejidad
                score_complejidad = self._ajustar_por_complejidad(plan, objetivo)
                score_final *= score_complejidad
                
                resultados_rerankeado.append({
                    **resultado,
                    'score_final': score_final,
                    'factores_ajuste': {
                        'rendimiento': score_rendimiento,
                        'temporalidad': score_temporal,
                        'complejidad': score_complejidad
                    }
                })
            
            # Reordenar por score final
            resultados_rerankeado.sort(key=lambda x: x['score_final'], reverse=True)
            
            return resultados_rerankeado
            
        except Exception as e:
            logger.error(f"Error en reranking: {e}")
            return resultados
    
    def _ajustar_por_rendimiento(self, plan: Dict) -> float:
        """Ajusta el score basado en el rendimiento histórico del plan"""
        estadisticas = plan.get('estadisticas', {})
        tasa_exito = estadisticas.get('tasa_exito', 0.5)
        veces_utilizado = estadisticas.get('veces_utilizado', 1)
        
        # Planes con buen historial y uso suficiente tienen bonus
        if tasa_exito > 0.8 and veces_utilizado >= 5:
            return 1.2
        elif tasa_exito > 0.6:
            return 1.0
        else:
            return 0.8
    
    def _ajustar_por_temporalidad(self, plan: Dict) -> float:
        """Ajusta el score basado en la temporalidad del plan"""
        from datetime import datetime, timedelta
        
        fecha_creacion = plan.get('metadata', {}).get('fecha_creacion')
        if not fecha_creacion:
            return 1.0
        
        # Convertir a datetime si es string
        if isinstance(fecha_creacion, str):
            try:
                fecha_creacion = datetime.fromisoformat(fecha_creacion.replace('Z', '+00:00'))
            except:
                return 1.0
        
        # Planes recientes (últimos 30 días) tienen bonus leve
        if datetime.now() - fecha_creacion < timedelta(days=30):
            return 1.1
        else:
            return 1.0