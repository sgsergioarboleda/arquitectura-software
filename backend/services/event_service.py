from datetime import datetime
from typing import List, Optional
from bson import ObjectId
from schemas.event_schemas import EventCreate, EventUpdate, EventResponse

class EventService:
    @staticmethod
    def validate_event_dates(start: datetime, end: Optional[datetime]) -> None:
        """Validar que las fechas del evento sean correctas."""
        if end and start >= end:
            raise ValueError("La fecha de inicio debe ser anterior a la fecha de fin")

    @staticmethod
    def validate_event_id(event_id: str, db) -> None:
        """Validar que el ID sea válido."""
        if not db.is_valid_object_id(event_id):
            raise ValueError("ID de evento inválido")

    @staticmethod
    def create_event(event_data: EventCreate, db) -> EventResponse:
        """Crear un nuevo evento."""
        event_doc = {
            "title": event_data.title,
            "start": event_data.start.isoformat(),
            "end": event_data.end.isoformat() if event_data.end else None,
            "location": event_data.location,
            "description": event_data.description,
            "created_at": datetime.now().isoformat(),
            "updated_at": None
        }
        collection = db.get_collection("events")
        result = collection.insert_one(event_doc)
        return EventService.get_event_by_id(str(result.inserted_id), db)

    @staticmethod
    def get_event_by_id(event_id: str, db) -> EventResponse:
        """Obtener un evento por ID."""
        EventService.validate_event_id(event_id, db)
        event = db.find_by_id("events", event_id)
        if not event:
            raise ValueError("Evento no encontrado")
        return EventService._convert_to_response(event)

    @staticmethod
    def update_event(event_id: str, event_update: EventUpdate, db) -> EventResponse:
        """Actualizar un evento existente."""
        EventService.validate_event_id(event_id, db)
        existing_event = db.find_by_id("events", event_id)
        if not existing_event:
            raise ValueError("Evento no encontrado")

        update_fields = {k: v for k, v in event_update.dict(exclude_unset=True).items()}
        update_fields["updated_at"] = datetime.now().isoformat()

        collection = db.get_collection("events")
        result = collection.update_one(
            {"_id": ObjectId(event_id)},
            {"$set": update_fields}
        )
        if result.modified_count == 0:
            raise ValueError("No se pudo actualizar el evento")
        return EventService.get_event_by_id(event_id, db)

    @staticmethod
    def delete_event(event_id: str, db) -> dict:
        """Eliminar un evento."""
        EventService.validate_event_id(event_id, db)
        existing_event = db.find_by_id("events", event_id)
        if not existing_event:
            raise ValueError("Evento no encontrado")

        collection = db.get_collection("events")
        result = collection.delete_one({"_id": ObjectId(event_id)})
        if result.deleted_count == 0:
            raise ValueError("No se pudo eliminar el evento")
        return {"message": "Evento eliminado exitosamente", "event_id": event_id}

    @staticmethod
    def filter_events_by_date(events: List[EventResponse], date: datetime) -> List[EventResponse]:
        """Filtrar eventos por una fecha específica."""
        return [
            event for event in events
            if datetime.fromisoformat(event.start).date() == date.date()
        ]

    @staticmethod
    def _convert_to_response(event) -> EventResponse:
        """Convertir un documento de MongoDB a EventResponse."""
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