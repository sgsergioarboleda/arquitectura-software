from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Auth.auth_service import auth_service
from services.dependencies import get_mongodb

# Esquema de autenticación HTTP Bearer
security = HTTPBearer()

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
        
        # Buscar usuario en la base de datos
        usuario = mongo_service.find_by_id("usuarios", user_id)
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado"
            )
        
        return usuario
        
    except HTTPException:
        raise
    except Exception as e:
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
