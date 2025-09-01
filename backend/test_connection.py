#!/usr/bin/env python3
"""
Script para probar la conexión a MongoDB
"""
import os
from dotenv import load_dotenv
from services.mongodb_service import MongoDBService

def test_mongodb_connection():
    """Probar conexión a MongoDB"""
    print("🔍 Probando conexión a MongoDB...")
    
    # Cargar variables de entorno
    load_dotenv()
    
    # Obtener configuración
    mongodb_uri = os.getenv("MONGODB_URI")
    database_name = os.getenv("MONGODB_DATABASE", "universidad_db")
    
    if not mongodb_uri:
        print("❌ Error: MONGODB_URI no está configurada en el archivo .env")
        return False
    
    print(f"📡 URI: {mongodb_uri}")
    print(f"🗄️  Base de datos: {database_name}")
    
    # Crear instancia del servicio
    mongo_service = MongoDBService(mongodb_uri, database_name)
    
    # Intentar conectar
    if mongo_service.connect():
        print("✅ Conexión exitosa a MongoDB")
        
        # Probar operaciones básicas
        try:
            # Contar documentos en colecciones
            events_count = mongo_service.count_documents("events")
            lost_items_count = mongo_service.count_documents("lost_items")
            users_count = mongo_service.count_documents("usuarios")
            
            print(f"📊 Estadísticas de la base de datos:")
            print(f"   - Eventos: {events_count}")
            print(f"   - Objetos perdidos: {lost_items_count}")
            print(f"   - Usuarios: {users_count}")
            
            # Cerrar conexión
            mongo_service.disconnect()
            print("🔌 Conexión cerrada")
            return True
            
        except Exception as e:
            print(f"❌ Error al consultar la base de datos: {str(e)}")
            mongo_service.disconnect()
            return False
    else:
        print("❌ Error al conectar a MongoDB")
        return False

if __name__ == "__main__":
    test_mongodb_connection()
