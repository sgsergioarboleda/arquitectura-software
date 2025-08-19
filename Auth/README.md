# Sistema de Autenticación JWT

Este módulo implementa un sistema completo de autenticación basado en JWT (JSON Web Tokens) para la API de usuarios.

## Características

- **Login**: Autenticación de usuarios con correo y contraseña
- **JWT**: Generación y verificación de tokens de acceso
- **Protección de endpoints**: Todos los endpoints de usuarios requieren autenticación
- **Verificación de tokens**: Middleware automático para validar tokens en cada petición

## Endpoints

### POST /auth/login
Autentica un usuario y devuelve un token JWT.

**Request Body:**
```json
{
    "correo": "usuario@ejemplo.com",
    "contraseña": "contraseña123"
}
```

**Response:**
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "user_id": "507f1f77bcf86cd799439011",
    "correo": "usuario@ejemplo.com",
    "nombre": "Usuario Ejemplo",
    "tipo": "usuario"
}
```

### POST /auth/logout
Endpoint para logout (el token se invalida en el cliente).

**Response:**
```json
{
    "message": "Logout exitoso. El token ha sido invalidado en el cliente."
}
```

### GET /auth/verify
Verifica la validez de un token JWT.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "valid": true,
    "user_id": "507f1f77bcf86cd799439011",
    "message": "Token válido"
}
```

## Uso de Tokens

Para acceder a los endpoints protegidos, incluye el token en el header de autorización:

```
Authorization: Bearer <tu_token_jwt>
```

## Configuración

### Variables de Entorno

```bash
# Clave secreta para firmar JWT (OBLIGATORIO cambiar en producción)
SECRET_PHRASE=tu-clave-super-secreta-aqui

# Algoritmo de JWT (opcional, por defecto HS256)
JWT_ALGORITHM=HS256

# Tiempo de expiración en minutos (opcional, por defecto 30)
JWT_EXPIRATION_MINUTES=30
```

### Seguridad

⚠️ **IMPORTANTE**: 
- Cambia `SECRET_PHRASE` en producción
- Usa una clave secreta fuerte y única
- No compartas la clave secreta en el código
- Considera usar variables de entorno del sistema en producción

## Estructura del Token

El payload del JWT contiene:

```json
{
    "user_id": "507f1f77bcf86cd799439011",
    "correo": "usuario@ejemplo.com",
    "tipo": "usuario",
    "exp": 1640995200
}
```

## Endpoints Protegidos

Todos los siguientes endpoints requieren autenticación:

- `POST /user/create` - Crear usuario
- `GET /user/list` - Listar usuarios
- `GET /user/{user_id}` - Obtener usuario por ID
- `GET /user/search/email/{email}` - Buscar usuario por correo
- `PUT /user/{user_id}` - Actualizar usuario
- `DELETE /user/{user_id}` - Eliminar usuario
- `DELETE /user/delete/all` - Eliminar todos los usuarios

## Flujo de Autenticación

1. **Login**: Usuario envía correo y contraseña
2. **Verificación**: Sistema verifica credenciales en MongoDB
3. **Generación**: Si son válidas, se genera un JWT con el ID del usuario
4. **Acceso**: Cliente incluye el token en headers para acceder a endpoints protegidos
5. **Verificación**: Cada petición verifica automáticamente la validez del token

## Notas de Implementación

- Las contraseñas se comparan sin cifrado por el momento (requerido para producción)
- Los tokens expiran automáticamente según la configuración
- El sistema verifica que el usuario exista en cada petición autenticada
- Se incluye manejo de errores para tokens inválidos o expirados
