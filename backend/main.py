import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
import importlib
import os

# Importar servicios
from services.config_service import config_service
from services.mongodb_service import MongoDBService
from services.password_service import password_service
from services.rate_limiter import rate_limiter

# Importar schemas de usuario
from users.schemas import UsuarioCreate, UsuarioUpdate, UsuarioResponse

# Importar autenticación
from Auth.auth_routes import auth_router
from Auth.auth_dependencies import get_current_user, get_current_user_id, require_admin, require_user, UserRole

# Importar dependencias compartidas
from services.dependencies import get_mongodb, mongo_service
from routes.storage_routes import router as storage_router
from routes.event_routes import router as event_router
from routes.lost_routes import router as lost_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events para manejar el ciclo de vida de la aplicación
    """
    # Startup
    print("🔄 Iniciando conexión a MongoDB Atlas...")
    if mongo_service.connect():
        print("✅ Conexión exitosa a MongoDB Atlas")
    else:
        print("❌ Error al conectar a MongoDB Atlas")
    
    if not config_service.validate_configuration():
        print("❌ Error en la configuración. Revisa las variables de entorno.")
        exit(1)
    
    print(f"🚀 Iniciando API en {config_service.app_host}:{config_service.app_port}")
    print(f"🌍 Debug: {config_service.app_debug}")
    
    yield
    
    # Shutdown
    print("🔄 Cerrando conexiones...")
    if mongo_service.is_connected():
        mongo_service.close()
        print("✅ Conexiones cerradas")

# Crear instancia de FastAPI con lifespan
app = FastAPI(
    title="API de Universidad",
    description="API CRUD completa para gestión de usuarios, eventos y objetos perdidos con MongoDB",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS para permitir conexión con el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Frontend Vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    is_limited, current_requests = await rate_limiter.is_rate_limited(client_ip)
    
    if is_limited:
        return JSONResponse(
            status_code=429,
            content={
                "error": "Too many requests",
                "detail": "Rate limit exceeded. Try again later."
            }
        )
    
    response = await call_next(request)
    return response

# Incluir rutas de autenticación
app.include_router(auth_router)
# Include storage routes
app.include_router(storage_router)
# Include event routes
app.include_router(event_router)
# Include lost items routes
app.include_router(lost_router)

# Los schemas de usuario están ahora en users/schemas/user_schemas.py

# Endpoint de salud (público)
@app.get("/health")
async def health_check():
    try:
        # Verificar conexión a MongoDB
        if not mongo_service.is_connected():
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": "MongoDB no conectado",
                    "mongodb_connected": False,
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "message": "API funcionando correctamente",
                "mongodb_connected": True,
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Error interno: {str(e)}",
                "mongodb_connected": False,
                "timestamp": datetime.now().isoformat()
            }
        )

# Endpoint de información de la API (público)
@app.get("/")
async def api_info():
    """
    Endpoint público que proporciona información básica de la API
    """
    return {
        "name": "API de Universidad",
        "version": "1.0.0",
        "description": "API CRUD completa para gestión de usuarios, eventos y objetos perdidos",
        "endpoints": {
            "public": [
                "GET / - Información de la API",
                "GET /health - Estado de salud del sistema",
                "POST /auth/login - Iniciar sesión"
            ],
            "protected": [
                "GET /events - Listar eventos",
                "GET /lost - Listar objetos perdidos",
                "GET /storage/* - Gestión de archivos"
            ],
            "admin_only": [
                "POST /events - Crear eventos",
                "PUT /events/{id} - Actualizar eventos",
                "DELETE /events/{id} - Eliminar eventos",
                "DELETE /lost/{id} - Eliminar objetos perdidos"
            ]
        },
        "authentication": "JWT con RSA256",
        "documentation": "/docs"
    }

# Endpoint de debug para MongoDB
@app.get("/debug/mongodb")
async def debug_mongodb(db: MongoDBService = Depends(get_mongodb)):
    try:
        # Verificar conexión
        is_connected = db.is_connected()
        
        if not is_connected:
            return {
                "status": "error",
                "message": "No hay conexión a MongoDB",
                "connection": False,
                "timestamp": datetime.now().isoformat()
            }
        
        # Formatear usuarios para mostrar
        usuarios_formateados = []
        for usuario in usuarios_ejemplo:
            usuarios_formateados.append({
                "id": str(usuario["_id"]),
                "nombre": usuario.get("nombre", "N/A"),
                "correo": usuario.get("correo", "N/A"),
                "tipo": usuario.get("tipo", "N/A")
            })
        
        return {
            "status": "success",
            "message": "Conexión a MongoDB exitosa",
            "connection": True,
            "database": db.database_name,
            "total_usuarios": total_usuarios,
            "usuarios_ejemplo": usuarios_formateados,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error en debug: {str(e)}",
            "connection": False,
            "timestamp": datetime.now().isoformat()
        }

# Endpoint de debug para probar búsqueda por ID
@app.get("/debug/user/{user_id}")
async def debug_user_by_id(user_id: str, db: MongoDBService = Depends(get_mongodb)):
    """
    Endpoint de debug para probar la búsqueda de un usuario por ID
    """
    try:
        print(f"🔍 DEBUG: Buscando usuario con ID: {user_id}")
        
        # Validar formato del ID
        is_valid = db.is_valid_object_id(user_id)
        print(f"🔍 DEBUG: ID válido: {is_valid}")
        
        if not is_valid:
            return {
                "status": "error",
                "message": f"ID inválido: '{user_id}' no es un ObjectId válido",
                "id_provided": user_id,
                "is_valid_object_id": False,
                "timestamp": datetime.now().isoformat()
            }
        
        # Verificar conexión
        if not db.is_connected():
            return {
                "status": "error",
                "message": "No hay conexión a MongoDB",
                "id_provided": user_id,
                "is_valid_object_id": True,
                "connection": False,
                "timestamp": datetime.now().isoformat()
            }
        
        # Buscar usuario
        usuario = db.find_by_id_with_validation("usuarios", user_id)
        
        if not usuario:
            return {
                "status": "not_found",
                "message": f"Usuario no encontrado con ID: {user_id}",
                "id_provided": user_id,
                "is_valid_object_id": True,
                "connection": True,
                "usuario_encontrado": False,
                "timestamp": datetime.now().isoformat()
            }
        
        return {
            "status": "success",
            "message": f"Usuario encontrado con ID: {user_id}",
            "id_provided": user_id,
            "is_valid_object_id": True,
            "connection": True,
            "usuario_encontrado": True,
            "usuario": {
                "id": str(usuario["_id"]),
                "nombre": usuario.get("nombre", "N/A"),
                "correo": usuario.get("correo", "N/A"),
                "tipo": usuario.get("tipo", "N/A"),
                "fecha_creacion": usuario.get("fecha_creacion", "N/A")
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ DEBUG: Error en debug_user_by_id: {str(e)}")
        return {
            "status": "error",
            "message": f"Error interno: {str(e)}",
            "id_provided": user_id,
            "timestamp": datetime.now().isoformat()
        }

# ===== RUTAS ESPECÍFICAS (DEBEN IR ANTES QUE LAS RUTAS CON PARÁMETROS) =====

# CREATE - Crear usuario (ruta específica)
@app.post("/users/create", response_model=UsuarioResponse, status_code=201)
async def create_user(
    usuario: UsuarioCreate, 
    db: MongoDBService = Depends(get_mongodb),
    current_user: dict = Depends(require_admin)
):
    """Crear un nuevo usuario en la base de datos"""
    try:
        # Verificar permisos
        if current_user["tipo"].lower() != "admin":
            raise HTTPException(
                status_code=403, 
                detail="No tienes permisos para crear usuarios"
            )
        
        # Verificar si el correo ya existe
        usuario_existente = db.find_one("usuarios", {"correo": usuario.correo})
        if usuario_existente:
            raise HTTPException(
                status_code=400, 
                detail="Ya existe un usuario con este correo electrónico"
            )
        
        # Verificar que la contraseña sea segura
        es_fuerte, mensaje_error = password_service.is_password_strong(usuario.contraseña)
        if not es_fuerte:
            raise HTTPException(
                status_code=400,
                detail=f"La contraseña no cumple con los requisitos de seguridad: {mensaje_error}"
            )
        
        # Preparar documento para insertar
        usuario_doc = {
            "nombre": usuario.nombre,
            "correo": usuario.correo,
            "contraseña": password_service.hash_password(usuario.contraseña),  # Encriptar contraseña
            "tipo": usuario.tipo,
            "fecha_creacion": datetime.now().isoformat()
        }
        
        # Insertar en MongoDB
        collection = db.get_collection("usuarios")
        result = collection.insert_one(usuario_doc)
        
        print(f"✅ Usuario creado con ID: {result.inserted_id}")
        
        # Obtener el usuario creado usando el método mejorado
        usuario_creado = db.find_by_id_with_validation("usuarios", str(result.inserted_id))
        
        if not usuario_creado:
            raise HTTPException(
                status_code=500, 
                detail="Usuario creado pero no se pudo recuperar de la base de datos"
            )
        
        return UsuarioResponse(
            id=str(result.inserted_id),
            nombre=usuario_creado["nombre"],
            correo=usuario_creado["correo"],
            tipo=usuario_creado["tipo"],
            fecha_creacion=usuario_creado.get("fecha_creacion")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

# READ - Obtener todos los usuarios
@app.get("/user/list", response_model=List[UsuarioResponse])
async def get_all_users(
    skip: int = 0, 
    limit: int = 100, 
    db: MongoDBService = Depends(get_mongodb),
    _: dict = Depends(require_user)
):
    """
    Obtener lista de usuarios con paginación
    """
    try:
        if not db.is_connected():
            raise HTTPException(
                status_code=500,
                detail="No hay conexión a MongoDB"
            )
            
        usuarios = db.find_all("usuarios", limit=limit, skip=skip)
        
        if usuarios:
            print(f"Encontrados {len(usuarios)} usuarios")
            
        usuarios_response = []
        for usuario in usuarios:
            usuarios_response.append(
                UsuarioResponse(
                    id=str(usuario["_id"]),
                    nombre=usuario["nombre"],
                    correo=usuario["correo"],
                    tipo=usuario["tipo"],
                    fecha_creacion=usuario.get("fecha_creacion")
                )
            )
        
        return usuarios_response
        
    except Exception as e:
        print(f"ERROR en get_all_users: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

# READ - Buscar usuario por correo (ruta específica)
@app.get("/user/search/email/{email}")
async def search_user_by_email(
    email: str, 
    db: MongoDBService = Depends(get_mongodb),
    current_user: dict = Depends(get_current_user)
):
    """
    Buscar usuario por correo electrónico
    """
    try:
        usuario = db.find_one("usuarios", {"correo": email})
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        return UsuarioResponse(
            id=str(usuario["_id"]),
            nombre=usuario["nombre"],
            correo=usuario["correo"],
            tipo=usuario["tipo"],
            fecha_creacion=usuario.get("fecha_creacion")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

# DELETE - Eliminar todos los usuarios (ADMIN ONLY) (ruta específica)
@app.delete("/user/delete/all")
async def delete_all_users(
    db: MongoDBService = Depends(get_mongodb),
    current_user: dict = Depends(require_admin)  # Cambiar _ por current_user
):
    """
    Eliminar todos los usuarios (solo para administradores)
    """
    
    if current_user["tipo"].lower() != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos para eliminar usuarios")
    
    try:
        # Obtener colección
        collection = db.get_collection("usuarios")
        
        # Contar usuarios antes de eliminar
        total_usuarios = db.count_documents("usuarios")
        
        # Eliminar todos los usuarios
        result = collection.delete_many({})
        
        return {
            "message": "Todos los usuarios han sido eliminados",
            "usuarios_eliminados": result.deleted_count,
            "total_anterior": total_usuarios
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

# ===== RUTAS CON PARÁMETROS (DEBEN IR DESPUÉS DE LAS RUTAS ESPECÍFICAS) =====

# READ - Obtener usuario por ID
@app.get("/user/{user_id}", response_model=UsuarioResponse)
async def get_user_by_id(
    user_id: str, 
    db: MongoDBService = Depends(get_mongodb),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener un usuario específico por su ID
    """
    try:
        # Validar formato del ID
        if not db.is_valid_object_id(user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"ID inválido: '{user_id}' no es un ObjectId válido"
            )
        
        print(f"🔍 Buscando usuario con ID: {user_id}")
        
        # Buscar usuario usando el método mejorado
        usuario = db.find_by_id_with_validation("usuarios", user_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        print(f"✅ Usuario encontrado: {usuario.get('nombre', 'N/A')}")
        
        return UsuarioResponse(
            id=str(usuario["_id"]),
            nombre=usuario["nombre"],
            correo=usuario["correo"],
            tipo=usuario["tipo"],
            fecha_creacion=usuario.get("fecha_creacion")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error en get_user_by_id: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

# UPDATE - Actualizar usuario
@app.put("/user/{user_id}", response_model=UsuarioResponse)
async def update_user(
    user_id: str, 
    usuario_update: UsuarioUpdate, 
    db: MongoDBService = Depends(get_mongodb),
    current_user: dict = Depends(get_current_user)
):
    """
    Actualizar un usuario existente
    """
    
    if current_user["tipo"].lower() != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos para editar usuarios")
    
    try:
        # Validar formato del ID
        if not db.is_valid_object_id(user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"ID inválido: '{user_id}' no es un ObjectId válido"
            )
        
        print(f"🔍 Verificando existencia del usuario con ID: {user_id}")
        
        # Verificar que el usuario existe usando el método mejorado
        usuario_existente = db.find_by_id_with_validation("usuarios", user_id)
        if not usuario_existente:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        print(f"✅ Usuario encontrado para actualizar: {usuario_existente.get('nombre', 'N/A')}")
        
        # Preparar campos a actualizar
        update_fields = {}
        if usuario_update.nombre is not None:
            update_fields["nombre"] = usuario_update.nombre
        if usuario_update.correo is not None:
            # Verificar que el nuevo correo no esté en uso por otro usuario
            if usuario_update.correo != usuario_existente["correo"]:
                usuario_con_correo = db.find_one("usuarios", {"correo": usuario_update.correo})
                if usuario_con_correo:
                    raise HTTPException(
                        status_code=400, 
                        detail="Ya existe un usuario con este correo electrónico"
                    )
            update_fields["correo"] = usuario_update.correo
        if usuario_update.contraseña is not None:
            # Verificar que la nueva contraseña sea segura
            es_fuerte, mensaje_error = password_service.is_password_strong(usuario_update.contraseña)
            if not es_fuerte:
                raise HTTPException(
                    status_code=400,
                    detail=f"La nueva contraseña no cumple con los requisitos de seguridad: {mensaje_error}"
                )
            # Encriptar la nueva contraseña
            update_fields["contraseña"] = password_service.hash_password(usuario_update.contraseña)
        if usuario_update.tipo is not None:
            update_fields["tipo"] = usuario_update.tipo
        
        # Agregar fecha de actualización
        update_fields["fecha_actualizacion"] = datetime.now().isoformat()
        
        # Actualizar en MongoDB
        collection = db.get_collection("usuarios")
        result = collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_fields}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="No se pudo actualizar el usuario")
        
        print(f"✅ Usuario actualizado exitosamente: {user_id}")
        
        # Obtener usuario actualizado
        usuario_actualizado = db.find_by_id_with_validation("usuarios", user_id)
        
        return UsuarioResponse(
            id=str(usuario_actualizado["_id"]),
            nombre=usuario_actualizado["nombre"],
            correo=usuario_actualizado["correo"],
            tipo=usuario_actualizado["tipo"],
            fecha_creacion=usuario_actualizado.get("fecha_creacion")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error en update_user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

# DELETE - Eliminar usuario
@app.delete("/user/{user_id}")
async def delete_user(
    user_id: str, 
    db: MongoDBService = Depends(get_mongodb),
    current_user: dict = Depends(get_current_user)
):
    if current_user["tipo"].lower() != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos para eliminar usuarios")
    
    try:
        # Validar formato del ID
        if not db.is_valid_object_id(user_id):
            raise HTTPException(
                status_code=400,
                detail="ID de usuario inválido"
            )
            
        # Eliminar usuario
        collection = db.get_collection("usuarios")
        result = collection.delete_one({"_id": ObjectId(user_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=404,
                detail="Usuario no encontrado"
            )
            
        return {
            "message": "Usuario eliminado exitosamente",
            "user_id": user_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

# Cargar configuración global
config = config_service._load_configuration()

# Cargar plugins dinámicamente
def load_plugins(app: FastAPI, config: dict):
    plugins_dir = "backend/plugins"
    for filename in os.listdir(plugins_dir):
        if filename.endswith("_plugin.py"):
            module_name = f"plugins.{filename[:-3]}"
            module = importlib.import_module(module_name)
            plugin_class = getattr(module, "Plugin")
            plugin_instance = plugin_class()
            plugin_instance.initialize(config)
            plugin_instance.register_routes(app)

@app.on_event("startup")
async def startup_event():
    load_plugins(app, config)

@app.get("/")
async def root():
    """Endpoint raíz de la API"""
    return {
        "message": "Bienvenido a la API de Usuarios",
        "version": "1.0.0"
    }


def main():
    print(f"🚀 Iniciando servidor")
    # Ejecutar servidor usando la configuración del servicio
    uvicorn.run(
        "main:app",
        host=config_service.app_host,
        port=config_service.app_port,
        reload=config_service.app_debug,
        log_level="info"
    )

if __name__ == "__main__":
    main()
