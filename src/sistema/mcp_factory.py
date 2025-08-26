from typing import Dict, Any
from .mcp import ModuloComprensionPlanificacion
from .mcp_generacion import GeneradorPlanes
from .mcp_adaptacion import AdaptadorPlanes
from .mcp_validacion import ValidadorOptimizadorPlanes
from loguru import logger

class MCPFactory:
    """Factory para la creación y configuración del Módulo de Comprensión y Planificación"""
    
    @staticmethod
    def crear_mcp(cliente_llm, sistema_memoria, configuracion: Dict[str, Any]) -> ModuloComprensionPlanificacion:
        """Crea una instancia completa del MCP con todas sus dependencias"""
        try:
            generador = GeneradorPlanes(cliente_llm, configuracion.get('mcp', {}))
            adaptador = AdaptadorPlanes(cliente_llm, configuracion.get('mcp', {}))
            validador = ValidadorOptimizadorPlanes(configuracion.get('mcp', {}))
            
            mcp = ModuloComprensionPlanificacion(
                cliente_llm=cliente_llm,
                sistema_memoria=sistema_memoria,
                configuracion=configuracion.get('mcp', {})
            )
            
            mcp.generador_planes = generador
            mcp.adaptador_planes = adaptador
            mcp.validador_planes = validador
            
            logger.success("MCP inicializado exitosamente con todos los componentes")
            return mcp
            
        except Exception as e:
            logger.error(f"Error creando MCP: {e}")
            raise