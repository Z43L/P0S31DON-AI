from typing import Dict, List, Any, Optional, Tuple
import json
import re
from datetime import datetime
from enum import Enum
from loguru import logger

class EstadoPlanificacion(Enum):
    """Estados posibles durante el proceso de planificación"""
    INICIO = "inicio"
    CONSULTA_KB = "consulta_base_conocimiento"
    GENERACION = "generacion_plan"
    ADAPTACION = "adaptacion_plan"
    VALIDACION = "validacion"
    OPTIMIZACION = "optimizacion"
    COMPLETADO = "completado"
    ERROR = "error"

class ModuloComprensionPlanificacion:
    """Módulo principal de Comprensión y Planificación de SAAM"""
    
    def __init__(self, cliente_llm, sistema_memoria, configuracion: Dict[str, Any]):
        self.llm = cliente_llm
        self.memoria = sistema_memoria
        self.config = configuracion
        self.estado_actual = EstadoPlanificacion.INICIO
        self.max_intentos_replanificacion = configuracion.get('max_intentos_replanificacion', 3)
        
        # Cache de planes recientes para optimización de rendimiento
        self.cache_planes = {}
        logger.info("Módulo de Comprensión y Planificación inicializado")
    
    def generar_plan(self, objetivo_usuario: str, contexto: Dict[str, Any] = None, 
                    session_id: str = None) -> Dict[str, Any]:
        """
        Función principal para generar un plan de tareas para un objetivo dado.
        
        Args:
            objetivo_usuario: Objetivo en lenguaje natural
            contexto: Información contextual adicional
            session_id: Identificador de sesión para mantener estado
        
        Returns:
            Dict: Plan estructurado con tareas y metadatos
        """
        try:
            self.estado_actual = EstadoPlanificacion.INICIO
            logger.info(f"Iniciando planificación para: {objetivo_usuario[:100]}...")
            
            # 1. Preprocesamiento y normalización del objetivo
            objetivo_normalizado = self._preprocesar_objetivo(objetivo_usuario)
            
            # 2. Consultar base de conocimiento para planes similares
            self.estado_actual = EstadoPlanificacion.CONSULTA_KB
            planes_similares = self._consultar_planes_similares(objetivo_normalizado)
            
            plan_estructurado = None
            origen_plan = "nuevo"
            
            if planes_similares:
                # 3A. Adaptar plan existente
                self.estado_actual = EstadoPlanificacion.ADAPTACION
                plan_estructurado = self._adaptar_plan_existente(
                    planes_similares[0], objetivo_normalizado, contexto
                )
                origen_plan = "adaptado"
            else:
                # 3B. Generar nuevo plan desde cero
                self.estado_actual = EstadoPlanificacion.GENERACION
                plan_estructurado = self._generar_nuevo_plan(
                    objetivo_normalizado, contexto
                )
            
            # 4. Validar y optimizar el plan
            self.estado_actual = EstadoPlanificacion.VALIDACION
            if not self._validar_plan(plan_estructurado):
                logger.warning("Plan inicial no válido, intentando replanificación")
                plan_estructurado = self._replanificar(objetivo_normalizado, contexto)
            
            self.estado_actual = EstadoPlanificacion.OPTIMIZACION
            plan_optimizado = self._optimizar_plan(plan_estructurado)
            
            # 5. Registrar en memoria de trabajo
            if session_id:
                self.memoria.guardar_contexto(
                    f"plan_{session_id}", 
                    plan_optimizado,
                    expiration=3600  # 1 hora
                )
            
            self.estado_actual = EstadoPlanificacion.COMPLETADO
            logger.success(f"Plan generado exitosamente ({origen_plan})")
            
            return {
                "plan": plan_optimizado,
                "metadatos": {
                    "origen": origen_plan,
                    "estado": self.estado_actual.value,
                    "timestamp": datetime.now().isoformat(),
                    "objetivo_original": objetivo_usuario,
                    "objetivo_normalizado": objetivo_normalizado
                }
            }
            
        except Exception as e:
            self.estado_actual = EstadoPlanificacion.ERROR
            logger.error(f"Error en generación de plan: {e}")
            raise
    
    def _preprocesar_objetivo(self, objetivo: str) -> str:
        """Normaliza y preprocesa el objetivo del usuario"""
        objetivo_limpio = re.sub(r'\s+', ' ', objetivo.strip()).lower()
        return self._enriquecer_con_intencion(objetivo_limpio)
    
    def _enriquecer_con_intencion(self, objetivo: str) -> str:
        """Enriquece el objetivo con información de intención detectada"""
        intenciones = {
            'buscar': ['encontrar', 'buscar', 'localizar', 'obtener información'],
            'crear': ['crear', 'generar', 'escribir', 'producir'],
            'analizar': ['analizar', 'evaluar', 'estudiar', 'examinar'],
            'resumir': ['resumir', 'resumen', 'sintetizar']
        }
        
        for intencion, palabras in intenciones.items():
            if any(palabra in objetivo for palabra in palabras):
                return f"{intencion} {objetivo}"
        
        return objetivo
    
    def _consultar_planes_similares(self, objetivo: str, limite: int = 3) -> List[Dict]:
        """Consulta la base de conocimiento para planes similares"""
        try:
            cache_key = f"plan_query_{hash(objetivo) % 1000}"
            if cache_key in self.cache_planes:
                return self.cache_planes[cache_key]
            
            resultados = self.memoria.buscar_habilidades(
                objetivo, 
                filtros={"tipo": "plan"},
                limite=limite
            )
            
            planes = []
            for resultado in resultados:
                try:
                    plan_data = resultado['habilidad']
                    if self._es_plan_valido(plan_data):
                        planes.append(plan_data)
                except (KeyError, TypeError):
                    continue
            
            self.cache_planes[cache_key] = planes
            return planes
            
        except Exception as e:
            logger.warning(f"Error en consulta de planes similares: {e}")
            return []
    
    def _es_plan_valido(self, plan: Dict) -> bool:
        """Valida la estructura básica de un plan"""
        required_keys = {'tareas', 'objetivo', 'tipo'}
        return all(key in plan for key in required_keys) and isinstance(plan['tareas'], list)