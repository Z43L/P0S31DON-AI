from typing import Dict, Any
from ..aprendizaje.analizador_principal import ModuloAprendizajeOptimizacion
from ..aprendizaje.analisis_rendimiento import AnalizadorRendimiento
from ..aprendizaje.deteccion_patrones import DetectorPatrones
from ..aprendizaje.gestor_optimizaciones import GestorOptimizaciones
from ..aprendizaje.monitor_impacto import MonitorImpactoOptimizaciones
from loguru import logger

class MAOFactory:
    """Factory para la creación y configuración del Módulo de Aprendizaje y Optimización"""
    
    @staticmethod
    def crear_mao(sistema_memoria, configuracion: Dict[str, Any]) -> ModuloAprendizajeOptimizacion:
        """Crea una instancia completa del MAO con todas sus dependencias"""
        try:
            # Configurar componentes de análisis
            analizador_rendimiento = AnalizadorRendimiento(
                configuracion.get('analisis', {}).get('rendimiento_herramientas', {})
            )
            
            detector_patrones = DetectorPatrones(
                configuracion.get('analisis', {}).get('deteccion_patrones', {})
            )
            
            # Configurar gestor de optimizaciones
            gestor_optimizaciones = GestorOptimizaciones(
                sistema_memoria, configuracion.get('optimizaciones', {})
            )
            
            # Configurar monitor de impacto
            monitor_impacto = MonitorImpactoOptimizaciones(
                sistema_memoria, configuracion.get('monitoreo', {})
            )
            
            # Crear instancia del MAO
            mao = ModuloAprendizajeOptimizacion(
                sistema_memoria=sistema_memoria,
                configuracion=configuracion.get('mao', {})
            )
            
            # Inyectar dependencias
            mao.analizador_rendimiento = analizador_rendimiento
            mao.detector_patrones = detector_patrones
            mao.gestor_optimizaciones = gestor_optimizaciones
            mao.monitor_impacto = monitor_impacto
            
            logger.success("MAO inicializado exitosamente con todos los componentes")
            return mao
            
        except Exception as e:
            logger.error(f"Error creando MAO: {e}")
            raise