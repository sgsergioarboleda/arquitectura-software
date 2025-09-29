from datetime import datetime
from typing import List
from schemas.event_schemas import EventCreate, EventUpdate, EventResponse

class EventService:
    @staticmethod
    def validate_event_dates(start: datetime, end: Optional[datetime]) -> None:
        """Validar que las fechas del evento sean correctas."""
        if end and start >= end:
            raise ValueError("La fecha de inicio debe ser anterior a la fecha de fin")

    @staticmethod
    def create_event(event_data: EventCreate) -> EventResponse:
        """Crear un evento y devolver su representación."""
        EventService.validate_event_dates(event_data.start, event_data.end)
        now = datetime.utcnow()
        return EventResponse(
            _id="generated_id",  # Aquí se generaría el ID real (por ejemplo, desde MongoDB)
            title=event_data.title,
            start=event_data.start.isoformat(),
            end=event_data.end.isoformat() if event_data.end else None,
            location=event_data.location,
            description=event_data.description,
            created_at=now.isoformat(),
            updated_at=now.isoformat(),
        )

    @staticmethod
    def update_event(event: EventResponse, update_data: EventUpdate) -> EventResponse:
        """Actualizar un evento existente."""
        updated_event = event.copy(update=update_data.dict(exclude_unset=True))
        EventService.validate_event_dates(
            datetime.fromisoformat(updated_event.start),
            datetime.fromisoformat(updated_event.end) if updated_event.end else None,
        )
        updated_event.updated_at = datetime.utcnow().isoformat()
        return updated_event

    @staticmethod
    def filter_events_by_date(events: List[EventResponse], date: datetime) -> List[EventResponse]:
        """Filtrar eventos por una fecha específica."""
        return [
            event for event in events
            if datetime.fromisoformat(event.start).date() == date.date()
        ]