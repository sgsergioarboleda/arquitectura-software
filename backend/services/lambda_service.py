import requests
import logging
from fastapi import HTTPException
from services.config_service import config_service
from urllib.parse import urlparse

class LambdaService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_url = config_service.lambda_api_url

    async def validate_data(self, data: dict) -> dict:
        try:
            response = requests.post(self.api_url, json=data)
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Error en validación Lambda"
                )
        except Exception as e:
            self.logger.error(f"Error Lambda: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error al conectar con Lambda"
            )

    def _validate_url(self, url: str) -> bool:
        """Validar URL para prevenir SSRF"""
        try:
            parsed = urlparse(url)
            return all([
                parsed.scheme in ['http', 'https'],
                not parsed.netloc.startswith('127.'),
                not parsed.netloc.startswith('localhost'),
                not parsed.netloc.startswith('169.254.'),
                not parsed.netloc.startswith('10.'),
                not parsed.netloc.startswith('172.16.'),
                not parsed.netloc.startswith('192.168.')
            ])
        except Exception:
            return False

# Instancia global
lambda_service = LambdaService()