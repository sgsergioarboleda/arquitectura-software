from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class EventCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    start: datetime
    end: Optional[datetime] = None
    location: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)

class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    location: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)

class EventResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    id: str = Field(serialization_alias="_id")
    title: str
    start: str  # ISO string
    end: Optional[str] = None  # ISO string
    location: Optional[str] = None
    description: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None

class EventsListResponse(BaseModel):
    events: list[EventResponse]
