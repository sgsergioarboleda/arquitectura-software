from abc import ABC, abstractmethod
from fastapi import FastAPI

class PluginInterface(ABC):
    @abstractmethod
    def register_routes(self, app: FastAPI):
        """Registrar las rutas del plugin en la aplicación principal."""
        pass

    @abstractmethod
    def initialize(self, config: dict):
        """Inicializar el plugin con la configuración proporcionada."""
        pass