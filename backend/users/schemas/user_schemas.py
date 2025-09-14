from pydantic import BaseModel, EmailStr
from typing import Optional, Literal

class TipoUsuario:
    """
    Clase para definir los tipos de usuario válidos
    Centraliza la definición de tipos para seguir el principio DRY
    """
    USUARIO = "usuario"
    ADMIN = "admin"
    
    # Lista de todos los tipos válidos para usar en Literal
    TIPOS_VALIDOS = Literal["usuario", "admin"]

class UsuarioBase(BaseModel):
    """
    Schema base para usuarios
    Contiene los campos comunes requeridos para crear y actualizar usuarios
    """
    nombre: str
    correo: EmailStr
    contraseña: str
    tipo: TipoUsuario.TIPOS_VALIDOS = TipoUsuario.USUARIO  # Solo puede ser "usuario" o "admin"

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
    tipo: Optional[TipoUsuario.TIPOS_VALIDOS] = None

class UsuarioResponse(BaseModel):
    """
    Schema para respuestas de la API
    No incluye la contraseña por seguridad
    """
    id: str
    nombre: str
    correo: str
    tipo: TipoUsuario.TIPOS_VALIDOS
    fecha_creacion: Optional[str] = None
    
    class Config:
        """
        Configuración del modelo Pydantic
        """
        # Permite crear el modelo desde un diccionario con campos adicionales
        from_attributes = True
        # Excluye campos no especificados en el modelo
        extra = "ignore" 