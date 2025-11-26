from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from services.config_service import config_service
from services.password_service import password_service
import os
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

class AuthService:
    """
    Servicio de autenticación que maneja JWT y verificación de usuarios
    """
    
    def __init__(self):
        self.jwt_config = config_service.get_jwt_config()
        self.failed_attempts = {}
        self.lockout_duration = 300  # 5 minutos
        self.max_attempts = 5
        
        # Cargar llaves RSA
        self._load_rsa_keys()
    
    def _load_rsa_keys(self):
        """Cargar llaves RSA desde archivos"""
        try:
            print("🔑 Cargando llaves RSA...")
            base_dir = Path(__file__).parent.parent
            private_key_path = base_dir / "keys" / "private.pem"
            public_key_path = base_dir / "keys" / "public.pem"
            
            # Si las llaves no existen en testing, usar valores por defecto
            if not private_key_path.exists() or not public_key_path.exists():
                print("[WARNING] Llaves RSA no encontradas. Usando valores de prueba.")
                self.private_key = None
                self.public_key = None
                return
            
            print(f"📁 Ruta de llave privada: {private_key_path}")
            with open(private_key_path, "rb") as f:
                self.private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None,
                    backend=default_backend()
                )
            print("✅ Llave privada cargada")
            
            print(f"📁 Ruta de llave pública: {public_key_path}")
            with open(public_key_path, "rb") as f:
                self.public_key = serialization.load_pem_public_key(
                    f.read(),
                    backend=default_backend()
                )
            print("✅ Llave pública cargada")
                
        except Exception as e:
            print(f"❌ Error: No se pudieron cargar las llaves RSA: {e}")
            raise Exception(f"No se pudieron cargar las llaves RSA: {str(e)}")
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """
        Crea un token JWT de acceso usando llave privada RSA
        
        Args:
            data: Datos a incluir en el payload del token
            
        Returns:
            str: Token JWT generado
        """
        to_encode = data.copy()
        
        # Agregar tiempo de expiración usando zona horaria de Bogotá (UTC-5)
        bogota_tz = timezone(timedelta(hours=-5))
        expire = datetime.now(bogota_tz) + timedelta(minutes=self.jwt_config["expiration_minutes"])
        to_encode.update({"exp": expire})
        
        # Generar token usando llave privada RSA
        encoded_jwt = jwt.encode(
            to_encode, 
            self.private_key, 
            algorithm="RS256"
        )
        
        return encoded_jwt
    
    def create_access_token_with_duration(self, data: Dict[str, Any], duration_minutes: int) -> str:
        """
        Crea un token JWT de acceso con duración personalizada usando llave privada RSA
        
        Args:
            data: Datos a incluir en el payload del token
            duration_minutes: Duración del token en minutos
            
        Returns:
            str: Token JWT generado
        """
        to_encode = data.copy()
        
        # Agregar tiempo de expiración con duración personalizada usando zona horaria de Bogotá (UTC-5)
        bogota_tz = timezone(timedelta(hours=-5))
        expire = datetime.now(bogota_tz) + timedelta(minutes=duration_minutes)
        print(f"🕐 Token generado con expiración: {expire} (Zona horaria: Bogotá UTC-5)")
        to_encode.update({"exp": expire})
        
        # Generar token usando llave privada RSA
        encoded_jwt = jwt.encode(
            to_encode, 
            self.private_key, 
            algorithm="RS256"
        )
        
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verifica y decodifica un token JWT usando llave pública RSA
        
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
                self.public_key, 
                algorithms=["RS256"]
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
    
    async def authenticate_user(self, mongo_service, correo: str, contraseña: str) -> Optional[Dict[str, Any]]:
        """
        Autentica un usuario verificando correo y contraseña
        
        Args:
            mongo_service: Servicio de MongoDB
            correo: Correo electrónico del usuario
            contraseña: Contraseña del usuario
            
        Returns:
            Optional[Dict[str, Any]]: Usuario autenticado o None si falla
        """
        # Verificar bloqueo
        if self._is_account_locked(correo):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Cuenta bloqueada temporalmente. Intente más tarde."
            )
            
        try:
            # Buscar usuario por correo
            usuario = mongo_service.find_one("usuarios", {"correo": correo})
            
            if not usuario:
                return None
            
            # Verificar contraseña usando el servicio de encriptación
            if not password_service.verify_password(contraseña, usuario["contraseña"]):
                self._track_failed_attempt(correo)
                return None
            
            # Reiniciar contador de intentos fallidos
            self.failed_attempts[correo] = {"count": 0, "last_attempt": None}
            
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

    def _track_failed_attempt(self, correo: str):
        """
        Rastrea los intentos fallidos de inicio de sesión
        
        Args:
            correo: Correo electrónico del usuario
        """
        bogota_tz = timezone(timedelta(hours=-5))
        current_time = datetime.now(bogota_tz)
        
        if correo in self.failed_attempts:
            self.failed_attempts[correo]["count"] += 1
            self.failed_attempts[correo]["last_attempt"] = current_time
        else:
            self.failed_attempts[correo] = {"count": 1, "last_attempt": current_time}
    
    def _is_account_locked(self, correo: str) -> bool:
        """
        Verifica si la cuenta está bloqueada debido a intentos fallidos
        
        Args:
            correo: Correo electrónico del usuario
            
        Returns:
            bool: True si la cuenta está bloqueada, False en caso contrario
        """
        if correo not in self.failed_attempts:
            return False
        
        attempts = self.failed_attempts[correo]
        if attempts["count"] >= self.max_attempts:
            # Verificar si ha pasado el tiempo de bloqueo usando zona horaria de Bogotá
            bogota_tz = timezone(timedelta(hours=-5))
            current_time = datetime.now(bogota_tz)
            if (current_time - attempts["last_attempt"]).total_seconds() < self.lockout_duration:
                return True
            else:
                # Reiniciar contador después del período de bloqueo
                self.failed_attempts[correo] = {"count": 0, "last_attempt": None}
        
        return False

# Instancia global del servicio de autenticación
auth_service = AuthService()
