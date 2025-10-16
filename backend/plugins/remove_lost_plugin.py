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
from fastapi import APIRouter, HTTPException, Depends
from plugins.plugin_interface import PluginInterface
from services.dependencies import get_mongodb
from Auth.auth_dependencies import require_admin
from bson import ObjectId
from datetime import datetime

class Plugin(PluginInterface):
    def __init__(self):
        self.router = APIRouter()

    def register_routes(self, app):
        @self.router.post("/lost/{item_id}/remove")
        async def remove_lost_item(
            item_id: str,
            notes: str,
            db = Depends(get_mongodb),
            current_user: dict = Depends(require_admin)
        ):
            """
            Marca un objeto perdido como removido del sistema
            """
            try:
                # Validar ID
                if not db.is_valid_object_id(item_id):
                    raise HTTPException(
                        status_code=400,
                        detail="ID de objeto inválido"
                    )

                # Verificar que el objeto existe
                item = db.find_by_id("lost_items", item_id)
                if not item:
                    raise HTTPException(
                        status_code=404,
                        detail="Objeto no encontrado"
                    )

                # Verificar que el objeto no haya sido removido ya
                if item.get("status") == "removed":
                    raise HTTPException(
                        status_code=400,
                        detail="Este objeto ya fue removido del sistema"
                    )

                # Crear registro de remoción
                removal_doc = {
                    "item_id": ObjectId(item_id),
                    "removed_by": str(current_user["_id"]),
                    "removed_at": datetime.now().isoformat(),
                    "notes": notes,
                    "previous_status": item.get("status", "available")
                }

                # Insertar registro de remoción
                removals_collection = db.get_collection("lost_item_removals")
                removal_result = removals_collection.insert_one(removal_doc)

                # Actualizar estado del objeto perdido
                items_collection = db.get_collection("lost_items")
                update_result = items_collection.update_one(
                    {"_id": ObjectId(item_id)},
                    {
                        "$set": {
                            "status": "removed",
                            "updated_at": datetime.now().isoformat(),
                            "removal_id": str(removal_result.inserted_id)
                        }
                    }
                )

                if update_result.modified_count == 0:
                    raise HTTPException(
                        status_code=500,
                        detail="No se pudo actualizar el estado del objeto"
                    )

                return {
                    "message": "Objeto removido exitosamente",
                    "item_id": item_id,
                    "removal_id": str(removal_result.inserted_id),
                    "removed_at": removal_doc["removed_at"]
                }

            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error interno del servidor: {str(e)}"
                )

        @self.router.get("/lost/removed")
        async def list_removed_items(
            db = Depends(get_mongodb),
            current_user: dict = Depends(require_admin)
        ):
            """
            Lista todos los objetos que han sido removidos
            """
            try:
                # Buscar objetos con estado "removed"
                items = db.find_all(
                    "lost_items",
                    filter_query={"status": "removed"},
                    limit=100
                )

                removed_items = []
                for item in items:
                    # Buscar información de remoción
                    removal_info = db.find_one(
                        "lost_item_removals",
                        {"item_id": item["_id"]}
                    )

                    # Buscar información del usuario que removió
                    removed_by_user = None
                    if removal_info and "removed_by" in removal_info:
                        removed_by_user = db.find_by_id(
                            "usuarios",
                            removal_info["removed_by"]
                        )

                    removed_items.append({
                        "id": str(item["_id"]),
                        "title": item["title"],
                        "found_location": item["found_location"],
                        "removed_at": removal_info["removed_at"] if removal_info else None,
                        "removed_by": {
                            "id": str(removed_by_user["_id"]) if removed_by_user else None,
                            "name": removed_by_user["nombre"] if removed_by_user else "Usuario no encontrado"
                        } if removal_info else None,
                        "removal_notes": removal_info["notes"] if removal_info else None,
                        "previous_status": removal_info["previous_status"] if removal_info else None
                    })

                return {
                    "total": len(removed_items),
                    "items": removed_items
                }

            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error interno del servidor: {str(e)}"
                )

        # Registrar las rutas con el prefijo /api
        app.include_router(self.router, prefix="/api")

    def initialize(self, config):
        """
        Inicializa el plugin con la configuración proporcionada
        """
        print("🗑️ Inicializando Remove Lost Plugin")
        print("📝 Configuración:", config)