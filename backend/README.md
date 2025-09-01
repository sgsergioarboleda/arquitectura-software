# Backend API - Universidad

Backend desarrollado con FastAPI y MongoDB para gestionar usuarios, eventos y objetos perdidos.

## Características

- **FastAPI**: Framework web moderno y rápido
- **MongoDB**: Base de datos NoSQL
- **Autenticación JWT**: Sistema de autenticación seguro
- **CORS**: Configurado para frontend React
- **Rate Limiting**: Protección contra spam
- **Validación de datos**: Con Pydantic

## Endpoints Principales

### Eventos (`/events`)
- `GET /events` - Obtener todos los eventos
- `POST /events` - Crear nuevo evento
- `GET /events/{id}` - Obtener evento específico
- `PUT /events/{id}` - Actualizar evento
- `DELETE /events/{id}` - Eliminar evento

### Objetos Perdidos (`/lost`)
- `GET /lost` - Listar objetos perdidos (con búsqueda opcional)
- `POST /lost` - Crear nuevo objeto perdido
- `GET /lost/{id}` - Obtener objeto específico
- `GET /lost/{id}/image` - Obtener imagen del objeto
- `POST /lost/{id}/claim` - Reclamar objeto perdido
- `PUT /lost/{id}` - Actualizar objeto perdido
- `DELETE /lost/{id}` - Eliminar objeto perdido

### Usuarios (`/user`)
- `GET /user/list` - Listar usuarios
- `POST /users/create` - Crear usuario
- `GET /user/{id}` - Obtener usuario específico
- `PUT /user/{id}` - Actualizar usuario
- `DELETE /user/{id}` - Eliminar usuario

### Autenticación (`/auth`)
- `POST /auth/login` - Iniciar sesión
- `POST /auth/register` - Registrarse
- `POST /auth/refresh` - Renovar token

## Instalación

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd backend
```

2. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno**
```bash
cp env.example .env
# Editar .env con tus credenciales de MongoDB
```

4. **Configurar MongoDB**
- Crear una base de datos en MongoDB Atlas
- Obtener la URI de conexión
- Configurar en el archivo `.env`

5. **Poblar base de datos con datos de ejemplo**
```bash
python scripts/populate_db.py
```

6. **Ejecutar el servidor**
```bash
python main.py
```

El servidor estará disponible en `http://localhost:8000`

## Variables de Entorno

Crear un archivo `.env` con las siguientes variables:

```env
# MongoDB
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/database
MONGODB_DATABASE=universidad_db

# JWT
JWT_SECRET_KEY=tu_clave_secreta_muy_larga
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App
APP_HOST=0.0.0.0
APP_PORT=8000
APP_DEBUG=true

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
```

## Estructura del Proyecto

```
backend/
├── main.py                 # Punto de entrada de la aplicación
├── requirements.txt        # Dependencias de Python
├── env.example            # Ejemplo de variables de entorno
├── README.md              # Este archivo
├── scripts/
│   └── populate_db.py     # Script para poblar datos de ejemplo
├── schemas/               # Esquemas Pydantic
│   ├── event_schemas.py
│   └── lost_item_schemas.py
├── routes/                # Rutas de la API
│   ├── event_routes.py
│   ├── lost_routes.py
│   └── storage_routes.py
├── services/              # Servicios de negocio
│   ├── mongodb_service.py
│   ├── auth_service.py
│   └── ...
├── auth/                  # Autenticación
│   ├── auth_routes.py
│   └── auth_service.py
└── users/                 # Gestión de usuarios
    └── schemas/
        └── user_schemas.py
```

## Documentación de la API

Una vez que el servidor esté ejecutándose, puedes acceder a:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Conexión con Frontend

El backend está configurado para aceptar conexiones desde:
- `http://localhost:5173` (Vite dev server)
- `http://127.0.0.1:5173`

## Notas Importantes

- La autenticación está temporalmente deshabilitada para facilitar las pruebas
- Los archivos de imágenes se almacenan en `uploads/lost_items/`
- El rate limiting está configurado para 100 requests por hora por IP
- Todos los endpoints devuelven respuestas JSON consistentes

## Desarrollo

Para desarrollo local:

```bash
# Ejecutar con recarga automática
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Ejecutar tests (si existen)
pytest

# Verificar linting
flake8 .
```
