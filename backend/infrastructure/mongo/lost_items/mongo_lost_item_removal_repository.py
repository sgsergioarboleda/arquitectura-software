from typing import Optional
from bson import ObjectId
from domain.lost_items.models.lost_item_removal import LostItemRemoval
from domain.lost_items.ports.lost_item_removal_repository_port import LostItemRemovalRepositoryPort


class MongoLostItemRemovalRepository:
    """Adaptador MongoDB para el repositorio de remociones de objetos perdidos"""
    
    def __init__(self, db):
        """
        Args:
            db: Instancia de MongoDBService
        """
        self.db = db
        self.collection_name = "lost_items_removals"
    
    def save_removal(self, removal: LostItemRemoval) -> LostItemRemoval:
        """Guarda un registro de remoción"""
        collection = self.db.get_collection(self.collection_name)
        if collection is None:
            raise RuntimeError("No se pudo obtener la colección")
        
        document = self._domain_to_document(removal)
        # Remover el _id si existe para inserción
        document.pop("_id", None)
        
        result = collection.insert_one(document)
        removal.id = str(result.inserted_id)
        return removal
    
    def find_by_item_id(self, item_id: str) -> Optional[LostItemRemoval]:
        """Busca un registro de remoción por ID del objeto"""
        collection = self.db.get_collection(self.collection_name)
        if collection is None:
            return None
        
        document = collection.find_one({"item_id": item_id})
        if not document:
            return None
        
        return self._document_to_domain(document)
    
    def _document_to_domain(self, document: dict) -> LostItemRemoval:
        """Convierte un documento MongoDB a entidad de dominio"""
        return LostItemRemoval(
            id=str(document["_id"]),
            item_id=document.get("item_id", ""),
            removed_by=document.get("removed_by", ""),
            removed_at=document.get("removed_at", ""),
            notes=document.get("notes", ""),
            previous_status=document.get("previous_status", "")
        )
    
    def _domain_to_document(self, removal: LostItemRemoval) -> dict:
        """Convierte una entidad de dominio a documento MongoDB"""
        document = {
            "item_id": removal.item_id,
            "removed_by": removal.removed_by,
            "removed_at": removal.removed_at,
            "notes": removal.notes,
            "previous_status": removal.previous_status
        }
        
        if removal.id:
            document["_id"] = removal.id
        
        return document
