from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime
from loguru import logger

class NucleoSAAM:
    """
    Núcleo principal del sistema SAAM que coordina el flujo completo PERA
    e integra todos los módulos del sistema.
    """
    
    def __init__(self, mcp, met, sm3, mao, configuracion: Dict[str, Any]):
        self.mcp = mcp
        self.met = met
        self.sm3 = sm3
        self.mao = mao
        self.config = configuracion
        self.sesiones_activas: Dict[str, Dict] = {}
        
        logger.info("Núcleo SAAM inicializado con todos los módulos integrados")
    
    async def procesar_objetivo(self, objetivo: str, contexto_usuario: Dict = None, 
                              session_id: str = None) -> Dict[str, Any]:
        """
        Ejecuta el flujo completo PERA para un objetivo del usuario.
        
        Args:
            objetivo: Objetivo en lenguaje natural
            contexto_usuario: Contexto adicional del usuario
            session_id: ID de sesión existente o None para nueva
        
        Returns:
            Dict: Resultado completo del procesamiento
        """
        session_id = session_id or self._generar_session_id()
        
        try:
            # FASE 1: PLANIFICACIÓN (MCP + SM3)
            logger.info(f"[Session {session_id}] Iniciando planificación")
            plan = await self._fase_planificacion(objetivo, contexto_usuario, session_id)
            
            # FASE 2: EJECUCIÓN (MET + SM3 Memoria Trabajo)
            logger.info(f"[Session {session_id}] Iniciando ejecución")
            resultados = await self._fase_ejecucion(plan, session_id)
            
            # FASE 3: RECOLECCIÓN (SM3 Memoria Episódica)
            logger.info(f"[Session {session_id}] Registrando resultados")
            episodio_id = await self._fase_recoleccion(objetivo, plan, resultados, session_id)
            
            # FASE 4: APRENDIZAJE (MAO + SM3 - Asíncrono)
            logger.info(f"[Session {session_id}] Iniciando aprendizaje asíncrono")
            asyncio.create_task(self._fase_aprendizaje(episodio_id))
            
            return {
                'session_id': session_id,
                'estado': 'completado',
                'resultados': resultados,
                'episodio_id': episodio_id,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"[Session {session_id}] Error en procesamiento: {e}")
            await self._registrar_error(session_id, str(e))
            raise
    
    async def _fase_planificacion(self, objetivo: str, contexto: Dict, session_id: str) -> Dict[str, Any]:
        """Ejecuta la fase de planificación del ciclo PERA"""
        # Inicializar memoria de trabajo para la sesión
        await self.sm3.inicializar_sesion(session_id)
        
        # Consultar base de conocimiento para planes similares
        planes_similares = await self.sm3.consultar_planes_similares(objetivo)
        
        # Generar o adaptar plan
        if planes_similares:
            plan = await self.mcp.adaptar_plan_existente(objetivo, planes_similares[0], contexto)
        else:
            plan = await self.mcp.generar_nuevo_plan(objetivo, contexto)
        
        # Guardar plan en memoria de trabajo
        await self.sm3.guardar_contexto(session_id, 'plan_actual', plan)
        
        return plan
    
    async def _fase_ejecucion(self, plan: Dict, session_id: str) -> Dict[str, Any]:
        """Ejecuta la fase de ejecución del ciclo PERA"""
        resultados_tareas = []
        
        for tarea in plan.get('tareas', []):
            # Ejecutar tarea individual
            resultado = await self.met.ejecutar_tarea(tarea, {
                'session_id': session_id,
                'contexto_plan': plan
            })
            
            # Guardar resultado en memoria de trabajo
            resultados_tareas.append(resultado)
            await self.sm3.guardar_contexto(
                session_id, 
                f"resultado_{tarea['id']}", 
                resultado
            )
            
            # Manejar errores críticos
            if not resultado.get('exito', False) and tarea.get('critica', False):
                raise Exception(f"Tarea crítica fallida: {tarea['id']}")
        
        return resultados_tareas
    
    async def _fase_recoleccion(self, objetivo: str, plan: Dict, resultados: List[Dict], 
                              session_id: str) -> str:
        """Ejecuta la fase de recolección del ciclo PERA"""
        # Obtener contexto completo de la sesión
        contexto_completo = await self.sm3.obtener_contexto_completo(session_id)
        
        # Crear episodio para memoria episódica
        episodio = {
            'objetivo': objetivo,
            'plan_ejecutado': plan,
            'resultados_tareas': resultados,
            'contexto_ejecucion': contexto_completo,
            'metricas': self._calcular_metricas_episodio(resultados),
            'session_id': session_id,
            'timestamp': datetime.now().isoformat()
        }
        
        # Guardar en memoria episódica
        episodio_id = await self.sm3.guardar_episodio(episodio)
        
        # Limpiar memoria de trabajo
        await self.sm3.limpiar_sesion(session_id)
        
        return episodio_id
    
    async def _fase_aprendizaje(self, episodio_id: str):
        """Ejecuta la fase de aprendizaje del ciclo PERA (asíncrono)"""
        try:
            # Obtener episodio completo
            episodio = await self.sm3.obtener_episodio(episodio_id)
            
            # Analizar para aprendizaje
            insights = await self.mao.analizar_episodio(episodio)
            
            # Aplicar optimizaciones si las hay
            if insights.get('optimizaciones'):
                await self.mao.aplicar_optimizaciones(insights['optimizaciones'])
            
            logger.info(f"Análisis de aprendizaje completado para episodio {episodio_id}")
            
        except Exception as e:
            logger.error(f"Error en fase de aprendizaje para episodio {episodio_id}: {e}")