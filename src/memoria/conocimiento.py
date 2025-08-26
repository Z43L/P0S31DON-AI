from typing import Dict, List, Any, Optional, Tuple
import chromadb
from chromadb.config import Settings
import json
from datetime import datetime
from loguru import logger

class BaseConocimiento:
    """
    Sistema de gestión de la base de conocimiento y habilidades de SAAM.
    Almacena procedimientos, recetas y estrategias de ejecución probadas.
    """
    
    def __init__(self, configuracion: Dict[str, Any]):
        self.config = configuracion
        self.ruta_bd = configuracion.get('ruta_bd', './data/conocimiento')
        self._inicializar_cliente()
        self._inicializar_colecciones()
        
        logger.info("Base de Conocimiento inicializada correctamente")
    
    def _inicializar_cliente(self):
        """Inicializa el cliente de ChromaDB con configuración optimizada"""
        self.client = chromadb.PersistentClient(
            path=self.ruta_bd,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=False
            )
        )
    
    def _inicializar_colecciones(self):
        """Inicializa las colecciones principales de la base de conocimiento"""
        # Colección principal de habilidades
        self.coleccion_habilidades = self.client.get_or_create_collection(
            name="habilidades",
            metadata={
                "description": "Habilidades y procedimientos aprendidos por SAAM",
                "version": "1.0"
            }
        )
        
        # Colección de métricas de rendimiento
        self.coleccion_metricas = self.client.get_or_create_collection(
            name="metricas_rendimiento",
            metadata={
                "description": "Métricas de rendimiento de habilidades",
                "version": "1.0"
            }
        )
        
        # Colección de relaciones semánticas
        self.coleccion_relaciones = self.client.get_or_create_collection(
            name="relaciones_semanticas",
            metadata={
                "description": "Relaciones semánticas entre habilidades",
                "version": "1.0"
            }
        )
    
    async def guardar_habilidad(self, habilidad: Dict[str, Any]) -> str:
        """
        Guarda una nueva habilidad en la base de conocimiento.
        
        Args:
            habilidad: Diccionario con la definición completa de la habilidad
        
        Returns:
            str: ID único de la habilidad guardada
        """
        try:
            # Validar y normalizar la habilidad
            habilidad_validada = self._validar_habilidad(habilidad)
            habilidad_id = self._generar_id_habilidad(habilidad_validada)
            
            # Preparar documentos para almacenamiento
            documento = json.dumps(habilidad_validada)
            embedding = self._generar_embedding_habilidad(habilidad_validada)
            
            # Guardar en ChromaDB
            self.coleccion_habilidades.add(
                documents=[documento],
                embeddings=[embedding],
                ids=[habilidad_id],
                metadatas=[{
                    'tipo': habilidad_validada.get('tipo', 'procedimiento'),
                    'categoria': habilidad_validada.get('categoria', 'general'),
                    'timestamp_creacion': datetime.now().isoformat(),
                    'version': '1.0'
                }]
            )
            
            logger.info(f"Habilidad guardada: {habilidad_id}")
            return habilidad_id
            
        except Exception as e:
            logger.error(f"Error guardando habilidad: {e}")
            raise
    
    def _validar_habilidad(self, habilidad: Dict) -> Dict:
        """Valida la estructura de una habilidad antes de almacenarla"""
        campos_requeridos = ['nombre', 'tipo', 'procedimiento']
        for campo in campos_requeridos:
            if campo not in habilidad:
                raise ValueError(f"Campo requerido faltante: {campo}")
        
        # Validar estructura del procedimiento
        if not isinstance(habilidad['procedimiento'], list):
            raise ValueError("El procedimiento debe ser una lista de pasos")
        
        return habilidad
    
    def _generar_id_habilidad(self, habilidad: Dict) -> str:
        """Genera un ID único para una habilidad basado en su contenido"""
        import hashlib
        contenido = f"{habilidad['nombre']}_{habilidad['tipo']}_{datetime.now().timestamp()}"
        return f"habilidad_{hashlib.md5(contenido.encode()).hexdigest()[:12]}"
    
    def _generar_embedding_habilidad(self, habilidad: Dict) -> List[float]:
        """Genera embedding semántico para una habilidad"""
        # Texto para embedding: nombre + descripción + objetivos
        texto_embedding = f"{habilidad.get('nombre', '')} {habilidad.get('descripcion', '')}"
        if 'objetivos' in habilidad:
            texto_embedding += " " + " ".join(habilidad['objetivos'])
        
        # Usar modelo de embedding configurado
        # (Implementación real usaría un modelo como sentence-transformers)
        return self._modelo_embedding.encode(texto_embedding)