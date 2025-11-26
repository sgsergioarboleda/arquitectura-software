"""
Schedule generation routes
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from typing import Dict, Any
import traceback

from schemas.schedule_schemas import (
    ScheduleGenerationResponse,
    ErrorResponse
)
from services.schedule_service import schedule_service
from Auth.auth_dependencies import require_admin

router = APIRouter(prefix="/schedule", tags=["schedule"])


@router.post(
    "/generate",
    response_model=ScheduleGenerationResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate schedule from Excel file",
    description="Upload an Excel file with course schedule data and generate optimized timetables using AI"
)
async def generate_schedule(
    file: UploadFile = File(..., description="Excel file with schedule data (.xlsx or .xls)"),
    current_user: dict = Depends(require_admin)
):
    """
    Generate an optimized schedule from an Excel file.
    
    The Excel file must contain the following columns:
    - Clase: Class name
    - Profesor: Professor name
    - Dia de la semana: Day of the week (Lunes, Martes, etc.)
    - grupo: Group identifier
    - disponibilidad del docente: Professor availability (HH:MM-HH:MM format)
    
    Returns:
        ScheduleGenerationResponse with scheduled and unscheduled sessions
    """
    
    # Validate file format
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    file_ext = file.filename.lower().split('.')[-1]
    if file_ext not in ['xlsx', 'xls']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file format. Expected .xlsx or .xls, got .{file_ext}"
        )
    
    try:
        # Read file content
        content = await file.read()
        
        if len(content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty file provided"
            )
        
        # Generate schedule
        result = await schedule_service.generate_schedule(content)
        
        # Return response
        return ScheduleGenerationResponse(
            scheduled=result["scheduled"],
            unscheduled=result["unscheduled"],
            justification=result.get("justification"),
            total_scheduled=result["total_scheduled"],
            total_unscheduled=result["total_unscheduled"],
            message=f"Schedule generated: {result['total_scheduled']} scheduled, {result['total_unscheduled']} unscheduled"
        )
        
    except HTTPException:
        raise
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Configuration error: {str(e)}"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid data format: {str(e)}"
        )
    except Exception as e:
        print(f"Error generating schedule: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating schedule: {str(e)}"
        )


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Check schedule service health"
)
async def schedule_health():
    """
    Check if the schedule generation service is available.
    
    Returns:
        Status information about the service
    """
    import os
    from services.schedule_service import ROOMS_FILE
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    rooms_exists = os.path.exists(ROOMS_FILE)
    
    # Get current working directory for debugging
    cwd = os.getcwd()
    
    return {
        "status": "healthy" if (gemini_key and rooms_exists) else "degraded",
        "gemini_configured": bool(gemini_key),
        "rooms_file_exists": rooms_exists,
        "rooms_file_path": ROOMS_FILE,
        "current_working_directory": cwd,
        "message": "Schedule generation service is operational" if (gemini_key and rooms_exists) else "Service configuration incomplete"
    }