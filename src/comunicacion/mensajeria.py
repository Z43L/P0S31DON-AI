import asyncio
import aio_pika
import json
from typing import Dict, Any, Callable, Optional
from loguru import logger

class SistemaMensajeria:
    """Sistema de mensajería asíncrona para comunicación entre módulos"""
    
    def __init__(self, config_rabbitmq: Dict[str, Any]):
        self.config = config_rabbitmq
        self.conexion: Optional[aio_pika.Connection] = None
        self.canal: Optional[aio_pika.Channel] = None
        self.colas_declaradas = set()
    
    async def conectar(self):
        """Establece conexión con RabbitMQ"""
        try:
            self.conexion = await aio_pika.connect_robust(
                host=self.config.get('host', 'localhost'),
                port=self.config.get('port', 5672),
                login=self.config.get('username', 'guest'),
                password=self.config.get('password', 'guest'),
                virtualhost=self.config.get('virtualhost', '/')
            )
            
            self.canal = await self.conexion.channel()
            await self.canal.set_qos(prefetch_count=10)
            
            logger.success("Conexión a RabbitMQ establecida exitosamente")
            
        except Exception as e:
            logger.error(f"Error conectando a RabbitMQ: {e}")
            raise
    
    async def declarar_exchange(self, nombre_exchange: str, tipo: str = 'topic') -> None:
        """Declara un exchange en RabbitMQ"""
        if self.canal:
            exchange = await self.canal.declare_exchange(
                nombre_exchange,
                type=tipo,
                durable=True
            )
            logger.debug(f"Exchange '{nombre_exchange}' declarado")
    
    async def publicar_mensaje(
        self,
        exchange: str,
        routing_key: str,
        mensaje: Dict[str, Any],
        propiedades: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Publica un mensaje en el sistema de mensajería.
        
        Args:
            exchange: Nombre del exchange
            routing_key: Clave de routing
            mensaje: Contenido del mensaje
            propiedades: Propiedades adicionales del mensaje
        """
        if not self.canal:
            raise RuntimeError("Canal no inicializado")
        
        try:
            exchange_obj = await self.canal.get_exchange(exchange)
            
            propiedades_msg = aio_pika.Message(
                body=json.dumps(mensaje).encode(),
                content_type='application/json',
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                **(propiedades or {})
            )
            
            await exchange_obj.publish(propiedades_msg, routing_key=routing_key)
            logger.debug(f"Mensaje publicado en {exchange} con clave {routing_key}")
            
        except Exception as e:
            logger.error(f"Error publicando mensaje: {e}")
            raise
    
    async def consumir_mensajes(
        self,
        nombre_cola: str,
        callback: Callable[[Dict[str, Any], aio_pika.Message], None],
        auto_ack: bool = False
    ) -> None:
        """
        Configura un consumidor para procesar mensajes de una cola.
        
        Args:
            nombre_cola: Nombre de la cola a consumir
            callback: Función callback para procesar mensajes
            auto_ack: Si se confirma automáticamente la recepción
        """
        if not self.canal:
            raise RuntimeError("Canal no inicializado")
        
        try:
            cola = await self.canal.declare_queue(nombre_cola, durable=True)
            self.colas_declaradas.add(nombre_cola)
            
            async def wrapper_callback(mensaje: aio_pika.IncomingMessage):
                async with mensaje.process():
                    try:
                        contenido = json.loads(mensaje.body.decode())
                        await callback(contenido, mensaje)
                        if not auto_ack:
                            await mensaje.ack()
                    except Exception as e:
                        logger.error(f"Error procesando mensaje: {e}")
                        if not auto_ack:
                            await mensaje.nack(requeue=False)
            
            await cola.consume(wrapper_callback)
            logger.info(f"Consumiendo mensajes de la cola '{nombre_cola}'")
            
        except Exception as e:
            logger.error(f"Error configurando consumidor: {e}")
            raise
    
    async def desconectar(self):
        """Cierra la conexión con RabbitMQ"""
        if self.conexion:
            await self.conexion.close()
            logger.info("Conexión a RabbitMQ cerrada")