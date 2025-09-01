# Sistema de Autenticación JWT con RSA

## Descripción

El sistema de autenticación utiliza JWT (JSON Web Tokens) firmados con llaves RSA para mayor seguridad. Las llaves se almacenan en el directorio `keys/` y se cargan automáticamente al iniciar el servicio.

## Configuración

### 1. Generar Llaves RSA

Si las llaves no existen, ejecuta:

```bash
cd backend
python generate_keys.py
```

Esto creará:
- `keys/private.pem` - Llave privada para firmar tokens
- `keys/public.pem` - Llave pública para verificar tokens

### 2. Configurar Variables de Entorno

En tu archivo `.env`, asegúrate de tener:

```env
# Secret Manager Configuration
SECRET_PASSWORD_PEPPER=tu-pepper-secreto-aqui

# JWT Configuration (ya no se usa, pero mantener para compatibilidad)
SECRET_PHRASE=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30
```

## Endpoints Públicos

Los siguientes endpoints no requieren autenticación:

- `GET /` - Información de la API
- `GET /health` - Estado de salud del sistema
- `POST /auth/login` - Iniciar sesión

## Endpoints Protegidos

### Requieren Autenticación (cualquier usuario)

- `GET /events` - Listar eventos
- `GET /events/{id}` - Obtener evento específico
- `GET /lost` - Listar objetos perdidos
- `GET /lost/{id}` - Obtener objeto perdido específico
- `GET /lost/{id}/image` - Obtener imagen de objeto perdido
- `GET /lost/{id}/miniature` - Obtener miniatura de objeto perdido
- `POST /lost` - Crear objeto perdido
- `PUT /lost/{id}` - Actualizar objeto perdido
- `POST /lost/{id}/claim` - Reclamar objeto perdido
- `POST /lost/{id}/miniature` - Subir miniatura
- `GET /auth/verify` - Verificar token
- `POST /storage/upload` - Subir archivo
- `GET /storage/file/{filename}` - Obtener archivo

### Requieren Rol de Administrador

- `POST /events` - Crear evento
- `PUT /events/{id}` - Actualizar evento
- `DELETE /events/{id}` - Eliminar evento
- `DELETE /lost/{id}` - Eliminar objeto perdido
- `POST /storage/validate` - Validar datos

## Uso de la API

### 1. Iniciar Sesión

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "correo": "usuario@ejemplo.com",
    "contraseña": "tu-contraseña"
  }'
```

Respuesta:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...",
  "token_type": "bearer",
  "user_id": "507f1f77bcf86cd799439011",
  "correo": "usuario@ejemplo.com",
  "nombre": "Usuario Ejemplo",
  "tipo": "usuario"
}
```

### 2. Usar Token en Requests

```bash
curl -X GET "http://localhost:8000/events" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..."
```

### 3. Verificar Token

```bash
curl -X GET "http://localhost:8000/auth/verify" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..."
```

## Seguridad

### Ventajas de RSA sobre HMAC

1. **Separación de responsabilidades**: Solo el servidor puede firmar tokens (llave privada)
2. **Verificación distribuida**: Múltiples servicios pueden verificar tokens (llave pública)
3. **Mayor seguridad**: Las llaves RSA son más difíciles de comprometer

### Mejores Prácticas

1. **Mantener llaves seguras**: Nunca compartas la llave privada
2. **Rotación de llaves**: Cambia las llaves periódicamente
3. **Almacenamiento seguro**: Usa variables de entorno para configuraciones sensibles
4. **Logs de auditoría**: Registra intentos de acceso y cambios de estado

## Estructura del Token JWT

```json
{
  "user_id": "507f1f77bcf86cd799439011",
  "correo": "usuario@ejemplo.com",
  "tipo": "usuario",
  "exp": 1640995200,
  "iat": 1640991600
}
```

## Manejo de Errores

### 401 Unauthorized
- Token faltante o inválido
- Token expirado
- Formato incorrecto del token

### 403 Forbidden
- Usuario no tiene permisos para la operación
- Rol insuficiente para el endpoint

### 429 Too Many Requests
- Rate limiting activado
- Demasiadas solicitudes en un período corto

## Troubleshooting

### Error: "No se pudieron cargar las llaves RSA"
- Verifica que existan los archivos `keys/private.pem` y `keys/public.pem`
- Ejecuta `python generate_keys.py` para generarlas

### Error: "Token inválido"
- Verifica que el token esté en el formato correcto: `Bearer <token>`
- Asegúrate de que el token no haya expirado
- Verifica que las llaves RSA sean las correctas

### Error: "No tienes los permisos necesarios"
- Verifica que el usuario tenga el rol requerido
- Los endpoints de administrador requieren rol "admin"
