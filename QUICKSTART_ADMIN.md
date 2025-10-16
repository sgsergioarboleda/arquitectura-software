# Guía Rápida - Dashboard de Administración

## 🚀 Inicio Rápido

### 1. Crear Usuario Administrador

Primero, crea un usuario administrador para poder acceder al dashboard:

```bash
cd backend
python scripts/create_admin.py
```

Esto creará un usuario con las siguientes credenciales:
- **Email**: `admin@universidad.edu`
- **Contraseña**: `Admin123!`

### 2. Iniciar el Backend

```bash
cd backend
python main.py
```

El servidor debería iniciarse en `http://localhost:8000`

### 3. Iniciar el Frontend

En otra terminal:

```bash
cd frontend
npm install  # Solo la primera vez
npm run dev
```

El frontend debería iniciarse en `http://localhost:5173`

### 4. Acceder al Dashboard

1. Abre tu navegador en `http://localhost:5173`
2. Inicia sesión con:
   - Email: `admin@universidad.edu`
   - Contraseña: `Admin123!`
3. Una vez autenticado, verás el link "Administración" en la barra de navegación
4. Haz clic en "Administración" para acceder al dashboard

## 📋 Funcionalidades Disponibles

### Ver Usuarios
- Al entrar al dashboard, verás una tabla con todos los usuarios
- Información: nombre, correo, tipo y fecha de creación

### Crear Usuario
1. Haz clic en "+ Crear Usuario"
2. Completa el formulario:
   - Nombre
   - Correo electrónico
   - Contraseña (mínimo 8 caracteres, con mayúsculas, minúsculas y números)
   - Tipo: Usuario o Admin
3. Haz clic en "Crear Usuario"

### Editar Usuario
1. Encuentra el usuario en la tabla
2. Haz clic en "Editar"
3. Modifica los campos que desees
4. Deja el campo de contraseña vacío si no quieres cambiarla
5. Haz clic en "Guardar Cambios"

### Eliminar Usuario
1. Encuentra el usuario en la tabla
2. Haz clic en "Eliminar"
3. Confirma la acción

## 🔒 Seguridad

### Requisitos de Contraseña
Las contraseñas deben cumplir con:
- Mínimo 8 caracteres
- Al menos una letra mayúscula
- Al menos una letra minúscula
- Al menos un número

### Restricciones
- Solo usuarios con rol `admin` pueden acceder al dashboard
- Usuarios regulares no verán el link de administración
- Si un usuario no-admin intenta acceder a `/admin`, será redirigido

## 🧪 Usuarios de Prueba

El script `create_admin.py` también puede crear usuarios de prueba:

```bash
python scripts/create_admin.py
# Responde 's' cuando te pregunte si deseas crear usuarios de prueba
```

Esto creará:
- Juan Pérez (usuario regular)
- María García (usuario regular)
- Contraseña para ambos: `Usuario123!`

## 📡 API Endpoints

Todos bajo el prefijo `/admin/users/`:

- `GET /admin/users/` - Listar usuarios
- `GET /admin/users/{id}` - Obtener usuario
- `POST /admin/users/` - Crear usuario
- `PUT /admin/users/{id}` - Actualizar usuario
- `DELETE /admin/users/{id}` - Eliminar usuario

**Nota**: Todos los endpoints requieren autenticación con token JWT y rol de admin.

## 🐛 Solución de Problemas

### "No tienes los permisos necesarios"
- Verifica que estás usando un usuario con rol `admin`
- Verifica que el token no haya expirado (cierra sesión e inicia nuevamente)

### "Token inválido"
- El token puede haber expirado
- Cierra sesión y vuelve a iniciar sesión

### No veo el link "Administración"
- Verifica que tu usuario tenga rol `admin`
- Revisa en la base de datos: el campo `tipo` debe ser `"admin"` (no `"Admin"` o `"ADMIN"`)

### Error de conexión a MongoDB
- Verifica que MongoDB esté corriendo
- Verifica las variables de entorno en `.env`
- Verifica la conexión con `python test_connection.py`

## 📚 Documentación Completa

Para más información detallada, consulta:
- [ADMIN_DASHBOARD.md](./ADMIN_DASHBOARD.md) - Documentación completa del sistema
- [backend/Auth/README.md](./backend/Auth/README.md) - Sistema de autenticación
- [backend/AUTHENTICATION.md](./backend/AUTHENTICATION.md) - Detalles de autenticación

## 💡 Tips

1. **Cambia la contraseña del admin**: Después de crear el usuario admin por primera vez, cámbiala desde el dashboard
2. **No elimines todos los admins**: Asegúrate de siempre tener al menos un usuario admin
3. **Usa contraseñas seguras**: Especialmente para usuarios admin
4. **Prueba con usuarios de prueba**: Usa los usuarios de prueba para experimentar sin riesgo

## 🎯 Siguiente Paso

Una vez que hayas probado el dashboard, considera:
1. Cambiar la contraseña del usuario admin
2. Crear tus propios usuarios admin
3. Eliminar el usuario admin de prueba si lo deseas
4. Eliminar los usuarios de prueba creados

¡Listo! Ya puedes administrar usuarios desde el dashboard. 🎉

