from fastapi import APIRouter, HTTPException
from plugins.plugin_interface import PluginInterface
from services.dependencies import mongo_service
from bson import ObjectId

class Plugin(PluginInterface):
    def __init__(self):
        self.router = APIRouter()
        self.collection_name = "lost_items"

    def register_routes(self, app):
        @self.router.delete("/lost/{item_id}")
        async def remove_lost_item(item_id: str):
            try:
                # Validar el formato del ID
                if not ObjectId.is_valid(item_id):
                    raise HTTPException(
                        status_code=400, 
                        detail="ID de objeto inválido"
                    )

                # Obtener la colección
                collection = mongo_service.get_collection(self.collection_name)
                
                # Intentar eliminar el objeto
                result = collection.delete_one({"_id": ObjectId(item_id)})
                
                if result.deleted_count == 0:
                    raise HTTPException(
                        status_code=404,
                        detail="Objeto perdido no encontrado"
                    )
                
                return {
                    "message": "Objeto perdido eliminado exitosamente",
                    "item_id": item_id
                }
                
            except HTTPException as he:
                raise he
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error al eliminar objeto perdido: {str(e)}"
                )

        app.include_router(self.router, prefix="/api")

    def initialize(self, config):
        print("[INFO] Inicializando Remove Lost Item Plugin")
        if not mongo_service.connect():
            print("[ERROR] No se pudo conectar a MongoDB")



import requests

response = requests.delete(
    "http://localhost:8000/api/lost/64f5a3b1234567890abcdef1"
)
print(response.json())

from fastapi import APIRouter, HTTPException
from plugins.plugin_interface import PluginInterface
from services.dependencies import mongo_service
from bson import ObjectId

class Plugin(PluginInterface):
    def __init__(self):
        self.router = APIRouter()
        self.collection_name = "lost_items"

    def register_routes(self, app):
        @self.router.delete("/lost/{item_id}")
        async def remove_lost_item(item_id: str):
            try:
                # Validar el formato del ID
                if not ObjectId.is_valid(item_id):
                    raise HTTPException(
                        status_code=400, 
                        detail="ID de objeto inválido"
                    )

                # Obtener la colección
                collection = mongo_service.get_collection(self.collection_name)
                
                # Intentar eliminar el objeto
                result = collection.delete_one({"_id": ObjectId(item_id)})
                
                if result.deleted_count == 0:
                    raise HTTPException(
                        status_code=404,
                        detail="Objeto perdido no encontrado"
                    )
                
                return {
                    "message": "Objeto perdido eliminado exitosamente",
                    "item_id": item_id
                }
                
            except HTTPException as he:
                raise he
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error al eliminar objeto perdido: {str(e)}"
                )

        app.include_router(self.router, prefix="/api")

    def initialize(self, config):
        print("[INFO] Inicializando Remove Lost Item Plugin")
        if not mongo_service.connect():
            print("[ERROR] No se pudo conectar a MongoDB")

import requests

response = requests.delete(
    "http://localhost:8000/api/lost/64f5a3b1234567890abcdef1"
)
print(response.json())