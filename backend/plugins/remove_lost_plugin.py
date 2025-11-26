from fastapi import APIRouter, HTTPException, Depends
from plugins.plugin_interface import PluginInterface
from services.dependencies import get_mongodb
from Auth.auth_dependencies import require_admin
from bson import ObjectId

# Importar capas hexagonales
from domain.lost_items.services.lost_item_service import LostItemService
from infrastructure.mongo.lost_items.mongo_lost_item_repository import MongoLostItemRepository
from infrastructure.mongo.lost_items.mongo_lost_item_removal_repository import MongoLostItemRemovalRepository


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
            Usando arquitectura hexagonal (puertos y adaptadores)
            """
            try:
                # Validar ID
                if not db.is_valid_object_id(item_id):
                    raise HTTPException(
                        status_code=400,
                        detail="ID de objeto inválido"
                    )

                # Crear instancias de los repositorios (adaptadores)
                lost_repo = MongoLostItemRepository(db)
                removal_repo = MongoLostItemRemovalRepository(db)

                # Crear instancia del servicio de dominio
                service = LostItemService(
                    lost_repo=lost_repo,
                    removal_repo=removal_repo
                )

                # Ejecutar la lógica de negocio a través del servicio
                result = service.remove_item(
                    item_id=item_id,
                    removed_by=str(current_user["_id"]),
                    notes=notes
                )

                return result

            except ValueError as ve:
                # Errores de validación de dominio
                raise HTTPException(
                    status_code=400,
                    detail=str(ve)
                )
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
            Mantiene la lógica actual sin cambios
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
        print("🗑️ Inicializando Remove Lost Plugin (Hexagonal Architecture)")
        print("📝 Configuración:", config)
