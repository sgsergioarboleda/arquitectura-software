from fastapi import APIRouter, HTTPException, Depends
from services.dependencies import get_mongodb, MongoDBService
from Auth.auth_dependencies import require_auth, require_admin
from schemas.event_schemas import EventCreate, EventUpdate, EventResponse
from services.event_service import EventService

router = APIRouter(prefix="/events", tags=["events"])

@router.get("/", response_model=list[EventResponse])
async def get_events(db: MongoDBService = Depends(get_mongodb)):
    try:
        events = db.find_all("events", limit=100)
        return [EventService._convert_to_response(event) for event in events]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=EventResponse, status_code=201)
async def create_event(event: EventCreate, db: MongoDBService = Depends(get_mongodb)):
    try:
        return EventService.create_event(event, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: str, db: MongoDBService = Depends(get_mongodb)):
    try:
        return EventService.get_event_by_id(event_id, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{event_id}", response_model=EventResponse)
async def update_event(event_id: str, event_update: EventUpdate, db: MongoDBService = Depends(get_mongodb)):
    try:
        return EventService.update_event(event_id, event_update, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{event_id}")
async def delete_event(event_id: str, db: MongoDBService = Depends(get_mongodb)):
    try:
        return EventService.delete_event(event_id, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
