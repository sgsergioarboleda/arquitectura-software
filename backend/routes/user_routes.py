from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from datetime import datetime
from bson import ObjectId

# Importar servicios
from services.mongodb_service import MongoDBService
from services.password_service import password_service
from services.dependencies import get_mongodb

# Importar schemas
from users.schemas import UsuarioCreate, UsuarioUpdate, UsuarioResponse

# Importar autenticación
from Auth.auth_dependencies import require_admin

# Crear router con prefijo /admin/users
router = APIRouter(prefix="/admin/users", tags=["Administración de Usuarios"])


@router.get("/", response_model=List[UsuarioResponse])
async def get_all_users(
    skip: int = 0, 
    limit: int = 100, 
    db: MongoDBService = Depends(get_mongodb),
    _: dict = Depends(require_admin)
):
    """
    Obtener lista de todos los usuarios (solo admin)
    """
    try:
        if not db.is_connected():
            raise HTTPException(
                status_code=500,
                detail="No hay conexión a MongoDB"
            )
            
        usuarios = db.find_all("usuarios", limit=limit, skip=skip)
        
        if usuarios:
            print(f"✅ Encontrados {len(usuarios)} usuarios")
            
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
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ERROR en get_all_users: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.get("/{user_id}", response_model=UsuarioResponse)
async def get_user_by_id(
    user_id: str, 
    db: MongoDBService = Depends(get_mongodb),
    _: dict = Depends(require_admin)
):
    """
    Obtener un usuario específico por su ID (solo admin)
    """
    try:
        # Validar formato del ID
        if not db.is_valid_object_id(user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"ID inválido: '{user_id}' no es un ObjectId válido"
            )
        
        print(f"🔍 Buscando usuario con ID: {user_id}")
        
        # Buscar usuario
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


@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    usuario: UsuarioCreate, 
    db: MongoDBService = Depends(get_mongodb),
    _: dict = Depends(require_admin)
):
    """
    Crear un nuevo usuario (solo admin)
    """
    try:
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
            "contraseña": password_service.hash_password(usuario.contraseña),
            "tipo": usuario.tipo,
            "fecha_creacion": datetime.now().isoformat()
        }
        
        # Insertar en MongoDB
        collection = db.get_collection("usuarios")
        result = collection.insert_one(usuario_doc)
        
        print(f"✅ Usuario creado con ID: {result.inserted_id}")
        
        # Obtener el usuario creado
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
        print(f"❌ Error en create_user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.put("/{user_id}", response_model=UsuarioResponse)
async def update_user(
    user_id: str, 
    usuario_update: UsuarioUpdate, 
    db: MongoDBService = Depends(get_mongodb),
    _: dict = Depends(require_admin)
):
    """
    Actualizar un usuario existente (solo admin)
    """
    try:
        # Validar formato del ID
        if not db.is_valid_object_id(user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"ID inválido: '{user_id}' no es un ObjectId válido"
            )
        
        print(f"🔍 Verificando existencia del usuario con ID: {user_id}")
        
        # Verificar que el usuario existe
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
        
        # Si no hay campos para actualizar
        if not update_fields:
            raise HTTPException(
                status_code=400,
                detail="No se proporcionaron campos para actualizar"
            )
        
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


@router.delete("/{user_id}")
async def delete_user(
    user_id: str, 
    db: MongoDBService = Depends(get_mongodb),
    _: dict = Depends(require_admin)
):
    """
    Eliminar un usuario (solo admin)
    """
    try:
        # Validar formato del ID
        if not db.is_valid_object_id(user_id):
            raise HTTPException(
                status_code=400,
                detail="ID de usuario inválido"
            )
        
        print(f"🗑️ Intentando eliminar usuario con ID: {user_id}")
        
        # Verificar que el usuario existe antes de eliminar
        usuario_existente = db.find_by_id_with_validation("usuarios", user_id)
        if not usuario_existente:
            raise HTTPException(
                status_code=404,
                detail="Usuario no encontrado"
            )
            
        # Eliminar usuario
        collection = db.get_collection("usuarios")
        result = collection.delete_one({"_id": ObjectId(user_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=500,
                detail="Error al eliminar el usuario"
            )
        
        print(f"✅ Usuario eliminado exitosamente: {user_id}")
            
        return {
            "message": "Usuario eliminado exitosamente",
            "user_id": user_id,
            "nombre": usuario_existente.get("nombre"),
            "correo": usuario_existente.get("correo")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error en delete_user: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get("/search/email/{email}", response_model=UsuarioResponse)
async def search_user_by_email(
    email: str, 
    db: MongoDBService = Depends(get_mongodb),
    _: dict = Depends(require_admin)
):
    """
    Buscar usuario por correo electrónico (solo admin)
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
        print(f"❌ Error en search_user_by_email: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

