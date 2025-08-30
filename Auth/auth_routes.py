from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from auth.auth_service import auth_service
from auth.auth_schemas import LoginRequest, LoginResponse, LogoutResponse
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
    Endpoint para autenticar usuario y generar token JWT
    
    Args:
        login_data: Datos de login (correo y contraseña)
        mongo_service: Servicio de MongoDB
        
    Returns:
        LoginResponse: Token JWT y datos del usuario
        
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
        
        # Crear token JWT con el ID del usuario
        token_data = {
            "user_id": str(usuario["_id"]),
            "correo": usuario["correo"],
            "tipo": usuario["tipo"]
        }
        
        access_token = auth_service.create_access_token(token_data)
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=str(usuario["_id"]),
            correo=usuario["correo"],
            nombre=usuario["nombre"],
            tipo=usuario["tipo"]
        )
        
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
    current_user: dict = Depends(auth_service.get_current_user_id)
):
    """
    Endpoint para verificar la validez de un token
    
    Args:
        current_user: ID del usuario autenticado (obtenido del token)
        
    Returns:
        dict: Información del token verificado
    """
    return {
        "valid": True,
        "user_id": current_user,
        "message": "Token válido"
    }
