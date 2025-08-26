from typing import Dict, List, Any, Optional
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy import create_engine, Column, String, JSON, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from loguru import logger

Base = declarative_base()

class EpisodioDB(Base):
    """Modelo de base de datos para episodios de ejecución"""
    __tablename__ = 'episodios'
    
    id = Column(String, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    objetivo = Column(String, nullable=False)
    plan_ejecutado = Column(JSON, nullable=False)
    resultados = Column(JSON, nullable=False)
    feedback_usuario = Column(JSON)
    metricas = Column(JSON)
    duracion_total = Column(Float)
    estado = Column(String)  # 'exito', 'fracaso', 'parcial'

class MemoriaEpisodica:
    """Gestiona el almacenamiento inmutable de episodios de ejecución"""
    
    def __init__(self, cadena_conexion: str = "sqlite:///./data/episodica.db"):
        self.engine = create_engine(cadena_conexion)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def guardar_episodio(self, episodio: Dict[str, Any]) -> str:
        """Guarda un episodio completo en la memoria episódica"""
        session = self.Session()
        try:
            # Generar ID único
            episodio_id = f"episodio_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(str(episodio)) % 10000:04d}"
            
            # Crear objeto de base de datos
            episodio_db = EpisodioDB(
                id=episodio_id,
                objetivo=episodio.get('objetivo', ''),
                plan_ejecutado=episodio.get('plan', {}),
                resultados=episodio.get('resultados', {}),
                feedback_usuario=episodio.get('feedback_usuario', {}),
                metricas=episodio.get('metricas', {}),
                duracion_total=episodio.get('duracion_total', 0),
                estado=episodio.get('estado', 'desconocido')
            )
            
            session.add(episodio_db)
            session.commit()
            
            logger.info(f"Episodio guardado: {episodio_id}")
            return episodio_id
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error guardando episodio: {e}")
            raise
        finally:
            session.close()
    
    def obtener_episodios(self, filtros: Optional[Dict] = None, 
                         limite: int = 100) -> List[Dict[str, Any]]:
        """Obtiene episodios con filtros opcionales"""
        session = self.Session()
        try:
            query = session.query(EpisodioDB)
            
            # Aplicar filtros
            if filtros:
                if 'estado' in filtros:
                    query = query.filter(EpisodioDB.estado == filtros['estado'])
                if 'desde' in filtros:
                    query = query.filter(EpisodioDB.timestamp >= filtros['desde'])
                if 'hasta' in filtros:
                    query = query.filter(EpisodioDB.timestamp <= filtros['hasta'])
                if 'objetivo_contiene' in filtros:
                    query = query.filter(EpisodioDB.objetivo.contains(filtros['objetivo_contiene']))
            
            episodios = query.order_by(EpisodioDB.timestamp.desc()).limit(limite).all()
            
            return [{
                'id': ep.id,
                'timestamp': ep.timestamp,
                'objetivo': ep.objetivo,
                'plan': ep.plan_ejecutado,
                'resultados': ep.resultados,
                'feedback_usuario': ep.feedback_usuario,
                'metricas': ep.metricas,
                'duracion_total': ep.duracion_total,
                'estado': ep.estado
            } for ep in episodios]
            
        finally:
            session.close()
    
    def obtener_episodios_por_tipo_tarea(self, tipo_tarea: str, 
                                       limite: int = 50) -> List[Dict[str, Any]]:
        """Obtiene episodios relacionados con un tipo específico de tarea"""
        session = self.Session()
        try:
            # Buscar episodios cuyo objetivo contenga el tipo de tarea
            episodios = session.query(EpisodioDB).filter(
                EpisodioDB.objetivo.contains(tipo_tarea)
            ).order_by(EpisodioDB.timestamp.desc()).limit(limite).all()
            
            return [{
                'id': ep.id,
                'timestamp': ep.timestamp,
                'objetivo': ep.objetivo,
                'estado': ep.estado,
                'metricas': ep.metricas
            } for ep in episodios]
            
        finally:
            session.close()