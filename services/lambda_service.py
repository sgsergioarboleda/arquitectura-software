import requests
import logging
from fastapi import HTTPException
from services.config_service import config_service

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

# Instancia global
lambda_service = LambdaService()