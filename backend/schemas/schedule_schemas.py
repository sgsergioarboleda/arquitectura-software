"""
Schedule schemas for request/response validation
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class ScheduledSession(BaseModel):
    """Schema for a successfully scheduled session"""
    idx: int = Field(..., description="Session index")
    dia: str = Field(..., description="Day of the week (L/M/X/J/V)")
    clase: str = Field(..., description="Class name")
    Horario: str = Field(..., description="Time slot (HH:MM-HH:MM)")
    Profesor: str = Field(..., description="Professor name")
    grupo: Optional[str] = Field(None, description="Group identifier")
    Salon: str = Field(..., description="Room identifier")


class UnscheduledSession(BaseModel):
    """Schema for a session that could not be scheduled"""
    idx: Optional[int] = Field(None, description="Session index")
    clase: Optional[str] = Field(None, description="Class name")
    profesor: Optional[str] = Field(None, description="Professor name")
    dia: Optional[str] = Field(None, description="Original day preference")
    grupo: Optional[str] = Field(None, description="Group identifier")
    reason: str = Field(..., description="Reason why it couldn't be scheduled")


class ScheduleGenerationResponse(BaseModel):
    """Response schema for schedule generation endpoint"""
    scheduled: List[ScheduledSession] = Field(default_factory=list, description="Successfully scheduled sessions")
    unscheduled: List[UnscheduledSession] = Field(default_factory=list, description="Sessions that couldn't be scheduled")
    justification: Optional[str] = Field(None, description="AI explanation for unscheduled sessions")
    total_scheduled: int = Field(..., description="Total number of scheduled sessions")
    total_unscheduled: int = Field(..., description="Total number of unscheduled sessions")
    message: str = Field(default="Schedule generated successfully", description="Status message")


class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str = Field(..., description="Error type")
    detail: str = Field(..., description="Error details")
    message: str = Field(..., description="User-friendly error message")