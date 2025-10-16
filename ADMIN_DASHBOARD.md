# Panel de Administración de Usuarios

## Descripción

Se ha implementado un sistema completo de administración de usuarios que permite a los administradores gestionar todos los usuarios del sistema desde una interfaz web.

## Características

### Seguridad
- ✅ **Acceso restringido**: Solo usuarios con rol `admin` pueden acceder al dashboard
- ✅ **Protección en frontend**: El link solo se muestra a usuarios admin
- ✅ **Protección en backend**: Todas las rutas requieren autenticación y rol admin
- ✅ **Validación de contraseñas**: Las contraseñas deben cumplir con requisitos de seguridad

### Funcionalidades

#### 1. Listar Usuarios
- Ver todos los usuarios del sistema en una tabla organizada
- Información mostrada:
  - Nombre
  - Correo electrónico
  - Tipo de usuario (admin/usuario)
  - Fecha de creación

#### 2. Crear Usuarios
- Formulario modal para crear nuevos usuarios
- Campos requeridos:
  - Nombre
  - Correo electrónico
  - Contraseña
  - Tipo de usuario (admin/usuario)
- Validaciones:
  - Correo único
  - Contraseña segura

#### 3. Editar Usuarios
- Modificar información de usuarios existentes
- Campos editables:
  - Nombre
  - Correo electrónico
  - Contraseña (opcional)
  - Tipo de usuario
- Solo actualiza los campos modificados

#### 4. Eliminar Usuarios
- Eliminar usuarios del sistema
- Confirmación antes de eliminar
- No se puede deshacer

## Estructura de Archivos

### Backend

#### `/backend/routes/user_routes.py`
Rutas para gestión de usuarios (solo admin):
- `GET /admin/users/` - Listar todos los usuarios
- `GET /admin/users/{user_id}` - Obtener un usuario por ID
- `POST /admin/users/` - Crear un nuevo usuario
- `PUT /admin/users/{user_id}` - Actualizar un usuario
- `DELETE /admin/users/{user_id}` - Eliminar un usuario
- `GET /admin/users/search/email/{email}` - Buscar usuario por email

#### `/backend/main.py` (actualizado)
- Integra las rutas de administración de usuarios

### Frontend

#### `/frontend/api/users.ts`
Cliente API con funciones para:
- `getAllUsers()` - Obtener lista de usuarios
- `getUserById()` - Obtener usuario específico
- `createUser()` - Crear nuevo usuario
- `updateUser()` - Actualizar usuario
- `deleteUser()` - Eliminar usuario
- `searchUserByEmail()` - Buscar por email

#### `/frontend/pages/AdminDashboard.tsx`
Componente principal del dashboard con:
- Tabla de usuarios
- Modal de creación
- Modal de edición
- Confirmación de eliminación
- Mensajes de éxito/error
- Estados de carga

#### `/frontend/routes/AppRouter.tsx` (actualizado)
- Nueva ruta `/admin` protegida

#### `/frontend/components/Layout.tsx` (actualizado)
- Link "Administración" visible solo para admins

#### `/frontend/types/index.ts` (actualizado)
- Tipo `User.role` ajustado para coincidir con backend: `"usuario" | "admin"`

## Uso

### Acceso al Dashboard

1. Inicia sesión con un usuario que tenga rol `admin`
2. En la barra de navegación, haz clic en "Administración"
3. Serás redirigido a `/admin`

### Crear un Usuario

1. Haz clic en el botón "+ Crear Usuario"
2. Completa el formulario:
   - Nombre completo
   - Correo electrónico
   - Contraseña segura
   - Tipo de usuario (Usuario o Admin)
3. Haz clic en "Crear Usuario"
4. El usuario aparecerá en la tabla

### Editar un Usuario

1. En la tabla, haz clic en "Editar" junto al usuario deseado
2. Modifica los campos necesarios
3. Para cambiar la contraseña, ingresa una nueva (dejar vacío para mantener la actual)
4. Haz clic en "Guardar Cambios"

### Eliminar un Usuario

1. En la tabla, haz clic en "Eliminar" junto al usuario deseado
2. Confirma la acción en el diálogo
3. El usuario será eliminado permanentemente

## Requisitos

### Backend
- FastAPI
- MongoDB
- Sistema de autenticación JWT implementado
- Roles de usuario: `admin` y `usuario`

### Frontend
- React
- TypeScript
- TailwindCSS
- React Router
- Axios

## Seguridad Implementada

1. **Autenticación JWT**: Todas las peticiones requieren token válido
2. **Autorización por Rol**: Solo admins pueden acceder a las rutas
3. **Validación de Contraseñas**: Requisitos de seguridad en backend
4. **Sanitización de Datos**: Validación con Pydantic en backend
5. **Protección de Rutas**: Componente `ProtectedRoute` en frontend
6. **Verificación de Rol**: El dashboard verifica el rol antes de renderizar

## Tipos de Usuario

- **admin**: Acceso completo al dashboard de administración
- **usuario**: Usuario regular sin acceso administrativo

## Notas Importantes

- Los administradores pueden crear otros administradores
- No se puede eliminar el último administrador del sistema (considerar implementar esta validación)
- Las contraseñas se hashean antes de almacenarse
- El sistema valida que los correos sean únicos
- Los cambios son inmediatos y se reflejan en la tabla

## Endpoints de API

Todas las rutas están bajo `/admin/users/` y requieren:
- Header `Authorization: Bearer {token}`
- Rol de usuario: `admin`

### Respuestas de Error

- `401 Unauthorized`: Token inválido o expirado
- `403 Forbidden`: Usuario sin permisos de administrador
- `400 Bad Request`: Datos inválidos o correo duplicado
- `404 Not Found`: Usuario no encontrado
- `500 Internal Server Error`: Error del servidor

## Mejoras Futuras Sugeridas

1. Paginación para grandes cantidades de usuarios
2. Filtros y búsqueda en la tabla
3. Exportar lista de usuarios (CSV/PDF)
4. Historial de cambios (audit log)
5. Validación para no eliminar el último admin
6. Suspender usuarios en lugar de eliminarlos
7. Reseteo de contraseñas por email
8. Bulk operations (acciones masivas)

