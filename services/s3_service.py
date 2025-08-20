import boto3
import logging
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException
from services.config_service import config_service

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

# Instancia global
s3_service = S3Service()