from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class LostItemCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    found_location: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    contact_info: Optional[str] = Field(None, max_length=200)

class LostItemUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    found_location: Optional[str] = Field(None, min_length=1, max_length=200)
    status: Optional[str] = Field(None, pattern="^(available|claimed|returned)$")
    description: Optional[str] = Field(None, max_length=1000)
    contact_info: Optional[str] = Field(None, max_length=200)

class LostItemResponse(BaseModel):
    _id: str
    title: str
    found_location: str
    status: str  # "available", "claimed", "returned"
    description: Optional[str] = None
    contact_info: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None

class LostItemsListResponse(BaseModel):
    items: List[LostItemResponse]

class ClaimRequest(BaseModel):
    notes: str = Field(..., min_length=1, max_length=1000)

class ClaimResponse(BaseModel):
    message: str
    claim_id: str
    status: str
