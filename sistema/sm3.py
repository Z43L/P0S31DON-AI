class SistemaMemoriaTripleCapa:
    def __init__(self, cliente_db_episodios, cliente_db_conocimiento):
        self.memoria_trabajo = {}  # Dict en memoria para la sesión actual
        self.db_conocimiento = cliente_db_conocimiento  # Cliente para la DB de habilidades/procedimientos
        self.db_episodios = cliente_db_episodios        # Cliente para la DB de logs inmutables

    def registrar_episodio(self, objetivo, plan, resultados, feedback_usuario):
        """
        Guarda un registro completo (episodio) de una ejecución en la memoria episódica.
        """
        episodio = {
            "timestamp": datetime.now().isoformat(),
            "objetivo": objetivo,
            "plan": plan,
            "resultados": resultados,
            "feedback_usuario": feedback_usuario,
            "metricas": self._calcular_metricas(resultados, feedback_usuario)
        }
        self.db_episodios.insert(episodio)

    def consultar_habilidades(self, tipo_tarea: str) -> list:
        """
        Consulta la Base de Conocimiento para encontrar habilidades relevantes para un tipo de tarea.
        """
        return self.db_conocimiento.query("tipo_tarea", tipo_tarea)