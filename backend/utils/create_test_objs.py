#!/usr/bin/env python3
"""
Script para crear objetos de prueba (eventos y objetos perdidos) en la base de datos
"""
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
import random

# Agregar el directorio padre al path para importar módulos
sys.path.append(str(Path(__file__).parent.parent))

from services.dependencies import mongo_service
from bson import ObjectId

def create_test_events():
    """Crear eventos de ejemplo variados para agosto y septiembre"""
    # Fechas base para agosto y septiembre
    august_base = datetime(2024, 8, 1)
    september_base = datetime(2024, 9, 1)
    
    events_data = [
        {
            "title": "Inauguración del Semestre",
            "start": (august_base + timedelta(days=5, hours=9)).isoformat(),
            "end": (august_base + timedelta(days=5, hours=12)).isoformat(),
            "location": "Auditorio Principal",
            "description": "Ceremonia de bienvenida para todos los estudiantes del nuevo semestre académico",
            "created_at": datetime.now().isoformat(),
            "updated_at": None
        },
        {
            "title": "Workshop de Programación Python",
            "start": (august_base + timedelta(days=8, hours=14)).isoformat(),
            "end": (august_base + timedelta(days=8, hours=18)).isoformat(),
            "location": "Laboratorio de Computación A",
            "description": "Taller práctico de programación en Python para principiantes",
            "created_at": datetime.now().isoformat(),
            "updated_at": None
        },
        {
            "title": "Feria de Ciencias",
            "start": (august_base + timedelta(days=15, hours=9)).isoformat(),
            "end": (august_base + timedelta(days=15, hours=17)).isoformat(),
            "location": "Gimnasio Universitario",
            "description": "Exposición de proyectos científicos de estudiantes de todas las facultades",
            "created_at": datetime.now().isoformat(),
            "updated_at": None
        },
        {
            "title": "Conferencia: Inteligencia Artificial",
            "start": (august_base + timedelta(days=22, hours=16)).isoformat(),
            "end": (august_base + timedelta(days=22, hours=18)).isoformat(),
            "location": "Sala de Conferencias",
            "description": "Charla sobre el futuro de la IA y su impacto en la sociedad",
            "created_at": datetime.now().isoformat(),
            "updated_at": None
        },
        {
            "title": "Torneo de Fútbol Interfacultades",
            "start": (august_base + timedelta(days=28, hours=10)).isoformat(),
            "end": (august_base + timedelta(days=28, hours=16)).isoformat(),
            "location": "Cancha de Fútbol",
            "description": "Torneo deportivo entre las diferentes facultades de la universidad",
            "created_at": datetime.now().isoformat(),
            "updated_at": None
        },
        {
            "title": "Exposición de Arte Estudiantil",
            "start": (september_base + timedelta(days=3, hours=10)).isoformat(),
            "end": (september_base + timedelta(days=6, hours=18)).isoformat(),
            "location": "Galería de Arte",
            "description": "Exposición de obras de arte creadas por estudiantes de la facultad de artes",
            "created_at": datetime.now().isoformat(),
            "updated_at": None
        },
        {
            "title": "Seminario de Emprendimiento",
            "start": (september_base + timedelta(days=10, hours=14)).isoformat(),
            "end": (september_base + timedelta(days=10, hours=19)).isoformat(),
            "location": "Centro de Emprendimiento",
            "description": "Seminario sobre cómo crear y desarrollar tu propia empresa",
            "created_at": datetime.now().isoformat(),
            "updated_at": None
        },
        {
            "title": "Noche de Talentos",
            "start": (september_base + timedelta(days=15, hours=19)).isoformat(),
            "end": (september_base + timedelta(days=15, hours=23)).isoformat(),
            "location": "Auditorio Principal",
            "description": "Evento cultural donde los estudiantes muestran sus talentos artísticos",
            "created_at": datetime.now().isoformat(),
            "updated_at": None
        }
    ]
    
    collection = mongo_service.get_collection("events")
    created_count = 0
    
    for event in events_data:
        # Verificar si el evento ya existe
        existing = collection.find_one({"title": event["title"]})
        if not existing:
            collection.insert_one(event)
            print(f"✅ Evento creado: {event['title']}")
            created_count += 1
        else:
            print(f"⏭️  Evento ya existe: {event['title']}")
    
    return created_count

def create_test_lost_items():
    """Crear objetos perdidos de ejemplo variados"""
    lost_items_data = [
        {
            "title": "Laptop MacBook Pro",
            "found_location": "Biblioteca Central - Piso 2",
            "status": "available",
            "description": "MacBook Pro plateada, modelo 2022, con funda negra y stickers de programación",
            "contact_info": "Oficina de Objetos Perdidos - Ext. 1234",
            "created_at": datetime.now().isoformat(),
            "updated_at": None
        },
        {
            "title": "Mochila Negra con Laptop",
            "found_location": "Cafetería Principal",
            "status": "claimed",
            "description": "Mochila negra Jansport con laptop Dell y libros de cálculo",
            "contact_info": "Oficina de Objetos Perdidos - Ext. 1234",
            "created_at": datetime.now().isoformat(),
            "updated_at": None
        },
        {
            "title": "iPhone 14 con Funda Transparente",
            "found_location": "Laboratorio de Física",
            "status": "available",
            "description": "iPhone 14 negro con funda transparente y protector de pantalla",
            "contact_info": "Oficina de Objetos Perdidos - Ext. 1234",
            "created_at": datetime.now().isoformat(),
            "updated_at": None
        },
        {
            "title": "Calculadora Científica Texas Instruments",
            "found_location": "Salón 301 - Matemáticas",
            "status": "available",
            "description": "Calculadora TI-84 Plus CE con funda azul",
            "contact_info": "Oficina de Objetos Perdidos - Ext. 1234",
            "created_at": datetime.now().isoformat(),
            "updated_at": None
        },
        {
            "title": "Llaves con Llavero de la Universidad",
            "found_location": "Estacionamiento Norte",
            "status": "returned",
            "description": "Llaves con llavero oficial de la universidad y tarjeta de acceso",
            "contact_info": "Oficina de Objetos Perdidos - Ext. 1234",
            "created_at": datetime.now().isoformat(),
            "updated_at": None
        },
        {
            "title": "Cartera Marrón de Cuero",
            "found_location": "Centro Estudiantil",
            "status": "available",
            "description": "Cartera marrón de cuero con documentos de identidad y tarjetas bancarias",
            "contact_info": "Oficina de Objetos Perdidos - Ext. 1234",
            "created_at": datetime.now().isoformat(),
            "updated_at": None
        },
        {
            "title": "Auriculares Sony WH-1000XM4",
            "found_location": "Auditorio Principal",
            "status": "available",
            "description": "Auriculares inalámbricos Sony negros con estuche de carga",
            "contact_info": "Oficina de Objetos Perdidos - Ext. 1234",
            "created_at": datetime.now().isoformat(),
            "updated_at": None
        },
        {
            "title": "Tablet iPad Air",
            "found_location": "Sala de Estudio - Biblioteca",
            "status": "claimed",
            "description": "iPad Air plateado con funda rosa y Apple Pencil",
            "contact_info": "Oficina de Objetos Perdidos - Ext. 1234",
            "created_at": datetime.now().isoformat(),
            "updated_at": None
        },
        {
            "title": "Reloj Apple Watch Series 7",
            "found_location": "Gimnasio Universitario",
            "status": "available",
            "description": "Apple Watch Series 7 con correa deportiva negra",
            "contact_info": "Oficina de Objetos Perdidos - Ext. 1234",
            "created_at": datetime.now().isoformat(),
            "updated_at": None
        },
        {
            "title": "Libro de Texto: Cálculo Diferencial",
            "found_location": "Salón 205 - Matemáticas",
            "status": "available",
            "description": "Libro 'Cálculo Diferencial e Integral' de Stewart, 8va edición",
            "contact_info": "Oficina de Objetos Perdidos - Ext. 1234",
            "created_at": datetime.now().isoformat(),
            "updated_at": None
        },
        {
            "title": "Bicicleta Azul con Canasta",
            "found_location": "Estacionamiento de Bicicletas",
            "status": "returned",
            "description": "Bicicleta azul con canasta frontal y candado",
            "contact_info": "Oficina de Objetos Perdidos - Ext. 1234",
            "created_at": datetime.now().isoformat(),
            "updated_at": None
        },
        {
            "title": "Cámara Canon EOS Rebel",
            "found_location": "Laboratorio de Fotografía",
            "status": "available",
            "description": "Cámara DSLR Canon con lente 18-55mm y estuche",
            "contact_info": "Oficina de Objetos Perdidos - Ext. 1234",
            "created_at": datetime.now().isoformat(),
            "updated_at": None
        }
    ]
    
    collection = mongo_service.get_collection("lost_items")
    created_count = 0
    
    for item in lost_items_data:
        # Verificar si el objeto ya existe
        existing = collection.find_one({"title": item["title"]})
        if not existing:
            collection.insert_one(item)
            print(f"✅ Objeto perdido creado: {item['title']}")
            created_count += 1
        else:
            print(f"⏭️  Objeto ya existe: {item['title']}")
    
    return created_count

def main():
    """Función principal"""
    print("🚀 Iniciando creación de objetos de prueba...")
    print("=" * 50)
    
    # Conectar a MongoDB
    if not mongo_service.connect():
        print("❌ Error al conectar a MongoDB")
        return
    
    print("✅ Conexión a MongoDB establecida")
    
    # Crear eventos de prueba
    print("\n📅 Creando eventos de prueba...")
    events_created = create_test_events()
    
    # Crear objetos perdidos de prueba
    print("\n🔍 Creando objetos perdidos de prueba...")
    items_created = create_test_lost_items()
    
    # Resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE CREACIÓN:")
    print(f"   • Eventos creados: {events_created}")
    print(f"   • Objetos perdidos creados: {items_created}")
    print(f"   • Total de objetos nuevos: {events_created + items_created}")
    print("=" * 50)
    
    # Cerrar conexión
    mongo_service.disconnect()
    print("✅ Script completado exitosamente")

if __name__ == "__main__":
    main()
