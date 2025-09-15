from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal

class TipoUsuario:
    USUARIO = "usuario"
    ADMIN = "admin"
    TIPOS_VALIDOS = Literal["usuario", "admin"]

class UsuarioBase(BaseModel):
    """
    Schema base para usuarios.
    Contiene los campos comunes requeridos para crear y actualizar usuarios.
    """
    nombre: str = Field(
        ...,
        strip_whitespace=True,
        min_length=3,
        max_length=100,
        regex=r'^[A-Za-z0-9\sÁÉÍÓÚÑáéíóúñ]+$'
    )
    correo: EmailStr
    contraseña: str
    tipo: TipoUsuario.TIPOS_VALIDOS = TipoUsuario.USUARIO

class UsuarioCreate(UsuarioBase):
    """Schema para crear un nuevo usuario."""
    pass

class UsuarioUpdate(BaseModel):
    """
    Schema para actualizar un usuario existente.
    Todos los campos son opcionales para permitir actualizaciones parciales.
    Aplica la misma validación de caracteres al nombre si se incluye.
    """
    nombre: Optional[str] = Field(
        None,
        strip_whitespace=True,
        min_length=3,
        max_length=100,
        regex=r'^[A-Za-z0-9\sÁÉÍÓÚÑáéíóúñ]+$'
    )
    correo: Optional[EmailStr] = None
    contraseña: Optional[str] = None
    tipo: Optional[TipoUsuario.TIPOS_VALIDOS] = None

class UsuarioResponse(BaseModel):
    """Schema para respuestas de la API."""
    id: str
    nombre: str
    correo: str
    tipo: TipoUsuario.TIPOS_VALIDOS
    fecha_creacion: Optional[str] = None

    class Config:
        from_attributes = True
        extra = "ignore"
