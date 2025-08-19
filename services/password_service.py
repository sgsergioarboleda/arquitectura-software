from passlib.context import CryptContext
from typing import Optional

class PasswordService:
    """
    Servicio para manejar la encriptación y verificación de contraseñas
    Utiliza bcrypt para el hash seguro de contraseñas
    """
    
    def __init__(self):
        # Configurar el contexto de encriptación con bcrypt
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def hash_password(self, password: str) -> str:
        """
        Encripta una contraseña usando bcrypt
        
        Args:
            password: Contraseña en texto plano
            
        Returns:
            str: Contraseña encriptada (hash)
        """
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verifica si una contraseña en texto plano coincide con su hash
        
        Args:
            plain_password: Contraseña en texto plano
            hashed_password: Contraseña encriptada (hash)
            
        Returns:
            bool: True si la contraseña coincide, False en caso contrario
        """
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def is_password_strong(self, password: str) -> tuple[bool, Optional[str]]:
        """
        Verifica si una contraseña cumple con los requisitos de seguridad
        
        Args:
            password: Contraseña a verificar
            
        Returns:
            tuple[bool, Optional[str]]: (es_fuerte, mensaje_error)
        """
        if len(password) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres"
        
        if not any(c.isupper() for c in password):
            return False, "La contraseña debe contener al menos una letra mayúscula"
        
        if not any(c.islower() for c in password):
            return False, "La contraseña debe contener al menos una letra minúscula"
        
        if not any(c.isdigit() for c in password):
            return False, "La contraseña debe contener al menos un número"
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            return False, "La contraseña debe contener al menos un carácter especial"
        
        return True, None

# Instancia global del servicio de contraseñas
password_service = PasswordService()
