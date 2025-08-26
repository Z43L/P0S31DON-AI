from typing import Dict, List, Any, Optional
import json
from datetime import datetime
from loguru import logger

class GestorOptimizaciones:
    """Gestor para aplicar y gestionar optimizaciones en el sistema"""
    
    def __init__(self, sistema_memoria, config_optimizaciones: Dict[str, Any]):
        self.memoria = sistema_memoria
        self.config = config_optimizaciones
        self.optimizaciones_aplicadas = []
        self.estado_optimizaciones = {}
    
    async def aplicar_optimizaciones(self, recomendaciones: List[Dict]) -> Dict[str, Any]:
        """
        Aplica las optimizaciones recomendadas al sistema.
        
        Args:
            recomendaciones: Lista de recomendaciones generadas por los análisis
        
        Returns:
            Dict: Resultado de la aplicación de optimizaciones
        """
        resultados = {
            'optimizaciones_aplicadas': 0,
            'optimizaciones_fallidas': 0,
            'detalles': []
        }
        
        for recomendacion in recomendaciones:
            try:
                resultado = await self._aplicar_optimizacion_individual(recomendacion)
                resultados['detalles'].append(resultado)
                
                if resultado['exito']:
                    resultados['optimizaciones_aplicadas'] += 1
                    self.optimizaciones_aplicadas.append({
                        'timestamp': datetime.now(),
                        'recomendacion': recomendacion,
                        'resultado': resultado
                    })
                else:
                    resultados['optimizaciones_fallidas'] += 1
                    
            except Exception as e:
                logger.error(f"Error aplicando optimización: {e}")
                resultados['detalles'].append({
                    'exito': False,
                    'error': str(e),
                    'recomendacion': recomendacion
                })
                resultados['optimizaciones_fallidas'] += 1
        
        return resultados
    
    async def _aplicar_optimizacion_individual(self, recomendacion: Dict) -> Dict[str, Any]:
        """Aplica una optimización individual específica"""
        tipo_optimizacion = recomendacion.get('tipo')
        
        if tipo_optimizacion == 'preferencia_herramienta':
            return await self._aplicar_preferencia_herramienta(recomendacion)
        elif tipo_optimizacion == 'nueva_habilidad':
            return await self._aplicar_nueva_habilidad(recomendacion)
        elif tipo_optimizacion == 'ajuste_parametros':
            return await self._aplicar_ajuste_parametros(recomendacion)
        else:
            return {
                'exito': False,
                'error': f'Tipo de optimización desconocido: {tipo_optimizacion}'
            }
    
    async def _aplicar_preferencia_herramienta(self, recomendacion: Dict) -> Dict[str, Any]:
        """Aplica una preferencia de herramienta optimizada"""
        try:
            tipo_tarea = recomendacion['tipo_tarea']
            herramienta_recomendada = recomendacion['herramienta_recomendada']
            
            # Actualizar la base de conocimiento
            self.memoria.base_conocimiento.actualizar_preferencia_herramienta(
                tipo_tarea, herramienta_recomendada
            )
            
            logger.info(f"Preferencia actualizada: {tipo_tarea} -> {herramienta_recomendada}")
            
            return {
                'exito': True,
                'tipo': 'preferencia_herramienta',
                'tipo_tarea': tipo_tarea,
                'herramienta': herramienta_recomendada,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'exito': False,
                'error': str(e),
                'tipo': 'preferencia_herramienta'
            }
    
    async def _aplicar_nueva_habilidad(self, recomendacion: Dict) -> Dict[str, Any]:
        """Aplica una nueva habilidad autogenerada"""
        try:
            habilidad = recomendacion['habilidad']
            
            # Guardar en la base de conocimiento
            habilidad_id = self.memoria.guardar_habilidad(habilidad)
            
            logger.info(f"Nueva habilidad creada: {habilidad_id}")
            
            return {
                'exito': True,
                'tipo': 'nueva_habilidad',
                'habilidad_id': habilidad_id,
                'nombre_habilidad': habilidad.get('nombre', ''),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'exito': False,
                'error': str(e),
                'tipo': 'nueva_habilidad'
            }