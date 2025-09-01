from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from Auth.auth_service import auth_service
from Auth.auth_schemas import LoginRequest, LoginResponse, LogoutResponse
from Auth.auth_dependencies import require_auth
from services.mongodb_service import MongoDBService
from services.dependencies import get_mongodb

# Crear router de autenticación
auth_router = APIRouter(prefix="/auth", tags=["Autenticación"])

@auth_router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    mongo_service: MongoDBService = Depends(get_mongodb)
):
    """
    Endpoint para autenticar usuario y generar token JWT con 15 minutos de duración
    
    Args:
        login_data: Datos de login (correo y contraseña)
        mongo_service: Servicio de MongoDB
        
    Returns:
        LoginResponse: Token JWT con 15 minutos de duración
        
    Raises:
        HTTPException: Si las credenciales son inválidas
    """
    try:
        # Autenticar usuario
        usuario = await auth_service.authenticate_user(
            mongo_service, 
            login_data.correo, 
            login_data.contraseña
        )
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas"
            )
        
        # Crear token JWT con el ID del usuario y 15 minutos de duración
        token_data = {
            "user_id": str(usuario["_id"]),
            "correo": usuario["correo"],
            "tipo": usuario["tipo"]
        }
        
        # Generar token con 15 minutos de duración
        access_token = auth_service.create_access_token_with_duration(token_data, 15)
        
        return LoginResponse(token=access_token)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@auth_router.post("/logout", response_model=LogoutResponse)
async def logout():
    """
    Endpoint para logout (el token se invalida en el cliente)
    
    Returns:
        LogoutResponse: Mensaje de confirmación
    """
    return LogoutResponse(
        message="Logout exitoso. El token ha sido invalidado en el cliente."
    )

@auth_router.get("/verify")
async def verify_token(
    current_user: dict = require_auth()
):
    """
    Endpoint para verificar la validez de un token
    
    Args:
        current_user: Usuario autenticado (obtenido del token)
        
    Returns:
        dict: Información del token verificado
    """
    return {
        "valid": True,
        "user_id": str(current_user["_id"]),
        "correo": current_user["correo"],
        "nombre": current_user["nombre"],
        "tipo": current_user["tipo"],
        "message": "Token válido"
    }
