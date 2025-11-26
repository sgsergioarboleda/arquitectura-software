from typing import Optional, List
from bson import ObjectId
from domain.lost_items.models.lost_item import LostItem
from domain.lost_items.ports.lost_item_repository_port import LostItemRepositoryPort


class MongoLostItemRepository:
    """Adaptador MongoDB para el repositorio de objetos perdidos"""
    
    def __init__(self, db):
        """
        Args:
            db: Instancia de MongoDBService
        """
        self.db = db
        self.collection_name = "lost_items"
    
    def find_by_id(self, item_id: str) -> Optional[LostItem]:
        """Busca un objeto perdido por ID"""
        if not ObjectId.is_valid(item_id):
            return None
        
        collection = self.db.get_collection(self.collection_name)
        if collection is None:
            return None
        
        document = collection.find_one({"_id": ObjectId(item_id)})
        if not document:
            return None
        
        return self._document_to_domain(document)
    
    def save(self, item: LostItem) -> LostItem:
        """Guarda un nuevo objeto perdido"""
        collection = self.db.get_collection(self.collection_name)
        if collection is None:
            raise RuntimeError("No se pudo obtener la colección")
        
        document = self._domain_to_document(item)
        # Remover el _id si existe para inserción
        document.pop("_id", None)
        
        result = collection.insert_one(document)
        item.id = str(result.inserted_id)
        return item
    
    def update(self, item: LostItem) -> LostItem:
        """Actualiza un objeto perdido existente"""
        if not item.id or not ObjectId.is_valid(item.id):
            raise ValueError("ID inválido para actualización")
        
        collection = self.db.get_collection(self.collection_name)
        if collection is None:
            raise RuntimeError("No se pudo obtener la colección")
        
        document = self._domain_to_document(item)
        item_id = document.pop("_id")
        
        result = collection.update_one(
            {"_id": ObjectId(item_id)},
            {"$set": document}
        )
        
        if result.matched_count == 0:
            raise ValueError(f"No se encontró el objeto con ID {item.id}")
        
        return item
    
    def find_removed(self, limit: int = 100) -> List[LostItem]:
        """Busca objetos perdidos que han sido removidos"""
        collection = self.db.get_collection(self.collection_name)
        if collection is None:
            return []
        
        documents = collection.find({"status": "removed"}).limit(limit)
        return [self._document_to_domain(doc) for doc in documents]
    
    def _document_to_domain(self, document: dict) -> LostItem:
        """Convierte un documento MongoDB a entidad de dominio"""
        return LostItem(
            id=str(document["_id"]),
            title=document.get("title", ""),
            found_location=document.get("found_location", ""),
            status=document.get("status", "available"),
            updated_at=document.get("updated_at"),
            removal_id=document.get("removal_id")
        )
    
    def _domain_to_document(self, item: LostItem) -> dict:
        """Convierte una entidad de dominio a documento MongoDB"""
        document = {
            "title": item.title,
            "found_location": item.found_location,
            "status": item.status,
            "updated_at": item.updated_at,
            "removal_id": item.removal_id
        }
        
        if item.id:
            document["_id"] = item.id
        
        return document
