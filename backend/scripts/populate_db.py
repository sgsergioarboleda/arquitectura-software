#!/usr/bin/env python3
"""
Script para poblar la base de datos con datos de ejemplo
"""
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Agregar el directorio padre al path para importar módulos
sys.path.append(str(Path(__file__).parent.parent))

from services.dependencies import mongo_service
from bson import ObjectId

# Cargar variables de entorno desde .env
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

# Leer las variables de entorno
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE")

print(f"MONGODB_URI: {MONGODB_URI}")
print(f"MONGODB_DATABASE: {MONGODB_DATABASE}")

if not MONGODB_URI or not MONGODB_DATABASE:
    print("❌ Archivo de configuración .env no encontrado o variables faltantes")
    exit(1)

def populate_events():
    """Poblar eventos de ejemplo"""
    try:
        collection = mongo_service.get_collection("events")
        if collection is None:
            print("❌ No se pudo obtener la colección de eventos")
            return

        events_data = [
            {
                "title": "Inicio de Clases",
                "start": (datetime.now() + timedelta(days=5)).isoformat(),
                "end": (datetime.now() + timedelta(days=5, hours=2)).isoformat(),
                "location": "Auditorio Principal",
                "description": "Ceremonia de bienvenida para nuevos estudiantes",
                "created_at": datetime.now().isoformat(),
                "updated_at": None
            },
            {
                "title": "Feria de Empleos",
                "start": (datetime.now() + timedelta(days=10)).isoformat(),
                "end": (datetime.now() + timedelta(days=10, hours=6)).isoformat(),
                "location": "Gimnasio Universitario",
                "description": "Feria anual de empleos con empresas locales",
                "created_at": datetime.now().isoformat(),
                "updated_at": None
            },
            {
                "title": "Examen Final Matemáticas",
                "start": (datetime.now() + timedelta(days=15)).isoformat(),
                "end": (datetime.now() + timedelta(days=15, hours=3)).isoformat(),
                "location": "Salón 301",
                "description": "Examen final del curso de Matemáticas Avanzadas",
                "created_at": datetime.now().isoformat(),
                "updated_at": None
            },
            {
                "title": "Conferencia de Tecnología",
                "start": (datetime.now() + timedelta(days=20)).isoformat(),
                "end": (datetime.now() + timedelta(days=20, hours=4)).isoformat(),
                "location": "Centro de Convenciones",
                "description": "Conferencia sobre las últimas tendencias en tecnología",
                "created_at": datetime.now().isoformat(),
                "updated_at": None
            }
        ]
        
        for event in events_data:
            # Verificar si el evento ya existe
            existing = collection.find_one({"title": event["title"]})
            if not existing:
                collection.insert_one(event)
                print(f"✅ Evento creado: {event['title']}")
            else:
                print(f"⏭️  Evento ya existe: {event['title']}")
    except Exception as e:
        print(f"❌ Error al poblar eventos: {e}")

def populate_lost_items():
    """Poblar objetos perdidos de ejemplo"""
    try:
        collection = mongo_service.get_collection("lost_items")
        if collection is None:
            print("❌ No se pudo obtener la colección de objetos perdidos")
            return

        lost_items_data = [
            {
                "title": "Laptop Dell Inspiron",
                "found_location": "Biblioteca Central",
                "status": "available",
                "description": "Laptop negra con stickers de programación",
                "contact_info": "Oficina de Objetos Perdidos",
                "created_at": datetime.now().isoformat(),
                "updated_at": None
            },
            {
                "title": "Mochila Azul",
                "found_location": "Cafetería",
                "status": "available",
                "description": "Mochila azul con libros de matemáticas",
                "contact_info": "Oficina de Objetos Perdidos",
                "created_at": datetime.now().isoformat(),
                "updated_at": None
            },
            {
                "title": "Teléfono Samsung",
                "found_location": "Laboratorio de Computación",
                "status": "claimed",
                "description": "Teléfono Samsung Galaxy con funda negra",
                "contact_info": "Oficina de Objetos Perdidos",
                "created_at": datetime.now().isoformat(),
                "updated_at": None
            },
            {
                "title": "Calculadora Científica",
                "found_location": "Salón 205",
                "status": "available",
                "description": "Calculadora Texas Instruments TI-84",
                "contact_info": "Oficina de Objetos Perdidos",
                "created_at": datetime.now().isoformat(),
                "updated_at": None
            },
            {
                "title": "Llaves con Llavero",
                "found_location": "Estacionamiento Norte",
                "status": "returned",
                "description": "Llaves con llavero de la universidad",
                "contact_info": "Oficina de Objetos Perdidos",
                "created_at": datetime.now().isoformat(),
                "updated_at": None
            }
        ]
        
        for item in lost_items_data:
            # Verificar si el objeto ya existe
            existing = collection.find_one({"title": item["title"]})
            if not existing:
                collection.insert_one(item)
                print(f"✅ Objeto perdido creado: {item['title']}")
            else:
                print(f"⏭️  Objeto ya existe: {item['title']}")
    except Exception as e:
        print(f"❌ Error al poblar objetos perdidos: {e}")

def main():
    """Función principal"""
    print("🚀 Iniciando población de base de datos...")
    
    try:
        # Conectar a MongoDB
        if not mongo_service.connect():
            print("❌ Error al conectar a MongoDB")
            return
        
        print("✅ Conexión a MongoDB establecida")
        
        # Poblar eventos
        print("\n📅 Poblando eventos...")
        populate_events()
        
        # Poblar objetos perdidos
        print("\n🔍 Poblando objetos perdidos...")
        populate_lost_items()
        
        print("\n✅ Población de base de datos completada")
        
    except Exception as e:
        print(f"❌ Error durante la población de datos: {e}")
    
    finally:
        # Cerrar conexión
        mongo_service.disconnect()

if __name__ == "__main__":
    main()
