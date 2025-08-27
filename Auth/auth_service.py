from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from jose import JWTError, jwt
from fastapi import HTTPException, status
from services.config_service import config_service
from services.mongodb_service import MongoDBService
from services.password_service import password_service

class AuthService:
    """
    Servicio de autenticación que maneja JWT y verificación de usuarios
    """
    
    def __init__(self):
        self.jwt_config = config_service.get_jwt_config()
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """
        Crea un token JWT de acceso
        
        Args:
            data: Datos a incluir en el payload del token
            
        Returns:
            str: Token JWT generado
        """
        to_encode = data.copy()
        
        # Agregar tiempo de expiración
        expire = datetime.utcnow() + timedelta(minutes=self.jwt_config["expiration_minutes"])
        to_encode.update({"exp": expire})
        
        # Generar token
        encoded_jwt = jwt.encode(
            to_encode, 
            self.jwt_config["secret"], 
            algorithm=self.jwt_config["algorithm"]
        )
        
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verifica y decodifica un token JWT
        
        Args:
            token: Token JWT a verificar
            
        Returns:
            Dict[str, Any]: Payload del token decodificado
            
        Raises:
            HTTPException: Si el token es inválido o ha expirado
        """
        try:
            payload = jwt.decode(
                token, 
                self.jwt_config["secret"], 
                algorithms=[self.jwt_config["algorithm"]]
            )
            
            # Verificar que el token no haya expirado
            if payload.get("exp") is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token sin tiempo de expiración"
                )
            
            return payload
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
    
    def authenticate_user(self, mongo_service: MongoDBService, correo: str, contraseña: str) -> Optional[Dict[str, Any]]:
        """
        Autentica un usuario verificando correo y contraseña
        
        Args:
            mongo_service: Servicio de MongoDB
            correo: Correo electrónico del usuario
            contraseña: Contraseña del usuario
            
        Returns:
            Optional[Dict[str, Any]]: Usuario autenticado o None si falla
        """
        try:
            # Buscar usuario por correo
            usuario = mongo_service.find_one("usuarios", {"correo": correo})
            
            if not usuario:
                return None
            
            # Verificar contraseña usando el servicio de encriptación
            if not password_service.verify_password(contraseña, usuario["contraseña"]):
                return None
            
            return usuario
            
        except Exception as e:
            print(f"Error en autenticación: {str(e)}")
            return None
    
    def get_current_user_id(self, token: str) -> str:
        """
        Obtiene el ID del usuario actual desde el token
        
        Args:
            token: Token JWT
            
        Returns:
            str: ID del usuario
            
        Raises:
            HTTPException: Si el token es inválido o no contiene el ID
        """
        payload = self.verify_token(token)
        user_id = payload.get("user_id")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token no contiene ID de usuario"
            )
        
        return user_id

    def validate_role(self, user: dict, required_roles: List[str]) -> bool:
        """
        Valida si un usuario tiene los roles requeridos
        
        Args:
            user: Usuario a validar
            required_roles: Lista de roles requeridos
            
        Returns:
            bool: True si el usuario tiene al menos uno de los roles requeridos
        """
        if not user or "tipo" not in user:
            return False
        return user["tipo"] in required_roles

    async def validate_token_and_permissions(
        self, 
        token: str, 
        required_roles: List[str]
    ) -> dict:
        """
        Valida token y permisos en una sola operación
        
        Args:
            token: Token JWT
            required_roles: Lista de roles requeridos
            
        Returns:
            dict: Payload del token si es válido y tiene permisos
            
        Raises:
            HTTPException: Si el token es inválido o no tiene permisos
        """
        payload = self.verify_token(token)
        if not self.validate_role(payload, required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes los permisos necesarios"
            )
        return payload

# Instancia global del servicio de autenticación
auth_service = AuthService()
