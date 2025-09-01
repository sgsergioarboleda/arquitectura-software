import os
from typing import List
from dotenv import load_dotenv
import logging

class ConfigService:
    """
    Servicio de configuración simplificado para manejar variables de entorno
    Carga configuración desde archivos .env y variables de entorno del sistema
    """
    
    def __init__(self, env_file: str = ".env"):
        """
        Inicializa el servicio de configuración
        
        Args:
            env_file: Ruta al archivo .env (opcional)
        """
        self.logger = logging.getLogger(__name__)
        
        # Cargar archivo .env si existe
        if os.path.exists(env_file):
            load_dotenv(env_file)
            self.logger.info(f"Archivo de configuración cargado: {env_file}")
        else:
            self.logger.warning(f"Archivo de configuración no encontrado: {env_file}")
        
        # Cargar configuración
        self._load_configuration()
    
    def _load_configuration(self):
        """Carga todas las configuraciones desde variables de entorno"""
        
        # MongoDB Configuration
        self.mongodb_uri = os.getenv("MONGODB_URI")
        self.mongodb_database = os.getenv("DATABASE_NAME")
        
        # JWT Configuration
        self.jwt_secret = os.getenv("SECRET_PHRASE")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.jwt_expiration = int(os.getenv("JWT_EXPIRATION_MINUTES", "30"))
        
        # Application Configuration
        self.app_host = os.getenv("APP_HOST", "0.0.0.0")
        self.app_port = int(os.getenv("APP_PORT", "8000"))
        self.app_debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # AWS Configuration
        self.aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.aws_region = os.getenv("AWS_REGION", "us-east-1")
        self.aws_bucket = os.getenv("AWS_S3_BUCKET")
        self.lambda_api_url = os.getenv("LAMBDA_API_URL")
        
        self.logger.info("Configuración cargada exitosamente")
    
    def _parse_list_env(self, env_var: str, default: List[str]) -> List[str]:
        """
        Parsea una variable de entorno que contiene una lista
        
        Args:
            env_var: Nombre de la variable de entorno
            default: Valor por defecto si no se encuentra
            
        Returns:
            List[str]: Lista parseada
        """
        value = os.getenv(env_var)
        if value:
            try:
                # Intentar parsear como JSON si es posible
                import json
                return json.loads(value)
            except (json.JSONDecodeError, ValueError):
                # Si falla, dividir por comas
                return [item.strip() for item in value.split(",")]
        return default
    
    def get_mongodb_config(self) -> dict:
        """
        Obtiene la configuración de MongoDB
        """
        return {
            "uri": self.mongodb_uri,
            "database": self.mongodb_database
        }
    
    def get_jwt_config(self) -> dict:
        """
        Obtiene la configuración de JWT
        """
        return {
            "expiration_minutes": self.jwt_expiration
        }
    
    def get_app_config(self) -> dict:
        """
        Obtiene la configuración de la aplicación
        
        Returns:
            dict: Configuración de la aplicación
        """
        return {
            "host": self.app_host,
            "port": self.app_port,
            "debug": self.app_debug
        }
    
    def is_production(self) -> bool:
        """
        Verifica si la aplicación está en modo producción
        
        Returns:
            bool: True si está en producción
        """
        return not self.app_debug
    
    def is_development(self) -> bool:
        """
        Verifica si la aplicación está en modo desarrollo
        
        Returns:
            bool: True si está en desarrollo
        """
        return self.app_debug
    
    def reload_configuration(self):
        """Recarga la configuración desde las variables de entorno"""
        self.logger.info("Recargando configuración...")
        self._load_configuration()
    
    def get_all_config(self) -> dict:
        """
        Obtiene toda la configuración
        """
        return {
            "mongodb": self.get_mongodb_config(),
            "jwt": self.get_jwt_config(),
            "app": self.get_app_config()
        }
    
    def validate_configuration(self) -> bool:
        """
        Valida que la configuración sea correcta
        
        Returns:
            bool: True si la configuración es válida
        """
        try:
            # Validar MongoDB URI
            if not self.mongodb_uri:
                self.logger.error("MONGODB_URI no está configurado")
                return False
            
            # Validar puerto de la aplicación
            if not (1 <= self.app_port <= 65535):
                self.logger.error(f"Puerto de aplicación inválido: {self.app_port}")
                return False
            
            self.logger.info("Configuración validada exitosamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error validando configuración: {str(e)}")
            return False

# Instancia global del servicio de configuración
config_service = ConfigService()