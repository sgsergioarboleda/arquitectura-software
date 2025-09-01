from pydantic import BaseModel, EmailStr
from typing import Optional

class LoginRequest(BaseModel):
    """
    Esquema para la solicitud de login
    """
    correo: EmailStr
    contraseña: str

class LoginResponse(BaseModel):
    """
    Esquema para la respuesta de login
    """
    token: str

class LogoutResponse(BaseModel):
    """
    Esquema para la respuesta de logout
    """
    message: str

class TokenData(BaseModel):
    """
    Esquema para los datos del token
    """
    user_id: Optional[str] = None
