import os
from typing import Optional

class SecretManager:
    """
    Servicio para gestionar secretos desde variables de entorno
    Los secretos deben tener el formato SECRET_[NOMBRE_SECRETO] en el archivo .env
    """
    
    def __init__(self):
        self._secrets_cache = {}
    
    def obtener_secret(self, secret_name: str) -> Optional[str]:
        """
        Obtiene un secreto del archivo .env
        
        Args:
            secret_name: Nombre del secreto (sin el prefijo SECRET_)
            
        Returns:
            str: Valor del secreto o None si no existe
        """
        # Construir la clave del secreto con el prefijo SECRET_
        env_key = f"SECRET_{secret_name.upper()}"
        
        # Verificar si ya está en caché
        if env_key in self._secrets_cache:
            return self._secrets_cache[env_key]
        
        # Obtener el secreto del archivo .env
        secret_value = os.getenv(env_key)
        
        # Guardar en caché
        self._secrets_cache[env_key] = secret_value
        
        return secret_value

# Instancia global del secret manager
secret_manager = SecretManager()
