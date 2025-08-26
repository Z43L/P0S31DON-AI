class ModuloEjecucionTareas:
    def __init__(self, herramientas_registradas, configuracion_optimizacion):
        self.herramientas = herramientas_registradas
        self.config = configuracion_optimizacion

    def ejecutar(self, tarea: dict) -> dict:
        """
        Ejecuta una única tarea y devuelve su resultado y metadatos de ejecución.
        """
        # Obtener parámetros de la tarea
        herramienta_id = tarea.get('herramienta')
        parametros = tarea.get('parametros', {})
        
        # Lógica de selección de herramienta si no está explícitamente definida
        if not herramienta_id:
            herramienta_id = self._seleccionar_mejor_herramienta(tarea.get('tipo'))
        
        herramienta = self.herramientas[herramienta_id]
        
        # Ejecución cronometrada con manejo de excepciones
        inicio = time.time()
        try:
            resultado = herramienta.ejecutar(**parametros)
            exito = True
            error_msg = None
        except Exception as e:
            resultado = None
            exito = False
            error_msg = str(e)
        fin = time.time()
        
        duracion = fin - inicio
        
        # Empaquetar resultado y metadatos
        return {
            'resultado': resultado,
            'metadatos': {
                'exito': exito,
                'herramienta': herramienta_id,
                'duracion': duracion,
                'error': error_msg
            }
        }