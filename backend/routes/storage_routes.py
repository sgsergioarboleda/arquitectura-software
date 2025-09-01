from fastapi import APIRouter, UploadFile, File, Depends
from services.s3_service import s3_service
from services.lambda_service import lambda_service
from Auth.auth_dependencies import require_user, require_admin

router = APIRouter(prefix="/storage", tags=["storage"])

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    _: dict = Depends(require_user)  # Cualquier usuario autenticado puede subir archivos
):
    result = await s3_service.upload_file(file.file, file.filename)
    return result

@router.get("/file/{filename}")
async def get_file(
    filename: str,
    _: dict = Depends(require_user)  # Cualquier usuario autenticado puede ver archivos
):
    url = await s3_service.get_file_url(filename)
    return {"url": url}

@router.post("/validate")
async def validate_data(
    data: dict,
    _: dict = Depends(require_admin)  # Solo admins pueden validar datos
):
    result = await lambda_service.validate_data(data)
    return result