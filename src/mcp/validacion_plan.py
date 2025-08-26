from typing import Dict, List, Any, Optional, Tuple
import networkx as nx
from loguru import logger

class ValidadorPlan:
    """Sistema de validación y optimización de planes generados"""
    
    def __init__(self, configuracion: Dict[str, Any]):
        self.config = configuracion
        self.reglas_validacion = self._cargar_reglas_validacion()
    
    async def validar_plan(self, plan: Dict) -> Tuple[bool, List[str]]:
        """
        Valida un plan contra un conjunto de reglas de consistencia y viabilidad.
        
        Args:
            plan: Plan a validar
        
        Returns:
            Tuple: (Resultado de validación, Lista de errores)
        """
        errores = []
        
        for regla in self.reglas_validacion:
            try:
                valido, mensaje = regla['funcion'](plan)
                if not valido:
                    errores.append(f"{regla['nombre']}: {mensaje}")
            except Exception as e:
                errores.append(f"Error ejecutando regla {regla['nombre']}: {str(e)}")
        
        return len(errores) == 0, errores
    
    async def optimizar_plan(self, plan: Dict) -> Dict:
        """
        Aplica optimizaciones al plan basado en mejores prácticas y aprendizaje.
        
        Args:
            plan: Plan a optimizar
        
        Returns:
            Dict: Plan optimizado
        """
        plan_optimizado = plan.copy()
        
        # Aplicar optimizaciones secuenciales
        plan_optimizado = await self._optimizar_secuencia(plan_optimizado)
        plan_optimizado = await self._optimizar_asignacion_recursos(plan_optimizado)
        plan_optimizado = await self._optimizar_parametros(plan_optimizado)
        
        return plan_optimizado
    
    async def _optimizar_secuencia(self, plan: Dict) -> Dict:
        """Optimiza la secuencia de ejecución de tareas"""
        tareas = plan.get('tareas', [])
        
        # Crear grafo de dependencias
        grafo = nx.DiGraph()
        for tarea in tareas:
            tarea_id = tarea.get('id')
            if tarea_id:
                grafo.add_node(tarea_id)
                for dep in tarea.get('dependencias', []):
                    grafo.add_edge(dep, tarea_id)
        
        # Ordenar topológicamente
        try:
            orden_optimo = list(nx.topological_sort(grafo))
            tareas_ordenadas = sorted(tareas, key=lambda x: orden_optimo.index(x['id']))
            plan['tareas'] = tareas_ordenadas
        except nx.NetworkXUnfeasible:
            logger.warning("Ciclo detectado en dependencias, manteniendo orden original")
        
        return plan
    
    def _cargar_reglas_validacion(self) -> List[Dict]:
        """Carga las reglas de validación para planes"""
        return [
            {
                "nombre": "tareas_minimo",
                "descripcion": "El plan debe tener al menos una tarea",
                "funcion": self._validar_minimo_tareas
            },
            {
                "nombre": "dependencias_validas",
                "descripcion": "Las dependencias deben ser válidas",
                "funcion": self._validar_dependencias
            },
            {
                "nombre": "recursos_suficientes",
                "descripcion": "Deben existir recursos para todas las tareas",
                "funcion": self._validar_recursos
            }
        ]
    
    def _validar_minimo_tareas(self, plan: Dict) -> Tuple[bool, str]:
        """Valida que el plan tenga al menos una tarea"""
        tareas = plan.get('tareas', [])
        if len(tareas) == 0:
            return False, "El plan no contiene tareas"
        return True, ""