from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import sqlalchemy as sa
from sqlalchemy import create_engine, Column, String, JSON, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from loguru import logger

Base = declarative_base()

class EpisodioDB(Base):
    """Modelo de base de datos para episodios"""
    __tablename__ = 'episodios'
    
    id = Column(String, primary_key=True)
    timestamp_creacion = Column(DateTime, default=datetime.utcnow)
    objetivo = Column(String, nullable=False)
    session_id = Column(String, nullable=False)
    plan_ejecutado = Column(JSON, nullable=False)
    resultados_tareas = Column(JSON, nullable=False)
    estado_global = Column(String, nullable=False)
    duracion_total = Column(Float, nullable=False)
    contexto_ejecucion = Column(JSON)
    metricas_rendimiento = Column(JSON)
    recursos_utilizados = Column(JSON)
    timestamp_inicio = Column(DateTime, nullable=False)
    timestamp_fin = Column(DateTime, nullable=False)
    version_sistema = Column(String, nullable=False)
    checksum_integridad = Column(String, nullable=False)
    feedback_usuario = Column(JSON)
    evaluacion_automatica = Column(JSON)

class GestorMemoriaEpisodica:
    """Gestor principal de la memoria episódica"""
    
    def __init__(self, configuracion: Dict[str, Any]):
        self.config = configuracion
        self.cadena_conexion = configuracion.get('cadena_conexion', 'sqlite:///./data/episodica.db')
        self.engine = create_engine(self.cadena_conexion)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        logger.info("Gestor de Memoria Episódica inicializado")
    
    async def guardar_episodio(self, episodio: Dict[str, Any]) -> str:
        """
        Guarda un episodio completo en la memoria episódica.
        
        Args:
            episodio: Diccionario con los datos del episodio
        
        Returns:
            str: ID del episodio guardado
        """
        session = self.Session()
        try:
            # Validar estructura básica
            if 'id' not in episodio:
                episodio['id'] = self._generar_id_episodio()
            
            # Crear objeto de base de datos
            episodio_db = EpisodioDB(
                id=episodio['id'],
                objetivo=episodio.get('objetivo', ''),
                session_id=episodio.get('session_id', ''),
                plan_ejecutado=episodio.get('plan_ejecutado', {}),
                resultados_tareas=episodio.get('resultados_tareas', []),
                estado_global=episodio.get('estado_global', 'desconocido'),
                duracion_total=episodio.get('duracion_total_segundos', 0),
                contexto_ejecucion=episodio.get('contexto_ejecucion', {}),
                metricas_rendimiento=episodio.get('metricas_rendimiento', {}),
                recursos_utilizados=episodio.get('recursos_utilizados', {}),
                timestamp_inicio=episodio.get('timestamp_inicio'),
                timestamp_fin=episodio.get('timestamp_fin'),
                version_sistema=episodio.get('version_sistema', ''),
                checksum_integridad=episodio.get('checksum_integridad', ''),
                feedback_usuario=episodio.get('feedback_usuario'),
                evaluacion_automatica=episodio.get('evaluacion_automatica', {})
            )
            
            session.add(episodio_db)
            session.commit()
            
            logger.info(f"Episodio guardado: {episodio['id']}")
            return episodio['id']
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error guardando episodio: {e}")
            raise
        finally:
            session.close()
    
    def _generar_id_episodio(self) -> str:
        """Genera un ID único para el episodio"""
        from datetime import datetime
        import hashlib
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        random_component = hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:8]
        return f"episodio_{timestamp}_{random_component}"
    
    async def obtener_episodio(self, episodio_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un episodio específico por ID.
        
        Args:
            episodio_id: ID del episodio a recuperar
        
        Returns:
            Optional[Dict]: Episodio completo o None si no existe
        """
        session = self.Session()
        try:
            episodio_db = session.query(EpisodioDB).filter(EpisodioDB.id == episodio_id).first()
            if not episodio_db:
                return None
            
            return self._db_a_dict(episodio_db)
            
        finally:
            session.close()
    
    async def obtener_episodios(self, filtros: Optional[Dict] = None, limite: int = 100) -> List[Dict[str, Any]]:
        """
        Obtiene múltiples episodios con filtros opcionales.
        
        Args:
            filtros: Diccionario con criterios de filtrado
            limite: Número máximo de resultados
        
        Returns:
            List[Dict]: Lista de episodios que coinciden con los filtros
        """
        session = self.Session()
        try:
            query = session.query(EpisodioDB)
            
            # Aplicar filtros
            if filtros:
                if 'estado' in filtros:
                    query = query.filter(EpisodioDB.estado_global == filtros['estado'])
                if 'desde' in filtros:
                    query = query.filter(EpisodioDB.timestamp_creacion >= filtros['desde'])
                if 'hasta' in filtros:
                    query = query.filter(EpisodioDB.timestamp_creacion <= filtros['hasta'])
                if 'objetivo_contiene' in filtros:
                    query = query.filter(EpisodioDB.objetivo.contains(filtros['objetivo_contiene']))
                if 'session_id' in filtros:
                    query = query.filter(EpisodioDB.session_id == filtros['session_id'])
            
            episodios_db = query.order_by(EpisodioDB.timestamp_creacion.desc()).limit(limite).all()
            
            return [self._db_a_dict(ep) for ep in episodios_db]
            
        finally:
            session.close()
    
    def _db_a_dict(self, episodio_db: EpisodioDB) -> Dict[str, Any]:
        """Convierte un objeto de base de datos a diccionario"""
        return {
            'id': episodio_db.id,
            'objetivo': episodio_db.objetivo,
            'session_id': episodio_db.session_id,
            'plan_ejecutado': episodio_db.plan_ejecutado,
            'resultados_tareas': episodio_db.resultados_tareas,
            'estado_global': episodio_db.estado_global,
            'duracion_total_segundos': episodio_db.duracion_total,
            'contexto_ejecucion': episodio_db.contexto_ejecucion,
            'metricas_rendimiento': episodio_db.metricas_rendimiento,
            'recursos_utilizados': episodio_db.recursos_utilizados,
            'timestamp_inicio': episodio_db.timestamp_inicio,
            'timestamp_fin': episodio_db.timestamp_fin,
            'version_sistema': episodio_db.version_sistema,
            'checksum_integridad': episodio_db.checksum_integridad,
            'feedback_usuario': episodio_db.feedback_usuario,
            'evaluacion_automatica': episodio_db.evaluacion_automatica,
            'timestamp_creacion': episodio_db.timestamp_creacion
        }