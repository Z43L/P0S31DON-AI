class ModuloComprensionPlanificacion:
    def __init__(self, cliente_llm, cliente_memoria):
        self.llm = cliente_llm
        self.memoria = cliente_memoria

    def generar_plan(self, objetivo_usuario: str, contexto: dict = None) -> dict:
        """
        Función principal para generar un plan de tareas para un objetivo dado.
        Consulta la memoria para encontrar planes similares o genera uno nuevo.
        """
        # 1. Consultar la Base de Conocimiento para planes similares
        planes_similares = self.memoria.consultar_habilidades(objetivo_usuario)
        
        if planes_similares:
            # Adaptar un plan existente encontrado
            plan_bruto = self.llm.refinar_plan(planes_similares[0], objetivo_usuario, contexto)
        else:
            # Crear un nuevo plan desde cero mediante razonamiento
            prompt_planificacion = self._construir_prompt_planificacion(objetivo_usuario, contexto)
            plan_bruto = self.llm.generar(prompt_planificacion)
        
        # 2. Parsear y estructurar la respuesta del LLM en un formato estandarizado
        plan_estructurado = self._parsear_plan(plan_bruto)
        return plan_estructurado

    def _construir_prompt_planificacion(self, objetivo, contexto):
        # Lógica para construir un prompt instructivo y contextualizado
        return prompt