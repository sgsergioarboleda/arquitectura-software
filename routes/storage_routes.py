from fastapi import APIRouter, UploadFile, File, Depends
from services.s3_service import s3_service
from services.lambda_service import lambda_service
from auth.auth_dependencies import get_current_user

router = APIRouter(prefix="/storage", tags=["storage"])

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    result = await s3_service.upload_file(file.file, file.filename)
    return result

@router.get("/file/{filename}")
async def get_file(
    filename: str,
    current_user: dict = Depends(get_current_user)
):
    url = await s3_service.get_file_url(filename)
    return {"url": url}

@router.post("/validate")
async def validate_data(
    data: dict,
    current_user: dict = Depends(get_current_user)
):
    result = await lambda_service.validate_data(data)
    return result