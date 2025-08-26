from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXInstrumentor
import logging
from typing import Dict, Any

class SistemaMonitorizacion:
    """Sistema de monitorización distribuida para SAAM"""
    
    def __init__(self, config_monitorizacion: Dict[str, Any]):
        self.config = config_monitorizacion
        self.tracer_provider = TracerProvider()
        self._configurar_exportadores()
        
    def _configurar_exportadores(self):
        """Configura los exportadores de tracing"""
        if self.config.get('otlp', {}).get('enabled', False):
            otlp_exporter = OTLPSpanExporter(
                endpoint=self.config['otlp']['endpoint'],
                insecure=self.config['otlp'].get('insecure', True)
            )
            span_processor = BatchSpanProcessor(otlp_exporter)
            self.tracer_provider.add_span_processor(span_processor)
        
        trace.set_tracer_provider(self.tracer_provider)
    
    def instrumentar_aplicacion(self, app):
        """Instrumenta una aplicación FastAPI"""
        FastAPIInstrumentor.instrument_app(app)
        HTTPXInstrumentor().instrument()
        
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        return app
    
    def obtener_tracer(self, nombre_modulo: str):
        """Obtiene un tracer para un módulo específico"""
        return trace.get_tracer(nombre_modulo)