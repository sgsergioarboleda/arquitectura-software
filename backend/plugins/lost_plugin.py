from fastapi import APIRouter
from plugins.plugin_interface import PluginInterface

class Plugin(PluginInterface):
    def __init__(self):
        self.router = APIRouter()

    def register_routes(self, app):
        @self.router.get("/lost")
        async def get_lost_items():
            return {"message": "Lista de objetos perdidos"}

        @self.router.post("/lost")
        async def create_lost_item(item: dict):
            return {"message": "Objeto perdido creado", "item": item}

        app.include_router(self.router, prefix="/api")

    def initialize(self, config):
        print("Inicializando Lost Plugin con configuración:", config)