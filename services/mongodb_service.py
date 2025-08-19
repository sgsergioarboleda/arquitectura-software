import logging
from typing import List, Dict, Any, Optional
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.database import Database
from pymongo.collection import Collection
from bson import ObjectId

class MongoDBService:
    """
    Servicio para interactuar con MongoDB
    Maneja conexiones y operaciones de lectura y escritura
    """
    def __init__(self, uri: str, database_name: str):
        """
        Inicializa el servicio de MongoDB
        
        Args:
            uri: URI de conexión a MongoDB
            database_name: Nombre de la base de datos
        """
        self.uri = uri
        self.database_name = database_name
        self.client: Optional[MongoClient] = None
        self.database: Optional[Database] = None
        self.logger = logging.getLogger(__name__)

    def connect(self) -> bool:
        """
        Establece conexión con MongoDB usando ServerApi
        """
        try:
            self.client = MongoClient(
                self.uri,
                server_api=ServerApi('1'),
                serverSelectionTimeoutMS=5000  # 5 segundos de timeout
            )
            # Prueba la conexión
            self.client.admin.command('ping')
            self.database = self.client[self.database_name]
            self.logger.info("✅ Conexión a MongoDB Atlas exitosa")
            return True
        except Exception as e:
            self.logger.error(f"❌ Error de conexión a MongoDB Atlas: {str(e)}")
            self.client = None
            self.database = None
            return False

    def disconnect(self):
        """Cierra la conexión con MongoDB"""
        if self.client:
            self.client.close()
            self.client = None
            self.database = None

    def get_collection(self, collection_name: str) -> Optional[Collection]:
        """
        Obtiene una colección específica
        """
        if self.database is None:
            return None
        return self.database[collection_name]

    def find_all(self, collection_name: str, filter_query: Dict = None, limit: int = 0, skip: int = 0) -> List[Dict[str, Any]]:
        """
        Busca todos los documentos en una colección con paginación
        """
        try:
            collection = self.get_collection(collection_name)
            if collection is None:
                return []
            query = filter_query if filter_query else {}
            cursor = collection.find(query)
            if skip > 0:
                cursor = cursor.skip(skip)
            if limit > 0:
                cursor = cursor.limit(limit)
            return list(cursor)
        except Exception as e:
            self.logger.error(f"Error en find_all: {e}")
            return []

    def find_one(self, collection_name: str, filter_query: Dict) -> Optional[Dict[str, Any]]:
        """
        Busca un documento específico en una colección
        """
        try:
            collection = self.get_collection(collection_name)
            if collection is None:
                return None
            return collection.find_one(filter_query)
        except Exception as e:
            self.logger.error(f"Error en find_one: {e}")
            return None

    def find_by_id(self, collection_name: str, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca un documento por su ID
        """
        try:
            collection = self.get_collection(collection_name)
            if collection is None:
                self.logger.error(f"❌ No se pudo obtener la colección '{collection_name}'")
                return None
            
            # Validar formato del ID
            if not ObjectId.is_valid(document_id):
                self.logger.error(f"❌ ID inválido: '{document_id}' no es un ObjectId válido")
                return None
            
            # Convertir a ObjectId y buscar
            object_id = ObjectId(document_id)
            result = collection.find_one({"_id": object_id})
            
            if result is None:
                self.logger.warning(f"⚠️ No se encontró documento con ID '{document_id}' en la colección '{collection_name}'")
            else:
                self.logger.info(f"✅ Documento encontrado con ID '{document_id}' en la colección '{collection_name}'")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error en find_by_id para ID '{document_id}': {e}")
            return None

    def is_valid_object_id(self, document_id: str) -> bool:
        """
        Valida si un string es un ObjectId válido de MongoDB
        
        Args:
            document_id: String a validar
            
        Returns:
            bool: True si es válido, False en caso contrario
        """
        try:
            return ObjectId.is_valid(document_id)
        except Exception as e:
            self.logger.error(f"Error validando ObjectId '{document_id}': {e}")
            return False

    def find_by_id_with_validation(self, collection_name: str, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca un documento por su ID con validación previa y logging detallado
        
        Args:
            collection_name: Nombre de la colección
            document_id: ID del documento a buscar
            
        Returns:
            Optional[Dict[str, Any]]: Documento encontrado o None
        """
        try:
            # Validar formato del ID primero
            if not self.is_valid_object_id(document_id):
                self.logger.error(f"❌ ID inválido: '{document_id}' no es un ObjectId válido")
                return None
            
            # Verificar conexión
            if not self.is_connected():
                self.logger.error("❌ No hay conexión activa a MongoDB")
                return None
            
            # Buscar documento
            result = self.find_by_id(collection_name, document_id)
            
            if result is None:
                self.logger.warning(f"⚠️ Documento no encontrado: ID '{document_id}' en colección '{collection_name}'")
            else:
                self.logger.info(f"✅ Documento encontrado: ID '{document_id}' en colección '{collection_name}'")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error en find_by_id_with_validation: {e}")
            return None

    def count_documents(self, collection_name: str, filter_query: Dict = None) -> int:
        """
        Cuenta documentos en una colección
        """
        try:
            collection = self.get_collection(collection_name)
            if collection is None:
                return 0
            query = filter_query if filter_query else {}
            return collection.count_documents(query)
        except Exception as e:
            self.logger.error(f"Error en count_documents: {e}")
            return 0

    def aggregate(self, collection_name: str, pipeline: List[Dict]) -> List[Dict[str, Any]]:
        """
        Ejecuta una agregación en la colección
        """
        try:
            collection = self.get_collection(collection_name)
            if collection is None:
                return []
            return list(collection.aggregate(pipeline))
        except Exception as e:
            self.logger.error(f"Error en aggregate: {e}")
            return []

    def is_connected(self) -> bool:
        """
        Verifica si la conexión está activa
        """
        try:
            # Verificar que tanto el cliente como la base de datos existan
            if self.client is None or self.database is None:
                return False
            
            # Verificar que la conexión esté activa haciendo un ping
            self.client.admin.command('ping')
            return True
        except Exception:
            return False