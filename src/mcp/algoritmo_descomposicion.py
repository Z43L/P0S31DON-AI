from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import re
from loguru import logger

class EstrategiaDescomposicion(Enum):
    """Estrategias disponibles para descomposición de objetivos"""
    BASADA_HABILIDADES = "basada_habilidades"
    RAZONAMIENTO_LLM = "razonamiento_llm"
    HIBRIDA = "hibrida"
    EMERGENCIA = "modo_emergencia"

class AlgoritmoDescomposicion:
    """Algoritmo principal de descomposición de objetivos en tareas"""
    
    def __init__(self, cliente_llm, sistema_memoria, configuracion: Dict[str, Any]):
        self.llm = cliente_llm
        self.memoria = sistema_memoria
        self.config = configuracion
        self.estrategia_actual = EstrategiaDescomposicion.HIBRIDA
        
        logger.info("Algoritmo de Descomposición inicializado")
    
    async def descomponer_objetivo(self, objetivo: str, contexto: Dict = None) -> Dict[str, Any]:
        """
        Descompone un objetivo en una secuencia estructurada de tareas ejecutables.
        
        Args:
            objetivo: Objetivo en lenguaje natural
            contexto: Información contextual adicional
        
        Returns:
            Dict: Plan estructurado con tareas y metadatos
        """
        try:
            # 1. Preprocesamiento y normalización
            objetivo_procesado = await self._preprocesar_objetivo(objetivo, contexto)
            
            # 2. Selección de estrategia de descomposición
            estrategia = self._seleccionar_estrategia(objetivo_procesado)
            
            # 3. Ejecución de la estrategia seleccionada
            if estrategia == EstrategiaDescomposicion.BASADA_HABILIDADES:
                plan = await self._descomposicion_basada_habilidades(objetivo_procesado)
            elif estrategia == EstrategiaDescomposicion.RAZONAMIENTO_LLM:
                plan = await self._descomposicion_por_razonamiento(objetivo_procesado)
            else:
                plan = await self._descomposicion_hibrida(objetivo_procesado)
            
            # 4. Validación y optimización del plan
            plan_validado = await self._validar_y_optimizar_plan(plan)
            
            logger.success(f"Objetivo descompuesto exitosamente: {objetivo[:50]}...")
            return plan_validado
            
        except Exception as e:
            logger.error(f"Error en descomposición de objetivo: {e}")
            # Fallback a estrategia de emergencia
            return await self._modo_emergencia(objetivo, contexto)
    
    async def _preprocesar_objetivo(self, objetivo: str, contexto: Dict) -> Dict[str, Any]:
        """Procesa y enriquece el objetivo con información contextual"""
        # Limpieza y normalización básica
        objetivo_limpio = re.sub(r'\s+', ' ', objetivo.strip())
        
        # Extracción de entidades y componentes clave
        entidades = await self._extraer_entidades(objetivo_limpio)
        
        # Determinación del tipo de objetivo
        tipo_objetivo = self._clasificar_tipo_objetivo(objetivo_limpio)
        
        return {
            'texto_original': objetivo,
            'texto_procesado': objetivo_limpio,
            'entidades': entidades,
            'tipo': tipo_objetivo,
            'contexto': contexto or {},
            'timestamp': self._obtener_timestamp()
        }
    
    def _seleccionar_estrategia(self, objetivo: Dict) -> EstrategiaDescomposicion:
        """Selecciona la estrategia óptima de descomposición"""
        # Consultar base de conocimiento para habilidades existentes
        habilidades_relevantes = self.memoria.buscar_habilidades(
            objetivo['tipo'], 
            filtros={'categoria': objetivo['tipo']},
            limite=3
        )
        
        if habilidades_relevantes and len(habilidades_relevantes) > 0:
            return EstrategiaDescomposicion.BASADA_HABILIDADES
        
        # Para objetivos complejos o novedosos, usar razonamiento
        if self._es_objetivo_complejo(objetivo):
            return EstrategiaDescomposicion.RAZONAMIENTO_LLM
        
        return EstrategiaDescomposicion.HIBRIDA