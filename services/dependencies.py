from fastapi import HTTPException, Depends
from services.mongodb_service import MongoDBService
from services.config_service import config_service

# Instancia del servicio MongoDB usando configuración
mongo_service = MongoDBService(
    config_service.mongodb_uri,
    config_service.mongodb_database
)

# Dependency para verificar conexión a MongoDB
async def get_mongodb():
    if not mongo_service.is_connected():
        if not mongo_service.connect():
            raise HTTPException(status_code=500, detail="Error de conexión a MongoDB")
    return mongo_service
