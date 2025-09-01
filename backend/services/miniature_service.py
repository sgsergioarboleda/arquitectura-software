import logging
from fastapi import HTTPException, UploadFile
from services.s3_service import s3_service
from PIL import Image
import io
import os

class MiniatureService:
    """
    Servicio para gestionar miniaturas de imágenes usando S3
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.miniature_size = (300, 300)  # Tamaño de la miniatura
        self.quality = 85  # Calidad de la imagen JPEG
    
    async def upload_miniature(self, item_id: str, image_file: UploadFile) -> dict:
        """
        Sube una miniatura de imagen para un item perdido
        
        Args:
            item_id: ID del item perdido
            image_file: Archivo de imagen a procesar
            
        Returns:
            dict: Información de la miniatura subida
        """
        try:
            # Leer la imagen original
            image_data = await image_file.read()
            image = Image.open(io.BytesIO(image_data))
            
            # Convertir a RGB si es necesario
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Crear miniatura
            miniature = image.copy()
            miniature.thumbnail(self.miniature_size, Image.Resampling.LANCZOS)
            
            # Guardar miniatura en buffer
            miniature_buffer = io.BytesIO()
            miniature.save(miniature_buffer, format='PNG', optimize=True)
            miniature_buffer.seek(0)
            
            # Generar nombre del archivo
            miniature_filename = f"miniatures/{item_id}_miniature.png"
            
            # Subir a S3
            result = await s3_service.upload_file(miniature_buffer, miniature_filename)
            
            self.logger.info(f"Miniatura subida exitosamente para item {item_id}")
            return {
                "item_id": item_id,
                "miniature_url": result["url"],
                "filename": result["filename"]
            }
            
        except Exception as e:
            self.logger.error(f"Error al crear miniatura para item {item_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error al procesar la miniatura: {str(e)}"
            )
    
    async def get_miniature_url(self, item_id: str) -> str:
        """
        Obtiene la URL de la miniatura para un item perdido
        
        Args:
            item_id: ID del item perdido
            
        Returns:
            str: URL de la miniatura
        """
        try:
            miniature_filename = f"miniatures/{item_id}_miniature.png"
            url = await s3_service.get_file_url(miniature_filename)
            return url
            
        except HTTPException as e:
            if e.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail=f"No se encontró miniatura para el item {item_id}"
                )
            raise e
        except Exception as e:
            self.logger.error(f"Error al obtener miniatura para item {item_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error al obtener la miniatura: {str(e)}"
            )
    
    async def delete_miniature(self, item_id: str) -> bool:
        """
        Elimina la miniatura de un item perdido
        
        Args:
            item_id: ID del item perdido
            
        Returns:
            bool: True si se eliminó correctamente
        """
        try:
            miniature_filename = f"miniatures/{item_id}_miniature.png"
            
            # Eliminar de S3
            s3_service.s3.delete_object(
                Bucket=s3_service.bucket,
                Key=miniature_filename
            )
            
            self.logger.info(f"Miniatura eliminada exitosamente para item {item_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al eliminar miniatura para item {item_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error al eliminar la miniatura: {str(e)}"
            )

# Instancia global del servicio de miniaturas
miniature_service = MiniatureService()
