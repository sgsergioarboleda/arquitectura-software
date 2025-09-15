from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from enum import Enum
from typing import List, Dict, Tuple
from Auth.auth_service import auth_service
from services.dependencies import get_mongodb
from datetime import datetime, timedelta

# Esquema de autenticación HTTP Bearer
security = HTTPBearer()

class UserRole(Enum):
    ADMIN = "admin"
    USER = "usuario"

# Primero definimos get_current_user
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
        print(f"🔐 Verificando token: {credentials.credentials[:20]}...")
        
        # Verificar token
        payload = auth_service.verify_token(credentials.credentials)
        print(f"📋 Payload del token: {payload}")
        
        user_id = payload.get("user_id")
        
        if not user_id:
            print("❌ Token no contiene user_id")
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

# Luego definimos check_permissions
def check_permissions(required_roles: List[UserRole]):
    async def permission_checker(current_user: dict = Depends(get_current_user)):
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No autenticado"
            )
        
        # Verificar que el rol existe y es válido
        if "tipo" not in current_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario sin rol definido"
            )
            
        # Validación más estricta de roles
        user_role = current_user["tipo"].lower()
        allowed_roles = [role.value.lower() for role in required_roles]
        
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Rol requerido: {allowed_roles}"
            )
            
        # Registrar intento de acceso
        print(f"👤 Acceso autorizado: {current_user['correo']} ({user_role})")
        return current_user
    return permission_checker

# Funciones de autorización específicas
require_admin = check_permissions([UserRole.ADMIN])
require_user = check_permissions([UserRole.USER, UserRole.ADMIN])

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


 