## Integrantes 
* Santiago Garzón
* Brayan Guerrero
* David Martinez

## Proyecto de automatizacion de tareas Escuela de Ciencias de la Computacion e Inteligencia Artificial
Sergio Arboleda

## Objetivo General
Automatizar diversas tareas de la Universidad Sergio Arboleda con el fin de mejorar la capacidad de toma decisiones tanto para estudiantes como para profesores.

## Objetivos especificos
* Generacion automatizada de horarios para profesores y estudiantes impulsado por Inteligencia Artificial, teniendo en cuenta las diferentes variables que esto implica.
* Automatizar la gestion de entrega y recuperacion de objetos perdidos desde el area de Decanatura de estudiantes.
* Automatizaciones de horarios de eventos  y actividades universitarias, debido a que entre tantos canales de comunicaciones, muchos eventos pasan desapercibidos.
* Canal informativo estudiantil relacionado al conocimiento de becas estudiantiles a las que los estudiantes pueden acceder, asi como conocer sus requerimientos y condiciones.
* Crear un portal web donde se integren los anteriores proyectos.

# Sistema de Gestión Universitaria

Sistema completo de gestión universitaria con frontend React/TypeScript y backend FastAPI/MongoDB.

## Características

### Frontend (React + TypeScript)
- **React 18** con TypeScript
- **Vite** como bundler
- **Tailwind CSS** para estilos
- **React Router** para navegación
- **Axios** para llamadas a la API
- **FullCalendar** para calendario de eventos
- **React Hook Form** con validación Zod

### Backend (FastAPI + MongoDB)
- **FastAPI** framework web moderno
- **MongoDB** base de datos NoSQL
- **JWT** autenticación
- **CORS** configurado para frontend
- **Rate Limiting** protección
- **Pydantic** validación de datos

## Funcionalidades

### 📅 Calendario de Eventos
- Ver eventos universitarios
- Crear, editar y eliminar eventos
- Vista de calendario interactiva

### 🔍 Objetos Perdidos
- Listar objetos perdidos
- Búsqueda por título o ubicación
- Reclamar objetos con evidencias
- Subir imágenes de objetos

### 👥 Gestión de Usuarios
- Registro e inicio de sesión
- Roles de usuario (estudiante/admin)
- CRUD completo de usuarios

## Instalación y Configuración

### Prerrequisitos
- Node.js 18+ y npm
- Python 3.8+
- MongoDB Atlas (gratuito)

### 1. Clonar el repositorio
```bash
git clone <repository-url>
cd taller-crud
```

### 2. Configurar Backend

```bash
cd backend

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp env.example .env
# Editar .env con tus credenciales de MongoDB

# Probar conexión a MongoDB
python test_connection.py

# Poblar base de datos con datos de ejemplo
python scripts/populate_db.py

# Ejecutar servidor
python run.py
```

El backend estará disponible en `http://localhost:8000`

### 3. Configurar Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Configurar variables de entorno (opcional)
# Crear .env.local si necesitas cambiar la URL del backend

# Ejecutar servidor de desarrollo
npm run dev
```

El frontend estará disponible en `http://localhost:5173`

## Variables de Entorno

### Backend (.env)
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
```

### Frontend (.env.local) - Opcional
```env
VITE_API_URL=http://localhost:8000
```

## Estructura del Proyecto

```
taller-crud/
├── backend/                 # Backend FastAPI
│   ├── main.py             # Punto de entrada
│   ├── requirements.txt    # Dependencias Python
│   ├── routes/            # Rutas de la API
│   ├── services/          # Servicios de negocio
│   ├── schemas/           # Esquemas Pydantic
│   ├── auth/              # Autenticación
│   └── scripts/           # Scripts de utilidad
├── frontend/               # Frontend React
│   ├── src/               # Código fuente
│   ├── components/        # Componentes React
│   ├── pages/            # Páginas de la aplicación
│   ├── api/              # Cliente API
│   └── types/            # Tipos TypeScript
└── README.md             # Este archivo
```

## API Endpoints

### Eventos
- `GET /events` - Listar eventos
- `POST /events` - Crear evento
- `GET /events/{id}` - Obtener evento
- `PUT /events/{id}` - Actualizar evento
- `DELETE /events/{id}` - Eliminar evento

### Objetos Perdidos
- `GET /lost` - Listar objetos perdidos
- `POST /lost` - Crear objeto perdido
- `GET /lost/{id}` - Obtener objeto
- `GET /lost/{id}/image` - Obtener imagen
- `POST /lost/{id}/claim` - Reclamar objeto
- `PUT /lost/{id}` - Actualizar objeto
- `DELETE /lost/{id}` - Eliminar objeto

### Usuarios
- `GET /user/list` - Listar usuarios
- `POST /users/create` - Crear usuario
- `GET /user/{id}` - Obtener usuario
- `PUT /user/{id}` - Actualizar usuario
- `DELETE /user/{id}` - Eliminar usuario

### Autenticación
- `POST /auth/login` - Iniciar sesión
- `POST /auth/register` - Registrarse
- `POST /auth/refresh` - Renovar token

## Documentación

- **Backend API**: `http://localhost:8000/docs` (Swagger UI)
- **Backend ReDoc**: `http://localhost:8000/redoc`

## Desarrollo

### Backend
```bash
cd backend
python run.py  # Con recarga automática
```

### Frontend
```bash
cd frontend
npm run dev    # Con recarga automática
```

### Scripts Útiles

```bash
# Probar conexión a MongoDB
cd backend && python test_connection.py

# Poblar base de datos
cd backend && python scripts/populate_db.py

# Construir frontend para producción
cd frontend && npm run build
```

## Notas Importantes

- La autenticación está temporalmente deshabilitada para facilitar las pruebas
- El backend incluye CORS configurado para el frontend
- Los archivos de imágenes se almacenan en `backend/uploads/`
- El rate limiting está configurado para 100 requests por hora por IP

## Tecnologías Utilizadas

### Frontend
- React 18
- TypeScript
- Vite
- Tailwind CSS
- React Router DOM
- Axios
- FullCalendar
- React Hook Form
- Zod

### Backend
- FastAPI
- MongoDB (PyMongo)
- JWT (python-jose)
- Passlib (bcrypt)
- Python-multipart
- Python-dotenv
- Uvicorn

## Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

