class ModuloAprendizajeOptimizacion:
    def __init__(self, cliente_memoria):
        self.memoria = cliente_memoria
        self.analizador = AnalizadorEstadistico()

    def analizar_episodios_recientes(self):
        """
        Función que se ejecuta periódicamente (ej: cada 24h) para aprender de experiencias recientes.
        """
        episodios_recientes = self.memoria.db_episodios.obtener_recientes(horas=24)
        
        # Agrupar episodios por tipo de tarea para análisis específico
        for tipo_tarea in self._identificar_tipos_tarea_comunes(episodios_recientes):
            episodios_filtrados = [e for e in episodios_recientes if tipo_tarea in e['objetivo']]
            
            # Analizar correlaciones entre herramientas utilizadas y éxito de la tarea
            correlaciones = self.analizador.encontrar_correlaciones_herramienta_exito(episodios_filtrados)
            
            # Actualizar preferencias de herramientas si se encuentra una óptima
            if correlaciones['herramienta_optima']:
                self.memoria.db_conocimiento.actualizar_preferencia_herramienta(
                    tipo_tarea, 
                    correlaciones['herramienta_optima']
                )
            
            # Generalizar planes exitosos recurrentes en nuevas habilidades
            planes_exitosos = [e['plan'] for e in episodios_filtrados if e['metricas']['exito'] > 0.8]
            if len(planes_exitosos) > 2: # Umbral mínimo de recurrencia
                nueva_habilidad = self._abstract_plantilla(planes_exitosos)
                self.memoria.db_conocimiento.insertar_habilidad(nueva_habilidad)