from typing import Dict, Any
from .met import ModuloEjecucionTareas
from ..herramientas.gestor_herramientas import GestorHerramientas
from ..herramientas.monitor_rendimiento import MonitorRendimiento
from loguru import logger

class METFactory:
    """Factory para la creación y configuración del Módulo de Ejecución de Tareas"""
    
    @staticmethod
    def crear_met(sistema_memoria, configuracion: Dict[str, Any]) -> ModuloEjecucionTareas:
        """Crea una instancia completa del MET con todas sus dependencias"""
        try:
            # Configurar gestor de herramientas
            gestor_herramientas = GestorHerramientas(
                configuracion.get('herramientas', {})
            )
            
            # Configurar monitor de rendimiento
            monitor = MonitorRendimiento(
                configuracion.get('monitorizacion', {})
            )
            
            # Crear instancia del MET
            met = ModuloEjecucionTareas(
                sistema_herramientas=gestor_herramientas,
                sistema_memoria=sistema_memoria,
                configuracion=configuracion.get('met', {})
            )
            
            # Inyectar dependencias adicionales
            met.monitor_rendimiento = monitor
            
            logger.success("MET inicializado exitosamente con todos los componentes")
            return met
            
        except Exception as e:
            logger.error(f"Error creando MET: {e}")
            raise