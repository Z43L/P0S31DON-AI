from typing import Dict, Any, Optional
import aio_pika
from loguru import logger

class GestorComunicacion:
    """Gestor centralizado de comunicación entre módulos SAAM"""
    
    def __init__(self, configuracion: Dict[str, Any]):
        self.config = configuracion
        self.conexion: Optional[aio_pika.Connection] = None
        self.canales: Dict[str, Any] = {}
        
    async def inicializar_comunicacion(self) -> bool:
        """
        Inicializa el sistema de comunicación entre módulos.
        
        Returns:
            bool: True si la inicialización fue exitosa
        """
        try:
            protocolo = self.config.get('comunicacion', {}).get('protocolo', 'rest')
            
            if protocolo == 'rabbitmq':
                return await self._inicializar_rabbitmq()
            else:
                return await self._inicializar_rest()
                
        except Exception as e:
            logger.error(f"Error inicializando comunicación: {e}")
            return False
    
    async def _inicializar_rabbitmq(self) -> bool:
        """Inicializa comunicación via RabbitMQ"""
        config_rabbit = self.config.get('comunicacion', {}).get('rabbitmq', {})
        
        try:
            self.conexion = await aio_pika.connect_robust(
                host=config_rabbit.get('host', 'localhost'),
                port=config_rabbit.get('port', 5672),
                login=config_rabbit.get('username', 'guest'),
                password=config_rabbit.get('password', 'guest'),
                virtualhost=config_rabbit.get('vhost', '/')
            )
            
            # Crear canales para cada módulo
            await self._crear_canales_rabbitmq()
            
            logger.success("Comunicación RabbitMQ inicializada exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error inicializando RabbitMQ: {e}")
            return False
    
    async def _crear_canales_rabbitmq(self):
        """Crea los canales y exchanges necesarios para RabbitMQ"""
        # Canal para MCP
        canal_mcp = await self.conexion.channel()
        await canal_mcp.declare_exchange('mcp_commands', 'direct')
        self.canales['mcp'] = canal_mcp
        
        # Canal para MET
        canal_met = await self.conexion.channel()  
        await canal_met.declare_exchange('met_tasks', 'direct')
        self.canales['met'] = canal_met
        
        # Canal para eventos del sistema
        canal_eventos = await self.conexion.channel()
        await canal_eventos.declare_exchange('system_events', 'topic')
        self.canales['eventos'] = canal_eventos