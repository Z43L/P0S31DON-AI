from typing import Dict, List, Any, Optional
from loguru import logger

class DescomposicionHabilidades:
    """Estrategia de descomposición utilizando habilidades preexistentes"""
    
    def __init__(self, cliente_llm, sistema_memoria, configuracion: Dict[str, Any]):
        self.llm = cliente_llm
        self.memoria = sistema_memoria
        self.config = configuracion
    
    async def descomponer_con_habilidades(self, objetivo: Dict) -> Dict[str, Any]:
        """
        Descompone un objetivo adaptando habilidades existentes de la base de conocimiento.
        
        Args:
            objetivo: Objetivo procesado y enriquecido
        
        Returns:
            Dict: Plan generado por adaptación de habilidades existentes
        """
        try:
            # 1. Buscar habilidades relevantes
            habilidades = self.memoria.buscar_habilidades(
                objetivo['tipo'],
                filtros={'estado': 'activo', 'tasa_exito': {'$gt': 0.7}},
                limite=5
            )
            
            if not habilidades:
                raise ValueError("No se encontraron habilidades relevantes")
            
            # 2. Seleccionar la mejor habilidad basado en similitud y rendimiento
            habilidad_optima = self._seleccionar_habilidad_optima(habilidades, objetivo)
            
            # 3. Adaptar la habilidad al objetivo específico
            plan_adaptado = await self._adaptar_habilidad(habilidad_optima, objetivo)
            
            return {
                **plan_adaptado,
                'metadatos': {
                    'estrategia': 'basada_habilidades',
                    'habilidad_base': habilidad_optima['nombre'],
                    'similitud': self._calcular_similitud(habilidad_optima, objetivo),
                    'confianza': habilidad_optima.get('estadisticas', {}).get('tasa_exito', 0.7)
                }
            }
            
        except Exception as e:
            logger.error(f"Error en descomposición por habilidades: {e}")
            raise
    
    def _seleccionar_habilidad_optima(self, habilidades: List[Dict], objetivo: Dict) -> Dict:
        """Selecciona la habilidad más adecuada para el objetivo"""
        habilidades_puntuadas = []
        
        for habilidad in habilidades:
            puntuacion = self._calcular_puntuacion_habilidad(habilidad, objetivo)
            habilidades_puntuadas.append((habilidad, puntuacion))
        
        # Seleccionar la habilidad con mayor puntuación
        return max(habilidades_puntuadas, key=lambda x: x[1])[0]
    
    def _calcular_puntuacion_habilidad(self, habilidad: Dict, objetivo: Dict) -> float:
        """Calcula una puntuación de adecuación de la habilidad al objetivo"""
        puntuacion = 0.0
        
        # Ponderar por similitud semántica
        similitud = self._calcular_similitud(habilidad, objetivo)
        puntuacion += similitud * 0.4
        
        # Ponderar por rendimiento histórico
        tasa_exito = habilidad.get('estadisticas', {}).get('tasa_exito', 0.5)
        puntuacion += tasa_exito * 0.4
        
        # Ponderar por relevancia contextual
        relevancia = self._calcular_relevancia_contextual(habilidad, objetivo)
        puntuacion += relevancia * 0.2
        
        return puntuacion