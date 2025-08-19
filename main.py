from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List
import os
from datetime import datetime
from bson import ObjectId

# Importar servicios
from services.mongodb_service import MongoDBService
from services.config_service import config_service

# Importar schemas de usuario
from users.schemas import UsuarioCreate, UsuarioUpdate, UsuarioResponse

# Crear instancia de FastAPI
app = FastAPI(
    title="API de Usuarios",
    description="API CRUD completa para gestión de usuarios con MongoDB",
    version="1.0.0"
)

# Los schemas de usuario están ahora en users/schemas/user_schemas.py

# Instancia del servicio MongoDB usando configuración
mongo_service = MongoDBService(
    config_service.mongodb_uri,
    config_service.mongodb_database
)

# Dependency para verificar conexión a MongoDB
async def get_mongodb():
    if not mongo_service.is_connected():
        if not mongo_service.connect():
            raise HTTPException(status_code=500, detail="Error de conexión a MongoDB")
    return mongo_service

# Endpoint de salud
@app.get("/health")
async def health_check():
    """Endpoint de verificación de salud de la API"""
    return JSONResponse(
        status_code=200,
        content="API de Usuarios"
    )

@app.post("/user/create", response_model=UsuarioResponse, status_code=201)
async def create_user(usuario: UsuarioCreate, db: MongoDBService = Depends(get_mongodb)):
    """
    Crear un nuevo usuario en la base de datos
    """
    try:
        # Verificar si el correo ya existe
        usuario_existente = db.find_one("usuarios", {"correo": usuario.correo})
        if usuario_existente:
            raise HTTPException(
                status_code=400, 
                detail="Ya existe un usuario con este correo electrónico"
            )
        
        # Preparar documento para insertar
        usuario_doc = {
            "nombre": usuario.nombre,
            "correo": usuario.correo,
            "contraseña": usuario.contraseña,  # En producción, hashear la contraseña
            "tipo": usuario.tipo,
            "fecha_creacion": datetime.now().isoformat()
        }
        
        # Insertar en MongoDB
        collection = db.get_collection("usuarios")
        result = collection.insert_one(usuario_doc)
        
        # Obtener el usuario creado
        usuario_creado = db.find_by_id("usuarios", str(result.inserted_id))
        
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
    db: MongoDBService = Depends(get_mongodb)
):
    """
    Obtener lista de usuarios con paginación
    """
    try:
        # Obtener usuarios con límite y skip
        usuarios = db.find_all("usuarios", limit=limit)
        
        # Aplicar skip manualmente ya que find_all no lo soporta directamente
        usuarios = usuarios[skip:skip + limit]
        
        # Convertir a formato de respuesta
        usuarios_response = []
        for usuario in usuarios:
            usuarios_response.append(UsuarioResponse(
                id=str(usuario["_id"]),
                nombre=usuario["nombre"],
                correo=usuario["correo"],
                tipo=usuario["tipo"],
                fecha_creacion=usuario.get("fecha_creacion")
            ))
        
        return usuarios_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

# READ - Obtener usuario por ID
@app.get("/user/{user_id}", response_model=UsuarioResponse)
async def get_user_by_id(user_id: str, db: MongoDBService = Depends(get_mongodb)):
    """
    Obtener un usuario específico por su ID
    """
    try:
        # Validar formato del ID
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="ID de usuario inválido")
        
        # Buscar usuario
        usuario = db.find_by_id("usuarios", user_id)
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

# READ - Buscar usuario por correo
@app.get("/user/search/email/{email}")
async def search_user_by_email(email: str, db: MongoDBService = Depends(get_mongodb)):
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

# UPDATE - Actualizar usuario
@app.put("/user/{user_id}", response_model=UsuarioResponse)
async def update_user(
    user_id: str, 
    usuario_update: UsuarioUpdate, 
    db: MongoDBService = Depends(get_mongodb)
):
    """
    Actualizar un usuario existente
    """
    try:
        # Validar formato del ID
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="ID de usuario inválido")
        
        # Verificar que el usuario existe
        usuario_existente = db.find_by_id("usuarios", user_id)
        if not usuario_existente:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
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
            update_fields["contraseña"] = usuario_update.contraseña
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
        
        # Obtener usuario actualizado
        usuario_actualizado = db.find_by_id("usuarios", user_id)
        
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
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

# DELETE - Eliminar usuario
@app.delete("/user/{user_id}")
async def delete_user(user_id: str, db: MongoDBService = Depends(get_mongodb)):
    """
    Eliminar un usuario por su ID
    """
    try:
        # Validar formato del ID
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="ID de usuario inválido")
        
        # Verificar que el usuario existe
        usuario_existente = db.find_by_id("usuarios", user_id)
        if not usuario_existente:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Eliminar usuario
        collection = db.get_collection("usuarios")
        result = collection.delete_one({"_id": ObjectId(user_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=400, detail="No se pudo eliminar el usuario")
        
        return {
            "message": "Usuario eliminado exitosamente",
            "id": user_id,
            "nombre": usuario_existente["nombre"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

# DELETE - Eliminar todos los usuarios (ADMIN ONLY)
@app.delete("/user/delete/all")
async def delete_all_users(db: MongoDBService = Depends(get_mongodb)):
    """
    Eliminar todos los usuarios (solo para administradores)
    """
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

@app.get("/")
async def root():
    """Endpoint raíz de la API"""
    return {
        "message": "Bienvenido a la API de Usuarios",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    # Prueba de conexión
    print("🔄 Probando conexión a MongoDB Atlas...")
    if mongo_service.connect():
        print("✅ Conexión exitosa a MongoDB Atlas")
    else:
        print("❌ Error al conectar a MongoDB Atlas")
        exit(1)
    
    import uvicorn
    
    if not config_service.validate_configuration():
        print("❌ Error en la configuración. Revisa las variables de entorno.")
        exit(1)
    
    print(f"🚀 Iniciando API en {config_service.app_host}:{config_service.app_port}")
    print(f"🌍 Debug: {config_service.app_debug}")
    
    uvicorn.run(
        app, 
        host=config_service.app_host, 
        port=config_service.app_port
    )