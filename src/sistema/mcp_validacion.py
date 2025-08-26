from typing import Dict, List, Any, Tuple
import networkx as nx
from loguru import logger

class ValidadorOptimizadorPlanes:
    """Clase para validar y optimizar planes generados"""
    
    def __init__(self, configuracion: Dict[str, Any]):
        self.config = configuracion
        self.reglas_validacion = self._cargar_reglas_validacion()
    
    def _cargar_reglas_validacion(self) -> List[Dict]:
        """Carga las reglas de validación para planes"""
        return [
            {
                "nombre": "tareas_minimo",
                "descripcion": "El plan debe tener al menos una tarea",
                "funcion": self._validar_minimo_tareas
            },
            {
                "nombre": "dependencias_ciclicas",
                "descripcion": "No debe haber ciclos en las dependencias",
                "funcion": self._validar_dependencias_ciclicas
            },
            {
                "nombre": "recursos_disponibles",
                "descripcion": "Las herramientas especificadas deben estar disponibles",
                "funcion": self._validar_recursos_disponibles
            }
        ]
    
    def validar_plan(self, plan: Dict) -> Tuple[bool, List[str]]:
        """Valida un plan contra todas las reglas"""
        errores = []
        
        for regla in self.reglas_validacion:
            try:
                valido, mensaje = regla["funcion"](plan)
                if not valido:
                    errores.append(f"{regla['nombre']}: {mensaje}")
            except Exception as e:
                errores.append(f"Error ejecutando regla {regla['nombre']}: {str(e)}")
        
        return len(errores) == 0, errores
    
    def _validar_minimo_tareas(self, plan: Dict) -> Tuple[bool, str]:
        """Valida que el plan tenga al menos una tarea"""
        tareas = plan.get('tareas', [])
        if len(tareas) == 0:
            return False, "El plan no contiene tareas"
        return True, ""
    
    def _validar_dependencias_ciclicas(self, plan: Dict) -> Tuple[bool, str]:
        """Valida que no haya ciclos en las dependencias entre tareas"""
        grafo = nx.DiGraph()
        
        for tarea in plan.get('tareas', []):
            tarea_id = tarea.get('id')
            if tarea_id:
                grafo.add_node(tarea_id)
                for dep in tarea.get('dependencias', []):
                    grafo.add_edge(dep, tarea_id)
        
        try:
            ciclos = list(nx.simple_cycles(grafo))
            if ciclos:
                return False, f"Se detectaron ciclos en las dependencias: {ciclos}"
            return True, ""
        except nx.NetworkXNoCycle:
            return True, ""
    
    def _validar_recursos_disponibles(self, plan: Dict) -> Tuple[bool, str]:
        """Valida que las herramientas especificadas estén disponibles"""
        herramientas_disponibles = {'busqueda_web', 'generacion_texto', 'api_rest'}
        herramientas_plan = set()
        
        for tarea in plan.get('tareas', []):
            herramienta = tarea.get('herramienta')
            if herramienta:
                herramientas_plan.add(herramienta)
        
        herramientas_no_disponibles = herramientas_plan - herramientas_disponibles
        if herramientas_no_disponibles:
            return False, f"Herramientas no disponibles: {herramientas_no_disponibles}"
        
        return True, ""
    
    def optimizar_plan(self, plan: Dict) -> Dict:
        """Aplica optimizaciones al plan"""
        plan_optimizado = plan.copy()
        
        plan_optimizado = self._optimizar_secuencia(plan_optimizado)
        plan_optimizado = self._optimizar_recursos(plan_optimizado)
        plan_optimizado = self._optimizar_parametros(plan_optimizado)
        
        return plan_optimizado
    
    def _optimizar_secuencia(self, plan: Dict) -> Dict:
        """Optimiza la secuencia de ejecución de tareas"""
        tareas = plan['tareas']
        tareas_ordenadas = sorted(tareas, key=lambda x: len(x.get('dependencias', [])))
        plan['tareas'] = tareas_ordenadas
        return plan
    
    def _optimizar_recursos(self, plan: Dict) -> Dict:
        """Optimiza la asignación de recursos/herramientas"""
        return plan
    
    def _optimizar_parametros(self, plan: Dict) -> Dict:
        """Optimiza parámetros basado en experiencias pasadas"""
        return plan