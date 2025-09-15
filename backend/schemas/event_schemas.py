from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class EventCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=3,
        max_length=200,
        regex=r'^[A-Za-z0-9\sÁÉÍÓÚÑáéíóúñ]+$'
    )
    start: datetime
    end: Optional[datetime] = None
    location: Optional[str] = Field(
        None,
        max_length=200,
        regex=r'^[A-Za-z0-9\sÁÉÍÓÚÑáéíóúñ]*$'
    )
    description: Optional[str] = Field(None, max_length=1000)

class EventUpdate(BaseModel):
    title: Optional[str] = Field(
        None,
        min_length=3,
        max_length=200,
        regex=r'^[A-Za-z0-9\sÁÉÍÓÚÑáéíóúñ]+$'
    )
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    location: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)

class EventResponse(BaseModel):
    _id: str
    title: str
    start: str  # ISO string
    end: Optional[str] = None  # ISO string
    location: Optional[str] = None
    description: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None

class EventsListResponse(BaseModel):
    events: list[EventResponse]
