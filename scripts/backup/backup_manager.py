from datetime import datetime, timedelta
import asyncio
import aiofiles
import json
import logging
from pathlib import Path
from typing import Dict, List

class BackupManager:
    """Sistema de gestión de backups para SAAM"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.backup_dir = Path(config['backup']['directory'])
        self.retention_days = config['backup']['retention_days']
        
    async def ejecutar_backup_completo(self) -> Dict:
        """Ejecuta un backup completo del sistema"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_info = {
            'timestamp': timestamp,
            'componentes': [],
            'estado': 'iniciado',
            'size_total': 0
        }
        
        try:
            # Backup de base de datos de memoria episódica
            db_backup = await self._backup_database()
            backup_info['componentes'].append(db_backup)
            
            # Backup de base de conocimiento
            kb_backup = await self._backup_knowledge_base()
            backup_info['componentes'].append(kb_backup)
            
            # Backup de configuración
            config_backup = await self._backup_configuration()
            backup_info['componentes'].append(config_backup)
            
            # Crear archivo de metadatos del backup
            backup_info['estado'] = 'completado'
            backup_info['size_total'] = sum(c['size'] for c in backup_info['componentes'])
            
            await self._guardar_metadata(backup_info)
            await self._aplicar_politica_retention()
            
            return backup_info
            
        except Exception as e:
            backup_info['estado'] = 'error'
            backup_info['error'] = str(e)
            logging.error(f"Error en backup: {e}")
            return backup_info
    
    async def _aplicar_politica_retention(self):
        """Aplica política de retención de backups"""
        cutoff_time = datetime.now() - timedelta(days=self.retention_days)
        
        for backup_file in self.backup_dir.glob("backup_*"):
            if backup_file.is_file():
                file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                if file_time < cutoff_time:
                    backup_file.unlink()
                    logging.info(f"Eliminado backup antiguo: {backup_file.name}")