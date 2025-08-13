from pydantic import BaseModel, EmailStr
from typing import Optional

class UsuarioBase(BaseModel):
    """
    Schema base para usuarios
    Contiene los campos comunes requeridos para crear y actualizar usuarios
    """
    nombre: str
    correo: EmailStr
    contraseña: str
    tipo: str = "usuario"  # Por defecto es usuario, puede ser "admin"

class UsuarioCreate(UsuarioBase):
    """
    Schema para crear un nuevo usuario
    Hereda todos los campos de UsuarioBase
    """
    pass

class UsuarioUpdate(BaseModel):
    """
    Schema para actualizar un usuario existente
    Todos los campos son opcionales para permitir actualizaciones parciales
    """
    nombre: Optional[str] = None
    correo: Optional[EmailStr] = None
    contraseña: Optional[str] = None
    tipo: Optional[str] = None

class UsuarioResponse(BaseModel):
    """
    Schema para respuestas de la API
    No incluye la contraseña por seguridad
    """
    id: str
    nombre: str
    correo: str
    tipo: str
    fecha_creacion: Optional[str] = None
    
    class Config:
        """
        Configuración del modelo Pydantic
        """
        # Permite crear el modelo desde un diccionario con campos adicionales
        from_attributes = True
        # Excluye campos no especificados en el modelo
        extra = "ignore" 