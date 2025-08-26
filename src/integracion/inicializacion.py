from typing import Dict, List, Any
import asyncio
from loguru import logger
from sistema.mcp_factory import MCPFactory
from sistema.met_factory import METFactory  
from sistema.sm3 import SistemaMemoriaTripleCapa
from sistema.mao_factory import MAOFactory

class InicializadorSAAM:
    """Sistema de inicialización y coordinación de todos los módulos SAAM"""
    
    def __init__(self, configuracion: Dict[str, Any]):
        self.config = configuracion
        self.modulos = {}
        self.estado = "detenido"
        
    async def inicializar_sistema(self) -> bool:
        """
        Inicializa todos los módulos de SAAM en el orden correcto.
        
        Returns:
            bool: True si la inicialización fue exitosa
        """
        try:
            logger.info("Iniciando inicialización del sistema SAAM")
            self.estado = "inicializando"
            
            # 1. Inicializar Sistema de Memoria primero (dependencia central)
            await self._inicializar_memoria()
            
            # 2. Inicializar Módulo de Aprendizaje y Optimización
            await self._inicializar_mao()
            
            # 3. Inicializar Módulo de Ejecución de Tareas
            await self._inicializar_met()
            
            # 4. Inicializar Módulo de Comprensión y Planificación
            await self._inicializar_mcp()
            
            # 5. Verificar integridad del sistema
            await self._verificar_integridad()
            
            self.estado = "inicializado"
            logger.success("Sistema SAAM inicializado exitosamente")
            return True
            
        except Exception as e:
            self.estado = "error"
            logger.critical(f"Error en inicialización del sistema: {e}")
            await self._apagar_sistema()
            return False
    
    async def _inicializar_memoria(self):
        """Inicializa el Sistema de Memoria de Triple Capa"""
        logger.info("Inicializando Sistema de Memoria (SM3)")
        self.modulos['sm3'] = SistemaMemoriaTripleCapa(self.config)
        await self.modulos['sm3'].inicializar()
        
    async def _inicializar_mao(self):
        """Inicializa el Módulo de Aprendizaje y Optimización"""
        logger.info("Inicializando Módulo de Aprendizaje (MAO)")
        self.modulos['mao'] = MAOFactory.crear_mao(
            self.modulos['sm3'], self.config
        )
        
    async def _inicializar_met(self):
        """Inicializa el Módulo de Ejecución de Tareas"""
        logger.info("Inicializando Módulo de Ejecución (MET)")
        self.modulos['met'] = METFactory.crear_met(
            self.modulos['sm3'], self.config
        )
        
    async def _inicializar_mcp(self):
        """Inicializa el Módulo de Comprensión y Planificación"""
        logger.info("Inicializando Módulo de Planificación (MCP)")
        self.modulos['mcp'] = MCPFactory.crear_mcp(
            self.modulos['sm3'], self.config
        )
    
    async def _verificar_integridad(self):
        """Verifica la integridad y conectividad de todos los módulos"""
        checks = [
            self._verificar_modulo('sm3', 'Memoria'),
            self._verificar_modulo('mao', 'Aprendizaje'),
            self._verificar_modulo('met', 'Ejecución'),
            self._verificar_modulo('mcp', 'Planificación')
        ]
        
        resultados = await asyncio.gather(*checks, return_exceptions=True)
        
        for modulo, resultado in zip(['sm3', 'mao', 'met', 'mcp'], resultados):
            if isinstance(resultado, Exception):
                raise Exception(f"Verificación fallida para {modulo}: {resultado}")