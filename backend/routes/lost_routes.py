from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
import os
import shutil
from pathlib import Path

from services.dependencies import get_mongodb, MongoDBService
from schemas.lost_item_schemas import (
    LostItemCreate,
    LostItemUpdate,
    LostItemResponse,
    LostItemsListResponse,
    ClaimRequest,
    ClaimResponse
)

router = APIRouter(prefix="/lost", tags=["lost"])

# Configurar directorio para imágenes
UPLOAD_DIR = Path("uploads/lost_items")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.get("/", response_model=List[LostItemResponse])
async def list_lost_items(
    q: Optional[str] = Query(None, description="Término de búsqueda"),
    db: MongoDBService = Depends(get_mongodb)
):
    """
    Obtener lista de objetos perdidos con búsqueda opcional
    """
    try:
        if not db.is_connected():
            raise HTTPException(
                status_code=500,
                detail="No hay conexión a MongoDB"
            )
        
        # Construir filtro de búsqueda
        filter_query = {}
        if q:
            # Búsqueda por título o ubicación
            filter_query = {
                "$or": [
                    {"title": {"$regex": q, "$options": "i"}},
                    {"found_location": {"$regex": q, "$options": "i"}}
                ]
            }
        
        # Obtener objetos perdidos
        items = db.find_all("lost_items", filter_query=filter_query, limit=100)
        
        # Convertir a formato de respuesta
        items_response = []
        for item in items:
            items_response.append(
                LostItemResponse(
                    _id=str(item["_id"]),
                    title=item["title"],
                    found_location=item["found_location"],
                    status=item.get("status", "available"),
                    description=item.get("description"),
                    contact_info=item.get("contact_info"),
                    created_at=item.get("created_at", ""),
                    updated_at=item.get("updated_at")
                )
            )
        
        return items_response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.post("/", response_model=LostItemResponse, status_code=201)
async def create_lost_item(
    item: LostItemCreate,
    db: MongoDBService = Depends(get_mongodb)
):
    """
    Crear un nuevo objeto perdido
    """
    try:
        if not db.is_connected():
            raise HTTPException(
                status_code=500,
                detail="No hay conexión a MongoDB"
            )
        
        # Preparar documento para insertar
        item_doc = {
            "title": item.title,
            "found_location": item.found_location,
            "status": "available",
            "description": item.description,
            "contact_info": item.contact_info,
            "created_at": datetime.now().isoformat(),
            "updated_at": None
        }
        
        # Insertar en MongoDB
        collection = db.get_collection("lost_items")
        result = collection.insert_one(item_doc)
        
        # Obtener el objeto creado
        created_item = db.find_by_id("lost_items", str(result.inserted_id))
        
        if not created_item:
            raise HTTPException(
                status_code=500,
                detail="Objeto creado pero no se pudo recuperar"
            )
        
        return LostItemResponse(
            _id=str(created_item["_id"]),
            title=created_item["title"],
            found_location=created_item["found_location"],
            status=created_item.get("status", "available"),
            description=created_item.get("description"),
            contact_info=created_item.get("contact_info"),
            created_at=created_item.get("created_at", ""),
            updated_at=created_item.get("updated_at")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.get("/{item_id}", response_model=LostItemResponse)
async def get_lost_item(
    item_id: str,
    db: MongoDBService = Depends(get_mongodb)
):
    """
    Obtener un objeto perdido específico por ID
    """
    try:
        if not db.is_valid_object_id(item_id):
            raise HTTPException(
                status_code=400,
                detail="ID de objeto inválido"
            )
        
        item = db.find_by_id("lost_items", item_id)
        if not item:
            raise HTTPException(
                status_code=404,
                detail="Objeto no encontrado"
            )
        
        return LostItemResponse(
            _id=str(item["_id"]),
            title=item["title"],
            found_location=item["found_location"],
            status=item.get("status", "available"),
            description=item.get("description"),
            contact_info=item.get("contact_info"),
            created_at=item.get("created_at", ""),
            updated_at=item.get("updated_at")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.get("/{item_id}/image")
async def get_lost_item_image(
    item_id: str,
    db: MongoDBService = Depends(get_mongodb)
):
    """
    Obtener imagen de un objeto perdido
    """
    try:
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
        
        # Buscar imagen en el directorio de uploads
        image_path = UPLOAD_DIR / f"{item_id}.jpg"
        if not image_path.exists():
            # Si no existe imagen, devolver una imagen por defecto
            default_image = Path("assets/default_lost_item.jpg")
            if default_image.exists():
                return FileResponse(default_image)
            else:
                raise HTTPException(
                    status_code=404,
                    detail="Imagen no encontrada"
                )
        
        return FileResponse(image_path)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.post("/{item_id}/claim", response_model=ClaimResponse)
async def claim_lost_item(
    item_id: str,
    notes: str = Form(...),
    evidences: List[UploadFile] = File(...),
    db: MongoDBService = Depends(get_mongodb)
):
    """
    Reclamar un objeto perdido
    """
    try:
        if not db.is_valid_object_id(item_id):
            raise HTTPException(
                status_code=400,
                detail="ID de objeto inválido"
            )
        
        # Verificar que el objeto existe y está disponible
        item = db.find_by_id("lost_items", item_id)
        if not item:
            raise HTTPException(
                status_code=404,
                detail="Objeto no encontrado"
            )
        
        if item.get("status") != "available":
            raise HTTPException(
                status_code=400,
                detail="Este objeto ya no está disponible para reclamar"
            )
        
        # Validar archivos de evidencia
        if not evidences:
            raise HTTPException(
                status_code=400,
                detail="Debe proporcionar al menos una evidencia"
            )
        
        # Crear directorio para evidencias si no existe
        evidence_dir = UPLOAD_DIR / "claims" / item_id
        evidence_dir.mkdir(parents=True, exist_ok=True)
        
        # Guardar archivos de evidencia
        evidence_files = []
        for i, evidence in enumerate(evidences):
            if evidence.content_type not in ["image/jpeg", "image/png", "image/gif", "application/pdf"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Tipo de archivo no permitido: {evidence.content_type}"
                )
            
            # Generar nombre único para el archivo
            file_extension = evidence.filename.split(".")[-1] if "." in evidence.filename else "bin"
            evidence_filename = f"evidence_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_extension}"
            evidence_path = evidence_dir / evidence_filename
            
            # Guardar archivo
            with open(evidence_path, "wb") as buffer:
                shutil.copyfileobj(evidence.file, buffer)
            
            evidence_files.append(evidence_filename)
        
        # Crear documento de reclamo
        claim_doc = {
            "item_id": item_id,
            "notes": notes,
            "evidence_files": evidence_files,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "updated_at": None
        }
        
        # Insertar reclamo en MongoDB
        collection = db.get_collection("claims")
        claim_result = collection.insert_one(claim_doc)
        
        # Actualizar estado del objeto perdido
        item_collection = db.get_collection("lost_items")
        item_collection.update_one(
            {"_id": ObjectId(item_id)},
            {
                "$set": {
                    "status": "claimed",
                    "updated_at": datetime.now().isoformat()
                }
            }
        )
        
        return ClaimResponse(
            message="Reclamo enviado exitosamente",
            claim_id=str(claim_result.inserted_id),
            status="pending"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.put("/{item_id}", response_model=LostItemResponse)
async def update_lost_item(
    item_id: str,
    item_update: LostItemUpdate,
    db: MongoDBService = Depends(get_mongodb)
):
    """
    Actualizar un objeto perdido existente
    """
    try:
        if not db.is_valid_object_id(item_id):
            raise HTTPException(
                status_code=400,
                detail="ID de objeto inválido"
            )
        
        # Verificar que el objeto existe
        existing_item = db.find_by_id("lost_items", item_id)
        if not existing_item:
            raise HTTPException(
                status_code=404,
                detail="Objeto no encontrado"
            )
        
        # Preparar campos a actualizar
        update_fields = {}
        if item_update.title is not None:
            update_fields["title"] = item_update.title
        if item_update.found_location is not None:
            update_fields["found_location"] = item_update.found_location
        if item_update.status is not None:
            update_fields["status"] = item_update.status
        if item_update.description is not None:
            update_fields["description"] = item_update.description
        if item_update.contact_info is not None:
            update_fields["contact_info"] = item_update.contact_info
        
        # Agregar fecha de actualización
        update_fields["updated_at"] = datetime.now().isoformat()
        
        # Actualizar en MongoDB
        collection = db.get_collection("lost_items")
        result = collection.update_one(
            {"_id": ObjectId(item_id)},
            {"$set": update_fields}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=400,
                detail="No se pudo actualizar el objeto"
            )
        
        # Obtener objeto actualizado
        updated_item = db.find_by_id("lost_items", item_id)
        
        return LostItemResponse(
            _id=str(updated_item["_id"]),
            title=updated_item["title"],
            found_location=updated_item["found_location"],
            status=updated_item.get("status", "available"),
            description=updated_item.get("description"),
            contact_info=updated_item.get("contact_info"),
            created_at=updated_item.get("created_at", ""),
            updated_at=updated_item.get("updated_at")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.delete("/{item_id}")
async def delete_lost_item(
    item_id: str,
    db: MongoDBService = Depends(get_mongodb)
):
    """
    Eliminar un objeto perdido
    """
    try:
        if not db.is_valid_object_id(item_id):
            raise HTTPException(
                status_code=400,
                detail="ID de objeto inválido"
            )
        
        # Verificar que el objeto existe
        existing_item = db.find_by_id("lost_items", item_id)
        if not existing_item:
            raise HTTPException(
                status_code=404,
                detail="Objeto no encontrado"
            )
        
        # Eliminar objeto
        collection = db.get_collection("lost_items")
        result = collection.delete_one({"_id": ObjectId(item_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=400,
                detail="No se pudo eliminar el objeto"
            )
        
        # Eliminar archivos asociados
        image_path = UPLOAD_DIR / f"{item_id}.jpg"
        if image_path.exists():
            image_path.unlink()
        
        evidence_dir = UPLOAD_DIR / "claims" / item_id
        if evidence_dir.exists():
            shutil.rmtree(evidence_dir)
        
        return {
            "message": "Objeto eliminado exitosamente",
            "item_id": item_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )
