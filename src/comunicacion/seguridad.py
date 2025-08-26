from typing import Dict, Any, Optional, Callable
import jwt
from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from loguru import logger

class MiddlewareSeguridad:
    """Middleware para seguridad en comunicaciones entre módulos"""
    
    def __init__(self, config_seguridad: Dict[str, Any]):
        self.config = config_seguridad
        self.secret_key = config_seguridad.get('jwt_secret_key', 'clave_por_defecto_cambiar_en_produccion')
        self.algoritmo = config_seguridad.get('jwt_algorithm', 'HS256')
        self.esquema_bearer = HTTPBearer(auto_error=False)
    
    async def validar_token(self, credenciales: HTTPAuthorizationCredentials) -> Dict[str, Any]:
        """Valida un token JWT y devuelve el payload"""
        if not credenciales:
            raise HTTPException(status_code=401, detail="Token de acceso requerido")
        
        try:
            payload = jwt.decode(
                credenciales.credentials,
                self.secret_key,
                algorithms=[self.algoritmo]
            )
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expirado")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Token inválido")
    
    def generar_token(self, modulo: str, permisos: List[str]) -> str:
        """Genera un token JWT para un módulo específico"""
        payload = {
            'sub': modulo,
            'permisos': permisos,
            'exp': datetime.now() + timedelta(hours=24)
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algoritmo)
    
    async def middleware_autenticacion(self, request: Request) -> Optional[Dict[str, Any]]:
        """Middleware de autenticación para endpoints"""
        credenciales = await self.esquema_bearer(request)
        if not credenciales:
            raise HTTPException(status_code=401, detail="Autenticación requerida")
        
        return await self.validar_token(credenciales)
    
    def crear_dependencia_permisos(self, permisos_requeridos: List[str]) -> Callable:
        """Crea una dependencia FastAPI para validar permisos"""
        async def validador_permisos(payload: Dict = Depends(self.middleware_autenticacion)):
            permisos_usuario = payload.get('permisos', [])
            if not any(permiso in permisos_usuario for permiso in permisos_requeridos):
                raise HTTPException(status_code=403, detail="Permisos insuficientes")
            return payload
        
        return validador_permisos