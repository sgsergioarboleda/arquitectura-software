from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

from services.dependencies import get_mongodb, MongoDBService
from schemas.event_schemas import (
    EventCreate, 
    EventUpdate, 
    EventResponse, 
    EventsListResponse
)

router = APIRouter(prefix="/events", tags=["events"])

@router.get("/", response_model=EventsListResponse)
async def get_events(
    db: MongoDBService = Depends(get_mongodb)
):
    """
    Obtener todos los eventos del calendario
    """
    try:
        if not db.is_connected():
            raise HTTPException(
                status_code=500,
                detail="No hay conexión a MongoDB"
            )
        
        # Obtener eventos ordenados por fecha de inicio
        events = db.find_all("events", limit=100)
        
        # Convertir a formato de respuesta
        events_response = []
        for event in events:
            events_response.append(
                EventResponse(
                    _id=str(event["_id"]),
                    title=event["title"],
                    start=event["start"],
                    end=event.get("end"),
                    location=event.get("location"),
                    description=event.get("description"),
                    created_at=event.get("created_at", ""),
                    updated_at=event.get("updated_at")
                )
            )
        
        return EventsListResponse(events=events_response)
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.post("/", response_model=EventResponse, status_code=201)
async def create_event(
    event: EventCreate,
    db: MongoDBService = Depends(get_mongodb)
):
    """
    Crear un nuevo evento
    """
    try:
        if not db.is_connected():
            raise HTTPException(
                status_code=500,
                detail="No hay conexión a MongoDB"
            )
        
        # Preparar documento para insertar
        event_doc = {
            "title": event.title,
            "start": event.start.isoformat(),
            "end": event.end.isoformat() if event.end else None,
            "location": event.location,
            "description": event.description,
            "created_at": datetime.now().isoformat(),
            "updated_at": None
        }
        
        # Insertar en MongoDB
        collection = db.get_collection("events")
        result = collection.insert_one(event_doc)
        
        # Obtener el evento creado
        created_event = db.find_by_id("events", str(result.inserted_id))
        
        if not created_event:
            raise HTTPException(
                status_code=500,
                detail="Evento creado pero no se pudo recuperar"
            )
        
        return EventResponse(
            _id=str(created_event["_id"]),
            title=created_event["title"],
            start=created_event["start"],
            end=created_event.get("end"),
            location=created_event.get("location"),
            description=created_event.get("description"),
            created_at=created_event.get("created_at", ""),
            updated_at=created_event.get("updated_at")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: str,
    db: MongoDBService = Depends(get_mongodb)
):
    """
    Obtener un evento específico por ID
    """
    try:
        if not db.is_valid_object_id(event_id):
            raise HTTPException(
                status_code=400,
                detail="ID de evento inválido"
            )
        
        event = db.find_by_id("events", event_id)
        if not event:
            raise HTTPException(
                status_code=404,
                detail="Evento no encontrado"
            )
        
        return EventResponse(
            _id=str(event["_id"]),
            title=event["title"],
            start=event["start"],
            end=event.get("end"),
            location=event.get("location"),
            description=event.get("description"),
            created_at=event.get("created_at", ""),
            updated_at=event.get("updated_at")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: str,
    event_update: EventUpdate,
    db: MongoDBService = Depends(get_mongodb)
):
    """
    Actualizar un evento existente
    """
    try:
        if not db.is_valid_object_id(event_id):
            raise HTTPException(
                status_code=400,
                detail="ID de evento inválido"
            )
        
        # Verificar que el evento existe
        existing_event = db.find_by_id("events", event_id)
        if not existing_event:
            raise HTTPException(
                status_code=404,
                detail="Evento no encontrado"
            )
        
        # Preparar campos a actualizar
        update_fields = {}
        if event_update.title is not None:
            update_fields["title"] = event_update.title
        if event_update.start is not None:
            update_fields["start"] = event_update.start.isoformat()
        if event_update.end is not None:
            update_fields["end"] = event_update.end.isoformat()
        if event_update.location is not None:
            update_fields["location"] = event_update.location
        if event_update.description is not None:
            update_fields["description"] = event_update.description
        
        # Agregar fecha de actualización
        update_fields["updated_at"] = datetime.now().isoformat()
        
        # Actualizar en MongoDB
        collection = db.get_collection("events")
        result = collection.update_one(
            {"_id": ObjectId(event_id)},
            {"$set": update_fields}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=400,
                detail="No se pudo actualizar el evento"
            )
        
        # Obtener evento actualizado
        updated_event = db.find_by_id("events", event_id)
        
        return EventResponse(
            _id=str(updated_event["_id"]),
            title=updated_event["title"],
            start=updated_event["start"],
            end=updated_event.get("end"),
            location=updated_event.get("location"),
            description=updated_event.get("description"),
            created_at=updated_event.get("created_at", ""),
            updated_at=updated_event.get("updated_at")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.delete("/{event_id}")
async def delete_event(
    event_id: str,
    db: MongoDBService = Depends(get_mongodb)
):
    """
    Eliminar un evento
    """
    try:
        if not db.is_valid_object_id(event_id):
            raise HTTPException(
                status_code=400,
                detail="ID de evento inválido"
            )
        
        # Verificar que el evento existe
        existing_event = db.find_by_id("events", event_id)
        if not existing_event:
            raise HTTPException(
                status_code=404,
                detail="Evento no encontrado"
            )
        
        # Eliminar evento
        collection = db.get_collection("events")
        result = collection.delete_one({"_id": ObjectId(event_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=400,
                detail="No se pudo eliminar el evento"
            )
        
        return {
            "message": "Evento eliminado exitosamente",
            "event_id": event_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )
