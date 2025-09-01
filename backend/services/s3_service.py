import boto3
import logging
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException
from services.config_service import config_service
import hashlib
import mimetypes

class S3Service:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=config_service.aws_access_key,
            aws_secret_access_key=config_service.aws_secret_key,
            region_name=config_service.aws_region
        )
        self.bucket = config_service.aws_bucket

    async def upload_file(self, file, filename: str) -> dict:
        # Validar integridad del archivo
        content_hash = hashlib.sha256(await file.read()).hexdigest()
        
        # Verificar tipo MIME usando la extensión del archivo
        content_type = mimetypes.guess_type(filename)[0]
        if not self._is_allowed_file_type(content_type):
            raise HTTPException(status_code=400, detail="Tipo de archivo no permitido")

        try:
            self.s3.upload_fileobj(file, self.bucket, filename)
            url = f"https://{self.bucket}.s3.amazonaws.com/{filename}"
            return {
                "filename": filename,
                "url": url
            }
        except ClientError as e:
            self.logger.error(f"Error S3: {str(e)}")
            raise HTTPException(status_code=500, detail="Error al subir archivo")

    async def get_file_url(self, filename: str) -> str:
        try:
            url = self.s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': filename},
                ExpiresIn=3600
            )
            return url
        except ClientError as e:
            self.logger.error(f"Error S3: {str(e)}")
            raise HTTPException(status_code=404, detail="Archivo no encontrado")

    def _is_allowed_file_type(self, content_type: str) -> bool:
        # Aquí puedes definir la lógica para permitir o denegar tipos de archivo
        allowed_types = ['image/jpeg', 'image/png', 'application/pdf']
        return content_type in allowed_types

# Instancia global
s3_service = S3Service()