from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from enum import Enum
from typing import List, Dict, Tuple
from auth.auth_service import auth_service
from services.dependencies import get_mongodb
from datetime import datetime, timedelta

# Esquema de autenticación HTTP Bearer
security = HTTPBearer()

class UserRole(Enum):
    ADMIN = "admin"
    USER = "usuario"

def check_permissions(required_roles: List[UserRole]):
    async def permission_checker(current_user: dict = Depends(get_current_user)):
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No autenticado"
            )
        
        if current_user["tipo"] not in [role.value for role in required_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Roles requeridos: {[role.value for role in required_roles]}"
            )
        return current_user
    return permission_checker

# Funciones de autorización específicas
require_admin = check_permissions([UserRole.ADMIN])
require_user = check_permissions([UserRole.USER, UserRole.ADMIN])

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    mongo_service = Depends(get_mongodb)
) -> dict:
    """
    Dependencia para obtener el usuario actual autenticado
    
    Args:
        credentials: Credenciales de autenticación del header
        mongo_service: Servicio de MongoDB
        
    Returns:
        dict: Usuario autenticado
        
    Raises:
        HTTPException: Si el token es inválido o el usuario no existe
    """
    try:
        # Verificar token
        payload = auth_service.verify_token(credentials.credentials)
        user_id = payload.get("user_id")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token no contiene ID de usuario"
            )
        
        print(f"🔍 Buscando usuario con ID: {user_id}")
        
        # Buscar usuario en la base de datos usando el método mejorado
        usuario = mongo_service.find_by_id_with_validation("usuarios", user_id)
        
        if not usuario:
            print(f"❌ Usuario no encontrado con ID: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado en la base de datos"
            )
        
        print(f"✅ Usuario encontrado: {usuario.get('nombre', 'N/A')} ({usuario.get('correo', 'N/A')})")
        return usuario
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error en get_current_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Error de autenticación: {str(e)}"
        )

async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Dependencia para obtener solo el ID del usuario actual
    
    Args:
        credentials: Credenciales de autenticación del header
        
    Returns:
        str: ID del usuario autenticado
    """
    payload = auth_service.verify_token(credentials.credentials)
    user_id = payload.get("user_id")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no contiene ID de usuario"
        )
    
    return user_id

def require_auth():
    """
    Decorador para requerir autenticación en endpoints
    """
    return Depends(get_current_user)

class RateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[datetime]] = {}

    async def is_rate_limited(self, ip: str) -> Tuple[bool, int]:
        now = datetime.now()
        if ip not in self.requests:
            self.requests[ip] = []

        # Limpiar solicitudes antiguas
        self.requests[ip] = [
            req_time for req_time in self.requests[ip]
            if now - req_time < timedelta(seconds=self.window_seconds)
        ]

        # Verificar límite
        if len(self.requests[ip]) >= self.max_requests:
            return True, len(self.requests[ip])

        self.requests[ip].append(now)
        return False, len(self.requests[ip])

rate_limiter = RateLimiter()

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    is_limited, current_requests = await rate_limiter.is_rate_limited(client_ip)
    
    if is_limited:
        return JSONResponse(
            status_code=429,
            content={
                "error": "Too many requests",
                "detail": f"Rate limit exceeded. Try again later."
            }
        )
    
    response = await call_next(request)
    return response
