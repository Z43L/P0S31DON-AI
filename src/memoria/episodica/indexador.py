from typing import Dict, List, Any, Optional
from datetime import datetime
from loguru import logger

class IndexadorEpisodios:
    """Sistema de indexación para búsqueda eficiente en memoria episódica"""
    
    def __init__(self, gestor_episodica, configuracion: Dict[str, Any]):
        self.gestor = gestor_episodica
        self.config = configuracion
        self.indices: Dict[str, Any] = {}
        self._inicializar_indices()
    
    def _inicializar_indices(self):
        """Inicializa los índices para búsqueda rápida"""
        self.indices = {
            'por_estado': {},
            'por_objetivo': {},
            'por_session': {},
            'por_fecha': {},
            'por_rendimiento': {}
        }
    
    async def indexar_episodio(self, episodio: Dict[str, Any]):
        """
        Indexa un episodio para búsquedas futuras.
        
        Args:
            episodio: Episodio a indexar
        """
        try:
            # Índice por estado
            estado = episodio.get('estado_global', 'desconocido')
            if estado not in self.indices['por_estado']:
                self.indices['por_estado'][estado] = []
            self.indices['por_estado'][estado].append(episodio['id'])
            
            # Índice por objetivo (tokens)
            objetivo = episodio.get('objetivo', '')
            tokens = self._extraer_tokens(objetivo)
            for token in tokens:
                if token not in self.indices['por_objetivo']:
                    self.indices['por_objetivo'][token] = []
                self.indices['por_objetivo'][token].append(episodio['id'])
            
            # Índice por sesión
            session_id = episodio.get('session_id')
            if session_id:
                if session_id not in self.indices['por_session']:
                    self.indices['por_session'][session_id] = []
                self.indices['por_session'][session_id].append(episodio['id'])
            
            # Índice por fecha
            fecha = episodio.get('timestamp_creacion').date() if episodio.get('timestamp_creacion') else None
            if fecha:
                fecha_str = fecha.isoformat()
                if fecha_str not in self.indices['por_fecha']:
                    self.indices['por_fecha'][fecha_str] = []
                self.indices['por_fecha'][fecha_str].append(episodio['id'])
            
            # Índice por rendimiento
            rendimiento = episodio.get('metricas_rendimiento', {}).get('puntuacion_global', 0.5)
            banda_rendimiento = self._categorizar_rendimiento(rendimiento)
            if banda_rendimiento not in self.indices['por_rendimiento']:
                self.indices['por_rendimiento'][banda_rendimiento] = []
            self.indices['por_rendimiento'][banda_rendimiento].append(episodio['id'])
            
            logger.debug(f"Episodio indexado: {episodio['id']}")
            
        except Exception as e:
            logger.error(f"Error indexando episodio: {e}")
    
    def _extraer_tokens(self, texto: str) -> List[str]:
        """Extrae tokens significativos de un texto"""
        import re
        # Eliminar stopwords y tokenizar
        palabras = re.findall(r'\b[a-záéíóúñ]{3,}\b', texto.lower())
        stopwords = {'con', 'para', 'por', 'de', 'la', 'el', 'en', 'y', 'a', 'los', 'las'}
        return [p for p in palabras if p not in stopwords]
    
    def _categorizar_rendimiento(self, rendimiento: float) -> str:
        """Categoriza el rendimiento en bandas"""
        if rendimiento >= 0.8:
            return "excelente"
        elif rendimiento >= 0.6:
            return "bueno"
        elif rendimiento >= 0.4:
            return "regular"
        else:
            return "deficiente"
    
    async def buscar_episodios(self, criterios: Dict[str, Any]) -> List[str]:
        """
        Busca episodios que coincidan con los criterios especificados.
        
        Args:
            criterios: Diccionario con criterios de búsqueda
        
        Returns:
            List[str]: Lista de IDs de episodios que coinciden
        """
        try:
            conjuntos_ids = []
            
            # Búsqueda por estado
            if 'estado' in criterios:
                estado_ids = self.indices['por_estado'].get(criterios['estado'], [])
                conjuntos_ids.append(set(estado_ids))
            
            # Búsqueda por objetivo
            if 'objetivo_contiene' in criterios:
                tokens = self._extraer_tokens(criterios['objetivo_contiene'])
                objetivo_ids = set()
                for token in tokens:
                    if token in self.indices['por_objetivo']:
                        objetivo_ids.update(self.indices['por_objetivo'][token])
                conjuntos_ids.append(objetivo_ids)
            
            # Búsqueda por sesión
            if 'session_id' in criterios:
                session_ids = self.indices['por_session'].get(criterios['session_id'], [])
                conjuntos_ids.append(set(session_ids))
            
            # Búsqueda por fecha
            if 'fecha' in criterios:
                fecha_str = criterios['fecha'].isoformat() if hasattr(criterios['fecha'], 'isoformat') else criterios['fecha']
                fecha_ids = self.indices['por_fecha'].get(fecha_str, [])
                conjuntos_ids.append(set(fecha_ids))
            
            # Búsqueda por rendimiento
            if 'rendimiento_minimo' in criterios:
                bandas_relevantes = self._obtener_bandas_relevantes(criterios['rendimiento_minimo'])
                rendimiento_ids = set()
                for banda in bandas_relevantes:
                    if banda in self.indices['por_rendimiento']:
                        rendimiento_ids.update(self.indices['por_rendimiento'][banda])
                conjuntos_ids.append(rendimiento_ids)
            
            # Intersección de todos los criterios
            if conjuntos_ids:
                ids_coincidentes = set.intersection(*conjuntos_ids)
                return list(ids_coincidentes)
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error en búsqueda: {e}")
            return []